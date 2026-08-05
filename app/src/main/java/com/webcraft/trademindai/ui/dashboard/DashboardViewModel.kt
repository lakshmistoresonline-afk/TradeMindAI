package com.webcraft.trademindai.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.webcraft.trademindai.data.remote.MarketStatsResponse
import com.webcraft.trademindai.domain.model.Stock
import com.webcraft.trademindai.domain.repository.IStockRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val repository: IStockRepository
) : ViewModel() {

    private val _stocks = MutableStateFlow<List<Stock>>(emptyList())
    val stocks: StateFlow<List<Stock>> = _stocks.asStateFlow()

    private val _marketStats = MutableStateFlow<Map<String, MarketStatsResponse>>(emptyMap())
    val marketStats: StateFlow<Map<String, MarketStatsResponse>> = _marketStats.asStateFlow()

    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading.asStateFlow()

    init {
        fetchData()
    }

    fun fetchData() {
        viewModelScope.launch {
            _loading.value = true
            val statsResult = repository.getMarketStats()
            val stocksResult = repository.getStocks()
            
            statsResult.onSuccess { _marketStats.value = it }
            stocksResult.onSuccess { _stocks.value = it }
            
            _loading.value = false
        }
    }

    fun triggerAnalysis() {
        viewModelScope.launch {
            repository.triggerAnalysis()
        }
    }
}
