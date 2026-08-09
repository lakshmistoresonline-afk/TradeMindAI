package com.webcraft.trademindai.domain.repository

import com.webcraft.trademindai.domain.model.Stock
import com.webcraft.trademindai.data.remote.MarketRegimeResponse
import com.webcraft.trademindai.data.remote.MarketStatsResponse

interface IStockRepository {
    suspend fun getStocks(): Result<List<Stock>>
    suspend fun getStockDetail(symbol: String): Result<Stock>
    suspend fun getMarketStats(): Result<Map<String, MarketStatsResponse>>
    suspend fun triggerAnalysis(): Result<String>
    suspend fun getMarketRegime(): Result<MarketRegimeResponse>
    suspend fun getPerformanceAudit(): Result<List<Map<String, Any>>>
    suspend fun getOpportunities(): Result<List<com.webcraft.trademindai.domain.model.MarketOpportunity>>
}
