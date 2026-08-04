package com.webcraft.trademindai.data.repository

import com.webcraft.trademindai.data.remote.ApiService
import com.webcraft.trademindai.data.remote.StockDto
import javax.inject.Inject

class StockRepositoryImpl @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun getStocks(): Result<List<StockDto>> {
        return try {
            Result.success(apiService.getStocks())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
