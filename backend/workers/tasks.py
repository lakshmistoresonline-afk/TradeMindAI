# Fresh Build: 2026-08-10 16:50
from celery import Celery, group
from celery.schedules import crontab
from backend.core.config import settings
from backend.domain.models.ios import LiveSignal, MarketRegime, MarketIntelligenceReport, ResearchNote, SignalEvent
from backend.core.websocket import manager
import datetime
import json
import asyncio
import traceback
import gc
import os
import uuid

print(f"DEBUG: tasks.py v2.2.2 loaded from {os.path.abspath(__file__)}")

celery_app = Celery("backend.workers.tasks", broker=settings.REDIS_URL)

# Vision 2.2: Hardened Routing
celery_app.conf.task_default_queue = "shadow"
celery_app.conf.task_routes = {
    "backend.workers.tasks.*": {"queue": "shadow"}
}

# Automated Schedule (DISABLED ON RAILWAY - LOCAL ONLY)
if settings.ENVIRONMENT == "production":
    celery_app.conf.beat_schedule = {}
    print("[!] SCHEDULER: Automated schedules are DISABLED in production environment.")
else:
    celery_app.conf.beat_schedule = {
        "run-shadow-monitoring-cycle": {
            "task": "backend.workers.tasks.run_shadow_cycle_task",
            "schedule": crontab(minute="*/30", hour="9-16", day_of_week="mon-fri"), # 9 AM to 4 PM IST
            "options": {"queue": "shadow"}
        },
        "shadow-worker-heartbeat": {
            "task": "backend.workers.tasks.terminal_heartbeat", # Reuse existing for basic health
            "schedule": 60.0,
            "options": {"queue": "shadow"}
        }
    }

celery_app.conf.timezone = 'Asia/Kolkata'

if settings.ENVIRONMENT != "production":
    print(f"[*] SCHEDULER: Active schedules detected: {len(celery_app.conf.beat_schedule)}")
    for name, spec in celery_app.conf.beat_schedule.items():
        print(f"    - {name}: {spec.get('task')}")

@celery_app.task(queue="shadow")
def run_shadow_cycle_task():
    from production.shadow.shadow_service import ShadowService
    from production.shadow.shadow_heartbeat import ShadowHeartbeat

    ShadowHeartbeat.record_heartbeat("SCHEDULER_TRIGGER")

    loop = asyncio.get_event_loop()
    return loop.run_until_complete(ShadowService.run_shadow_cycle())

@celery_app.task
def sync_stock_data_task(symbol: str, period="1y"):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_sync_stock_data_logic(symbol, period))

@celery_app.task
def analyze_stock_ai_task(symbol: str):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_analyze_stock_ai_logic(symbol))

@celery_app.task
def process_market_intelligence():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_process_intel_logic())

@celery_app.task
def refresh_ai_rankings():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_refresh_rankings_logic())

async def _sync_stock_data_logic(symbol: str, period: str):
    import pandas as pd
    from backend.core.container import container
    from backend.analysis.technical import TechnicalAnalysis
    from backend.analysis.smc import SMCAnalysis
    from backend.analysis.wyckoff import WyckoffAnalysis
    from backend.services.quant_engine import QuantEngine

    try:
        service = container.stock_service
        feature_store = container.feature_store

        # 1. Sync Base Data (Price, News, Financials, Options)
        stock = await service.collect_stock_data(symbol, period)

        # 2. Get Context (250 bars)
        recent_prices = await service.repository.get_recent_prices(symbol, limit=250)
        if not recent_prices:
            return f"No price history found for {symbol}"

        df = pd.DataFrame([p.model_dump() for p in recent_prices])
        df.set_index('date', inplace=True)
        df.columns = [c.capitalize() for c in df.columns]

        # 3. Technical & SMC Analysis
        df_ta = TechnicalAnalysis.calculate_indicators(df)
        smc_obs = SMCAnalysis.detect_order_blocks(df)
        smc_fvgs = SMCAnalysis.detect_fvg(df)
        smc_structure = SMCAnalysis.detect_structure_change(df)
        wyckoff_phase = WyckoffAnalysis.detect_phase(df)

        last = df_ta.iloc[-1]
        c, e20, e50, e200 = last.get("Close", 0), last.get("EMA_20"), last.get("EMA_50"), last.get("EMA_200")
        wave = "Wave 1 (Accumulation)"
        if e200 and e20 and e50:
            if c > e200 and e20 > e50: wave = "Wave 3 (Impulse)"
            elif c < e200: wave = "Wave 4 (Correction)"
            elif c > e200 and e20 < e50: wave = "Wave 5 (Ending)"

        smc_data = {
            "order_blocks": smc_obs[-5:],
            "fvgs": smc_fvgs[-5:],
            "structure": smc_structure,
            "wyckoff": wyckoff_phase,
            "elliott": wave
        }

        # 4. Ingest Features
        ai_features = feature_store.extract_institutional_features(df_ta, smc_data)
        await feature_store.ingest_features(symbol, df.index[-1], ai_features)

        # 5. Quant Metrics
        try:
            nifty_df = await service.provider.fetch_history("NIFTY", period)
            if nifty_df.empty:
                nifty_df = await service.provider.fetch_history("^NSEI", period)

            if not nifty_df.empty:
                QuantEngine.calculate_metrics(symbol, df, nifty_df)
        except Exception as e:
            print(f"[!] Warning: Quant metrics skipped for {symbol} due to Nifty data error: {e}")

        # Explicitly set AI status to PENDING if it was never successful
        if stock.ai_status != "SUCCESS":
            stock.ai_status = "PENDING"

        await container.repository.save_stock(stock)
        return f"Data synced for {symbol}"

    except Exception as e:
        print(f"Error syncing data for {symbol}: {e}")
        return str(e)
    finally:
        gc.collect()

async def _analyze_stock_ai_logic(symbol: str):
    import yfinance as yf
    from backend.core.container import container
    from backend.ai.workflow import create_ai_workflow
    from backend.services.scoring_service import ScoringService

    try:
        repo = container.repository
        stock = await repo.get_stock_by_symbol(symbol)
        if not stock: return f"Stock {symbol} not found"

        # Check if already successful and fresh (less than 12h)
        if stock.ai_status == "SUCCESS" and stock.updated_at:
            if (datetime.datetime.utcnow() - stock.updated_at).total_seconds() < 43200:
                return f"AI analysis for {symbol} is already current."

        # Fetch required data from Feature Store and repository
        features = await container.data_platform_repo.get_features_by_range(symbol, datetime.datetime.utcnow() - datetime.timedelta(days=7), datetime.datetime.utcnow())
        if not features: return f"No features found for {symbol}"

        ai_features = features[-1].features
        ml_prediction = await container.ml_service.predict_with_champion(symbol, ai_features)

        # Enrich with live data
        live_ticker = yf.Ticker(f"{symbol}.NS")
        news_summary = [n.get("title") for n in live_ticker.news[:3]] if live_ticker.news else []
        options_proxy = stock.options_data or {}

        # AI Workflow
        workflow = create_ai_workflow()
        mtf_results = await container.timeframe_service.analyze_alignment(symbol)

        # Detect current regime
        from backend.core.container import container
        regime_obj = await container.ios_repo.get_latest_regime()
        regime_label = regime_obj.regime if regime_obj else "NEUTRAL"

        initial_state = {
            "symbol": symbol,
            "regime": regime_label,
            "technical_data": {
                "indicators": ai_features,
                "smc": stock.analysis.get("technical_data", {}).get("smc") if stock.analysis else {},
                "ml_prediction": ml_prediction,
                "mtf_alignment": mtf_results
            },
            "fundamental_data": {
                "pe_ratio": stock.pe_ratio,
                "pb_ratio": stock.pb_ratio,
                "market_cap": stock.market_cap,
                "financial_history": stock.financial_history
            },
            "news_sentiment": {"recent_headlines": news_summary},
            "options_data": options_proxy,
            "macro_data": {},
            "institutional_data": {"fii_holding": stock.fii_holding, "dii_holding": stock.dii_holding},
            "recommendations": [],
            "consensus": ""
        }

        result = workflow.invoke(initial_state)

        # Parse and update
        structured_consensus = {}
        if result.get("consensus"):
            try:
                import re
                content = result["consensus"]
                json_match = re.search(r'(\{.*\})', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).replace("'", "\"")
                    structured_consensus = json.loads(json_str)
            except: pass

        scoring_results = ScoringService.calculate_unified_score(ai_features, ml_prediction, result)

        # Vision 2.2: Live Signal Snapshot
        rating_upper = (structured_consensus.get("rating") or result.get("consensus", "")).upper()
        if "BUY" in rating_upper or "SELL" in rating_upper:
            sig_id = f"sig_{symbol}_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M')}"
            direction = "LONG" if "BUY" in rating_upper else "SHORT"

            # Initial Events
            gen_event = SignalEvent(type="GENERATED", message=f"Signal identified via {direction} multi-agent consensus.")
            val_event = SignalEvent(type="VALIDATED", message=f"Consensus reached with {scoring_results.get('score', 50)}% conviction.")

            live_sig = LiveSignal(
                id=sig_id,
                symbol=symbol,
                timestamp=datetime.datetime.utcnow(),
                rating=str(structured_consensus.get("rating", "BUY" if direction == "LONG" else "SELL")),
                direction=direction,
                conviction=float(scoring_results.get("score", 50)),
                entry_price=stock.last_price or 0.0,
                target_price=structured_consensus.get("target"),
                stop_loss_price=structured_consensus.get("stop_loss"),
                timeframe=str(structured_consensus.get("timeframe", "SWING")),
                status="WAITING_FOR_ENTRY",
                validated_at=datetime.datetime.utcnow(),
                model_version="TradeMind Core v2.2",
                events=[gen_event, val_event]
            )
            await container.ios_repo.save_live_signal(live_sig)

        stock.analysis = result
        stock.structured_consensus = structured_consensus
        stock.ai_investment_score = scoring_results["score"]
        stock.ai_investment_grade = scoring_results["grade"]
        stock.health_metrics = scoring_results["health"]
        stock.ai_status = "SUCCESS"
        stock.ai_last_error = None
        stock.updated_at = datetime.datetime.utcnow()

        await repo.save_stock(stock)

        # Broadcast real-time completion to active terminal sessions
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(manager.broadcast({
                "type": "AI_COMPLETED",
                "symbol": symbol,
                "rating": stock.decision.rating if hasattr(stock, 'decision') else structured_consensus.get('rating'),
                "message": f"AI Intelligence for {symbol} has been reconciled."
            }))
        except: pass

        # Auto-generate Research Note for high-conviction
        if scoring_results["score"] > 80:
            note = ResearchNote(
                id=str(uuid.uuid4()),
                user_id="SYSTEM_AI",
                symbol=symbol,
                content=f"AI High-Conviction Alert: {structured_consensus.get('thesis', 'Bullish alignment detected.')}",
                tags=["AI_GENERATED", "HIGH_CONVICTION"]
            )
            await container.ios_repo.save_research_note(note)

        return f"AI Analysis successful for {symbol}"

    except Exception as e:
        err_msg = str(e)
        print(f"AI Error for {symbol}: {err_msg}")
        # Save failure state
        stock = await container.repository.get_stock_by_symbol(symbol)
        if stock:
            stock.ai_status = "FAILED"
            stock.ai_last_error = err_msg
            await container.repository.save_stock(stock)
        return err_msg

async def _process_intel_logic():
    from backend.core.container import container
    from backend.domain.models.ios import MarketRegime, MarketIntelligenceReport
    import yfinance as yf

    print("[*] Processing Market Intelligence...")
    try:
        service = container.stock_service
        ios_repo = container.ios_repo
        provider = container.provider

        # 1. Detect Regime - Resilient Index Fetching
        nifty_price = 0.0
        vix = 15.0

        try:
            # Try Provider first (Groww usually more stable for NSE)
            nifty_price = await provider.get_ltp("NIFTY")
            if nifty_price <= 0:
                nifty_ticker = yf.Ticker("^NSEI")
                nifty_price = nifty_ticker.fast_info.last_price
        except Exception as e:
            print(f"[!] Warning: Failed to fetch Nifty price: {e}")
            # Absolute fallback to keep system alive
            nifty_price = 24500.0

        try:
            vix_ticker = yf.Ticker("^INDIAVIX")
            vix = vix_ticker.fast_info.last_price
        except Exception as e:
            print(f"[!] Warning: Failed to fetch VIX: {e}")
            vix = 15.0

        regime_label = "BULLISH" if nifty_price > 24000 else "SIDEWAYS" # Dynamic logic simplified
        if vix > 18: regime_label = "VOLATILE"

        regime = MarketRegime(
            date=datetime.datetime.utcnow(),
            regime=regime_label,
            risk_mode="RISK_ON" if regime_label == "BULLISH" else "NEUTRAL",
            sentiment_score=0.65 if regime_label == "BULLISH" else 0.5,
            volatility_index=vix,
            description=f"Market is currently in a {regime_label} phase. Institutional bias remains stable."
        )
        await ios_repo.save_market_regime(regime)

        # 2. Generate Intel Report
        stocks = await service.repository.get_all_stocks(limit=100)
        report = MarketIntelligenceReport(
            id=f"report_{datetime.datetime.utcnow().strftime('%Y%m%d%H')}",
            type="PERIODIC",
            date=datetime.datetime.utcnow(),
            summary=f"Market Intelligence Update: {regime_label} conditions observed. Nifty 100 breadth tracking session dynamics.",
            key_events=["Institutional Accumulation", "Sector Rotation"],
            top_movers=[],
            sector_performance={},
            ai_bias="POSITIVE" if regime_label == "BULLISH" else "NEUTRAL"
        )
        await ios_repo.save_intel_report(report)

        print("[+] Market Intelligence Processed.")
    except Exception as e:
        print(f"[!] Intel Logic Error: {e}")

async def _refresh_rankings_logic():
    from backend.core.container import container
    repo = container.repository
    stocks = await repo.get_all_stocks(limit=100)
    # This keeps the Opportunity Scanner fresh
    opps = container.opportunity_engine.find_opportunities(stocks)
    for opp in opps:
        await container.ios_repo.save_opportunity(opp)
    print(f"[+] AI Rankings & Opportunities Refreshed: {len(opps)} found.")

@celery_app.task
def analyze_nifty_100(period="1y"):
    from scripts.audit_database import ALL_SUPPORTED
    job = group(sync_stock_data_task.s(symbol, period=period) for symbol in ALL_SUPPORTED)
    job.apply_async()
    return f"Triggered data sync for full Alpha Universe ({len(ALL_SUPPORTED)} stocks)."

@celery_app.task(queue="shadow")
def terminal_heartbeat():
    """
    Vision 2.2: Ultra-Resilient Live Terminal Heartbeat.
    Ensures terminal context is maintained even if primary data providers are throttled.
    """
    import yfinance as yf
    from backend.core.container import container
    from production.shadow.shadow_heartbeat import ShadowHeartbeat

    # Record worker presence in DB for dashboard
    ShadowHeartbeat.record_heartbeat("WORKER_PRESENCE")

    try:
        nifty = 0.0
        try:
            # 1. Try Groww Primary
            loop = asyncio.get_event_loop()
            nifty = loop.run_until_complete(container.provider.get_ltp("NIFTY"))
        except: pass

        if nifty <= 0:
            try:
                # 2. Try yfinance Secondary
                n_ticker = yf.Ticker("^NSEI")
                nifty = n_ticker.fast_info.last_price
            except: pass

        if nifty <= 0 or nifty is None:
            # 3. Last Stand Fallback: Use last known regime price or baseline
            try:
                loop = asyncio.get_event_loop()
                regime = loop.run_until_complete(container.ios_repo.get_latest_regime())
                nifty = (regime.volatility_index * 1000) if regime else 24500.0 # Heuristic
            except:
                nifty = 24500.0

        print(f"[Heartbeat] Nifty Sync: {nifty}")
    except Exception as e:
        print(f"[Heartbeat] Fatal logic error: {e}")

@celery_app.task
def audit_signals_task():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_audit_signals_logic())

@celery_app.task
def ingest_historical_data_task(symbol: str, start_date_str: str, end_date_str: str, interval: str):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_ingest_historical_logic(symbol, start_date_str, end_date_str, interval))

@celery_app.task
def sync_instruments_task():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_sync_instruments_logic())

async def _ingest_historical_logic(symbol: str, start_date_str: str, end_date_str: str, interval: str):
    from backend.core.container import container
    from backend.services.ingestion_service import IngestionService
    from datetime import datetime

    start_date = datetime.fromisoformat(start_date_str)
    end_date = datetime.fromisoformat(end_date_str)

    ingestor = IngestionService(container.repository, container.provider)
    result = await ingestor.ingest_historical_data(symbol, start_date, end_date, interval)
    return f"Ingestion for {symbol}: {result['status']} ({result.get('count', 0)} candles)"

async def _sync_instruments_logic():
    from backend.core.container import container
    from backend.core.postgres import InstrumentDB
    provider = container.provider
    session_factory = container.repository.session_factory

    print("[*] Syncing instruments from provider...")
    instruments = await provider.get_instruments()

    if not instruments:
        print("[!] No instruments returned from provider.")
        return "No instruments to sync."

    with session_factory() as session:
        for inst in instruments:
            # Map provider fields to TradeMind InstrumentDB
            inst_id = inst.get("id") or inst.get("groww_symbol")
            if not inst_id: continue

            db_inst = session.query(InstrumentDB).filter(InstrumentDB.id == inst_id).first()
            if not db_inst:
                db_inst = InstrumentDB(id=inst_id)
                session.add(db_inst)

            db_inst.exchange = inst.get("exchange", "NSE")
            db_inst.trading_symbol = inst.get("trading_symbol") or inst.get("symbol")
            db_inst.segment = inst.get("segment", "CASH")
            db_inst.instrument_type = inst.get("instrument_type", "EQUITY")
            db_inst.groww_symbol = inst.get("groww_symbol") or inst_id

            expiry = inst.get("expiry")
            if expiry and isinstance(expiry, (int, float)):
                db_inst.expiry = datetime.datetime.fromtimestamp(expiry / 1000.0)
            elif isinstance(expiry, str):
                try: db_inst.expiry = datetime.datetime.fromisoformat(expiry)
                except: pass

            db_inst.strike = float(inst.get("strike", 0))
            db_inst.option_type = inst.get("option_type")
            db_inst.source = settings.MARKET_DATA_PROVIDER
            db_inst.last_updated = datetime.datetime.utcnow()

        session.commit()

    return f"Synced {len(instruments)} instruments."

@celery_app.task
def audit_signals_task():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_audit_signals_logic())

async def _audit_signals_logic():
    from backend.core.container import container
    from backend.services.signal_auditor import SignalAuditor
    auditor = SignalAuditor(container.ios_repo)
    await auditor.audit_active_signals()
    return "Signal Audit Complete."
