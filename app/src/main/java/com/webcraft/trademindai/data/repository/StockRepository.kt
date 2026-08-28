package com.webcraft.trademindai.data.repository

import com.webcraft.trademindai.data.remote.ApiService
import com.webcraft.trademindai.data.remote.MarketRegimeResponse
import com.webcraft.trademindai.data.remote.MarketStatsResponse
import com.webcraft.trademindai.domain.model.Stock
import com.webcraft.trademindai.domain.repository.IStockRepository
import javax.inject.Inject

class StockRepository @Inject constructor(
    private val apiService: ApiService
) : IStockRepository {

    override suspend fun getStocks(): Result<List<Stock>> {
        return try {
            val response = apiService.getStocks()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getStockDetail(symbol: String): Result<Stock> {
        return try {
            val response = apiService.getStockDetail(symbol)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getMarketStats(): Result<Map<String, MarketStatsResponse>> {
        return try {
            val response = apiService.getMarketStats()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun triggerAnalysis(): Result<String> {
        return try {
            val response = apiService.triggerAnalysis()
            Result.success(response.message)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getMarketRegime(): Result<MarketRegimeResponse> {
        return try {
            val response = apiService.getMarketRegime()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getPerformanceAudit(): Result<List<Map<String, Any>>> {
        return try {
            val response = apiService.getPerformanceAudit()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getOpportunities(): Result<List<com.webcraft.trademindai.domain.model.MarketOpportunity>> {
        return try {
            val response = apiService.getOpportunities()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    override suspend fun getLiveSignals(): Result<List<com.webcraft.trademindai.domain.model.LiveSignal>> {
        return try {
            val response = apiService.getLiveSignals()
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
