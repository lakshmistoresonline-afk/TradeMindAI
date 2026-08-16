package com.webcraft.trademindai.data.remote

import com.webcraft.trademindai.domain.model.Stock
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.POST

interface ApiService {
    @GET("stocks/")
    suspend fun getStocks(): List<Stock>

    @GET("stocks/{symbol}")
    suspend fun getStockDetail(@Path("symbol") symbol: String): Stock

    @GET("stocks/market-stats")
    suspend fun getMarketStats(): Map<String, MarketStatsResponse>

    @POST("analysis/trigger")
    suspend fun triggerAnalysis(): TriggerResponse

    @POST("analysis/backtest/{symbol}")
    suspend fun triggerBacktest(@Path("symbol") symbol: String): TriggerResponse

    @GET("ios/regime")
    suspend fun getMarketRegime(): MarketRegimeResponse

    @GET("ios/opportunities")
    suspend fun getOpportunities(): List<com.webcraft.trademindai.domain.model.MarketOpportunity>

    @GET("ios/signals/live")
    suspend fun getLiveSignals(): List<com.webcraft.trademindai.domain.model.LiveSignal>

    @GET("ios/twin/{symbol}")
    suspend fun getDigitalTwin(@Path("symbol") symbol: String): Map<String, Any>

    @GET("ios/journal")
    suspend fun getTradeJournal(): List<Map<String, Any>>

    @GET("analysis/performance/audit")
    suspend fun getPerformanceAudit(): List<Map<String, Any>>

    @POST("ai/chat")
    suspend fun aiChat(@retrofit2.http.Body query: String): ChatResponse
}

data class ChatResponse(val response: String)

data class MarketRegimeResponse(
    val regime: String,
    val risk_mode: String,
    val description: String,
    val volatility_index: Double
)

data class MarketStatsResponse(
    val value: Double? = null,
    val change: Double? = null,
    val advancing: Int? = null,
    val declining: Int? = null,
    val ratio: Double? = null
)

data class TriggerResponse(
    val message: String,
    val task_id: String
)
