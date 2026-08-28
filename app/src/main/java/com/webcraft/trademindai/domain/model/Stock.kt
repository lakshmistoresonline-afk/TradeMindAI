package com.webcraft.trademindai.domain.model

data class Stock(
    val symbol: String,
    val name: String?,
    val sector: String?,
    val industry: String? = null,
    val last_price: Double?,
    val change_pct: Double?,
    val market_cap: Double?,
    val pe_ratio: Double?,
    val pb_ratio: Double?,
    val analysis: AnalysisReport?,
    val structured_consensus: Map<String, Any>? = null,
    val ai_investment_score: Double? = null,
    val ai_investment_grade: String? = null,
    val updated_at: String?
)

data class AnalysisReport(
    val symbol: String,
    val recommendations: List<AgentRecommendation>,
    val consensus: String
)

data class AgentRecommendation(
    val agent: String,
    val analysis: String
)

data class MarketStat(
    val value: Double,
    val change: Double
)
