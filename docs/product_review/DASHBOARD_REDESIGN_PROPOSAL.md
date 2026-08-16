# DASHBOARD REDESIGN PROPOSAL: THE "COMMAND CENTER"

## 🎯 OBJECTIVE: DECISION-SPEED
The main Dashboard should act as a "Commander's Intent" view. A trader opening the app at 9:15 AM should know the market posture in **under 3 seconds**.

---

## 🏗️ PROPOSED HIERARCHY

### ROW 1: THE MARKET PULSE (High-Contrast Stacks)
*Combine indices and breadth into a single cohesive "State of the Market" card.*
- **LEFT**: Nifty 50 / Bank Nifty / India VIX (Compact).
- **CENTER**: A/D Ratio + Signal Gauge (Bullish/Bearish needle).
- **RIGHT**: FII/DII Net Flow Heuristic (Institutional Momentum).

### ROW 2: AI ALPHA RADAR (Primary Focus)
*Move "Live AI Signals" to a 2-column layout.*
- **COL 1**: "Institutional Breakouts" (Top 5 symbols with recent SMC OB + AI Buy).
- **COL 2**: "Risk Alerts" (Sudden Volatility or AI Rating downgrades).

### ROW 3: INTELLIGENCE SYNTHESIS
- **Market Brief**: The Llama 3.1 8B session summary.
- **Economic Calendar**: Next 3 "High Impact" events only.

---

## 📉 WIDGET CONSOLIDATION PLAN

| Legacy Widget | Action | Proposed Merge |
| :--- | :--- | :--- |
| **StatCard (Nifty 100)**| Merge | Into "Market Pulse" Header. |
| **Market Breadth (Line)**| Promote | To be the background trend for the Breadth Card. |
| **Opportunity Engine** | Rename | "Institutional Alpha Finder." |
| **StatCard (AI Sentiment)**| Promote | To a "Meta-Signal" Gauge. |

---

## ✨ PROPOSED VISUAL IMPROVEMENTS
1.  **Glow Borders**: Use a subtle Emerald/Rose border-glow for the primary "Signal" widgets to draw immediate attention.
2.  **Compact Density**: Reduce `TableCell` padding and use **JetBrains Mono** for all price data.
3.  **Sparklines**: Add tiny price sparklines (24H) next to every symbol in the "Live AI Signals" feed.
