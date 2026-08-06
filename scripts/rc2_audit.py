import httpx
import json

def run_audit():
    base_url = "https://trademind-api-m8jg.onrender.com/api/v1"

    print("\n" + "="*50)
    print("TRADE MIND AI: RC-2 PRODUCTION DATA AUDIT")
    print("="*50 + "\n")

    # 1. Audit RELIANCE (Detailed Analysis)
    print("--- STEP 1: AUDITING [RELIANCE] DNA ---")
    try:
        r = httpx.get(f"{base_url}/stocks/RELIANCE", timeout=30.0)
        if r.status_code == 200:
            data = r.json()
            # Core Info
            core = {k: v for k, v in data.items() if k != "analysis"}
            print(f"✅ Core Info Found: {list(core.keys())}")

            # Analysis
            analysis = data.get("analysis")
            if analysis:
                print(f"✅ Analysis Keys: {list(analysis.keys())}")
                tech = analysis.get("technical_data", {})
                print(f"✅ Technical Data Keys: {list(tech.keys())}")

                # Check for nested signal structure
                recs = analysis.get("recommendations", [])
                print(f"✅ AI Recommendations: {len(recs)} agents participated")
            else:
                print("❌ Analysis Data: MISSING (Worker may still be processing)")
        else:
            print(f"❌ RELIANCE Fetch Failed: Status {r.status_code}")
    except Exception as e:
        print(f"❌ Error during RELIANCE audit: {e}")

    # 2. Audit Market Intelligence
    print("\n--- STEP 2: AUDITING MARKET INTELLIGENCE ---")
    try:
        r = httpx.get(f"{base_url}/ios/intel?type=CLOSING", timeout=30.0)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Intel Report: {data.get('summary')[:100]}...")
            print(f"✅ Events: {data.get('key_events')}")
        else:
            print(f"❌ Intel Fetch Failed: Status {r.status_code}")
    except Exception as e:
        print(f"❌ Error during Intel audit: {e}")

    # 3. Audit Market Regime
    print("\n--- STEP 3: AUDITING MARKET REGIME ---")
    try:
        r = httpx.get(f"{base_url}/ios/regime", timeout=30.0)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Regime: {data.get('regime')}")
            print(f"✅ Risk Mode: {data.get('risk_mode')}")
        else:
            print(f"❌ Regime Fetch Failed: Status {r.status_code}")
    except Exception as e:
        print(f"❌ Error during Regime audit: {e}")

    print("\n" + "="*50)
    print("AUDIT COMPLETE")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_audit()
