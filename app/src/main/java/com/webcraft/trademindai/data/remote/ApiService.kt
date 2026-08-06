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

    @GET("ios/twin/{symbol}")
    suspend fun getDigitalTwin(@Path("symbol") symbol: String): Map<String, Any>

    @GET("ios/journal")
    suspend fun getTradeJournal(): List<Map<String, Any>>
}

data class MarketRegimeResponse(
    val regime: String,
    val risk_mode: String,
    val description: String,
    val volatility_index: Double
)

data class MarketStatsResponse(
    val value: Double,
    val change: Double
)

data class TriggerResponse(
    val message: String,
    val task_id: String
)
