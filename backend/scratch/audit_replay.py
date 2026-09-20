import sys
import os
import asyncio

# Add project root to path
sys.path.append(os.getcwd())

from backend.services.signal_replay_engine import SignalReplayEngine

async def test_replay():
    print("CLAIM: Deterministic Replay (V2.3 Shadow Gate)")
    print("-" * 60)

    # 1. Run Replay
    res1 = await SignalReplayEngine.replay_shadow_gate(limit=10)
    print(f"Run 1: Total {res1['total_processed']}, Blocked {res1['blocked']}, Efficiency {res1['net_gate_efficiency']}")

    # 2. Run Replay Again
    res2 = await SignalReplayEngine.replay_shadow_gate(limit=10)
    print(f"Run 2: Total {res2['total_processed']}, Blocked {res2['blocked']}, Efficiency {res2['net_gate_efficiency']}")

    if res1['total_processed'] == res2['total_processed'] and res1['blocked'] == res2['blocked']:
        print("\nRESULT: PASS (Deterministic)")
    else:
        print("\nRESULT: FAIL (Non-deterministic)")

if __name__ == "__main__":
    asyncio.run(test_replay())
