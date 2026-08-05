package com.webcraft.trademindai.domain.repository

import com.webcraft.trademindai.domain.model.Stock
import com.webcraft.trademindai.data.remote.MarketStatsResponse

interface IStockRepository {
    suspend fun getStocks(): Result<List<Stock>>
    suspend fun getStockDetail(symbol: String): Result<Stock>
    suspend fun getMarketStats(): Result<Map<String, MarketStatsResponse>>
    suspend fun triggerAnalysis(): Result<String>
}
