package com.webcraft.trademindai.domain.model

data class MarketOpportunity(
    val id: String,
    val symbol: String,
    val type: String, // BREAKOUT, REVERSAL, MOMENTUM, UNDERVALUED
    val conviction_score: Double,
    val ai_thesis: String,
    val indicators: List<String>,
    val timestamp: String
)
