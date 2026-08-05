package com.webcraft.trademindai.domain.model

data class Stock(
    val symbol: String,
    val name: String?,
    val sector: String?,
    val last_price: Double?,
    val change_pct: Double?,
    val market_cap: Double?,
    val pe_ratio: Double?,
    val pb_ratio: Double?,
    val analysis: AnalysisReport?,
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
