package com.webcraft.trademindai.data.remote

import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.POST
import retrofit2.http.Query

interface ApiService {
    @GET("stocks")
    suspend fun getStocks(): List<StockDto>

    @GET("stocks/{symbol}")
    suspend fun getStockDetail(@Path("symbol") symbol: String): StockDetailDto

    @POST("ai/chat")
    suspend fun aiChat(@Query("query") query: String): ChatResponseDto
}

data class StockDto(
    val symbol: String,
    val name: String,
    val price: Double,
    val change: Double
)

data class StockDetailDto(
    val symbol: String,
    val name: String,
    val sector: String,
    val technicals: Map<String, Double>,
    val consensus: String
)

data class ChatResponseDto(
    val response: String
)
