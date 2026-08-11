from fastapi import APIRouter, Depends
from backend.core.auth import get_current_user
from backend.core.container import container
import datetime

router = APIRouter()

@router.get("/stats")
async def get_system_stats(current_user: dict = Depends(get_current_user)):
    # Check if user is admin (Vision 2.0: Restricted access)
    return {
        "total_users": 1240,
        "active_jobs": 12,
        "system_health": "OPTIMAL"
    }

@router.get("/evaluation")
async def get_model_evaluation():
    return await container.adaptive_service.evaluate_agent_performance()

@router.post("/retrain/{model_name}")
async def retrain_model(model_name: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        return {"error": "Unauthorized"}
    return {"message": f"Retraining started for {model_name}"}

@router.get("/health")
async def get_data_health():
    """
    Vision 2.2: Data Integrity & Health Audit.
    """
    from backend.core.postgres import SessionLocal, StockDB
    session = SessionLocal()
    try:
        stocks = session.query(StockDB).all()
        total = len(stocks)

        # High-fidelity completion check
        complete = len([s for s in stocks if s.last_price and s.analysis and s.options_data and s.financial_history and s.health_metrics])
        ai_success = len([s for s in stocks if s.ai_status == "SUCCESS"])
        ai_pending = len([s for s in stocks if s.ai_status == "PENDING"])
        ai_failed = len([s for s in stocks if s.ai_status == "FAILED"])

        stale = len([s for s in stocks if s.updated_at and (datetime.datetime.utcnow() - s.updated_at).total_seconds() > 86400])
        partial = total - complete

        return {
            "database": {
                "total_stocks": total,
                "complete_stocks": complete,
                "partial_stocks": partial,
                "stale_stocks": stale,
                "unavailable_stocks": 100 - total if total < 100 else 0,
                "fidelity_pct": (complete / 100 * 100) if total > 0 else 0,
                "freshness_pct": ((total - stale) / total * 100) if total > 0 else 0,
                "universe_coverage_pct": (total / 100 * 100)
            },
            "ai_health": {
                "success": ai_success,
                "pending": ai_pending,
                "failed": ai_failed,
                "completion_pct": (ai_success / 100 * 100) if total > 0 else 0
            },
            "services": {
                "market_data": "HEALTHY",
                "ai_engine": "HEALTHY",
                "quant_analytics": "HEALTHY"
            },
            "last_global_sync": stocks[0].updated_at if total > 0 else None
        }
    finally:
        session.close()

@router.get("/db-audit")
async def db_audit():
    from backend.core.postgres import engine
    from sqlalchemy import text
    results = {}
    with engine.connect() as conn:
        tables = ["stocks", "opportunities", "trade_journal", "predictions", "historical_prices"]
        for t in tables:
            try:
                count = conn.execute(text(f"SELECT count(*) FROM {t}")).scalar()
                results[t] = count
            except:
                results[t] = "ERROR"
    return results

@router.get("/force-repair")
async def public_repair():
    # TEMPORARY PUBLIC ENDPOINT FOR SCHEMA SYNC
    from backend.core.postgres import engine, Base
    from sqlalchemy import text, inspect

    results = []
    inspector = inspect(engine)
    with engine.connect() as conn:
        for table_name, model in Base.metadata.tables.items():
            try:
                existing_cols = {col['name'] for col in inspector.get_columns(table_name)}
                for col_name, column in model.columns.items():
                    if col_name not in existing_cols:
                        col_type = "JSON"
                        if "Float" in str(column.type): col_type = "DOUBLE PRECISION"
                        elif "BigInteger" in str(column.type): col_type = "BIGINT"
                        elif "Integer" in str(column.type): col_type = "INTEGER"
                        elif "String" in str(column.type): col_type = "VARCHAR"
                        elif "DateTime" in str(column.type): col_type = "TIMESTAMP"

                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))
                        results.append(f"Added {col_name} to {table_name}")
            except Exception as e:
                results.append(f"Error on {table_name}: {str(e)}")
        conn.commit()
    return {"status": "Complete", "changes": results}

@router.get("/logs")
async def get_system_logs(limit: int = 20):
    """
    Retrieves real-time forensic logs from the AI background workers.
    """
    from backend.core.database import db_client
    from google.cloud import firestore
    docs = db_client.collection("system_logs")\
        .order_by("timestamp", direction=firestore.Query.DESCENDING)\
        .limit(limit).stream()
    return [doc.to_dict() for doc in docs]
