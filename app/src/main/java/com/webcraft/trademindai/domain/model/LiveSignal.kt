package com.webcraft.trademindai.domain.model

data class LiveSignal(
    val id: String,
    val symbol: String,
    val timestamp: String?,
    val rating: String,
    val direction: String, // LONG or SHORT
    val conviction: Double,
    val entry_price: Double,
    val target_price: Double?,
    val stop_loss_price: Double?,
    val timeframe: String,
    val status: String, // WAITING_FOR_ENTRY, ENTRY_TRIGGERED, ACTIVE, TARGET_HIT, STOP_LOSS, EXPIRED, CANCELLED
    val validated_at: String?,
    val triggered_at: String?,
    val trigger_price: Double?,
    val trigger_condition: String?,
    val outcome_date: String?,
    val profit_pct: Double?,
    val mfe: Double = 0.0,
    val mae: Double = 0.0,
    val model_version: String = "TradeMind Core v2.2",
    val events: List<SignalEvent> = emptyList()
)

data class SignalEvent(
    val id: String,
    val type: String,
    val timestamp: String?,
    val price: Double?,
    val message: String?,
    val metadata: Map<String, Any> = emptyMap()
)
