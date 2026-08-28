package com.webcraft.trademindai.ui.dashboard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.webcraft.trademindai.data.remote.MarketRegimeResponse
import com.webcraft.trademindai.data.remote.MarketStatsResponse
import com.webcraft.trademindai.domain.model.LiveSignal
import com.webcraft.trademindai.domain.model.MarketOpportunity
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

    private val _liveSignals = MutableStateFlow<List<LiveSignal>>(emptyList())
    val liveSignals: StateFlow<List<LiveSignal>> = _liveSignals.asStateFlow()

    private val _selectedTimeframe = MutableStateFlow("ALL")
    val selectedTimeframe: StateFlow<String> = _selectedTimeframe.asStateFlow()

    private val _marketStats = MutableStateFlow<Map<String, MarketStatsResponse>>(emptyMap())
    val marketStats: StateFlow<Map<String, MarketStatsResponse>> = _marketStats.asStateFlow()

    private val _regime = MutableStateFlow<MarketRegimeResponse?>(null)
    val regime: StateFlow<MarketRegimeResponse?> = _regime.asStateFlow()

    private val _performanceAudit = MutableStateFlow<List<Map<String, Any>>>(emptyList())
    val performanceAudit: StateFlow<List<Map<String, Any>>> = _performanceAudit.asStateFlow()

    private val _opportunities = MutableStateFlow<List<MarketOpportunity>>(emptyList())
    val opportunities: StateFlow<List<MarketOpportunity>> = _opportunities.asStateFlow()

    private val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading.asStateFlow()

    init {
        fetchData()
    }

    fun setTimeframe(timeframe: String) {
        _selectedTimeframe.value = timeframe
    }

    fun fetchData() {
        viewModelScope.launch {
            _loading.value = true
            val statsResult = repository.getMarketStats()
            val stocksResult = repository.getStocks()
            val regimeResult = repository.getMarketRegime()
            val auditResult = repository.getPerformanceAudit()
            val opportunitiesResult = repository.getOpportunities()
            val liveSignalsResult = repository.getLiveSignals()
            
            statsResult.onSuccess { _marketStats.value = it }
            stocksResult.onSuccess { _stocks.value = it }
            regimeResult.onSuccess { _regime.value = it }
            auditResult.onSuccess { _performanceAudit.value = it }
            opportunitiesResult.onSuccess { _opportunities.value = it }
            liveSignalsResult.onSuccess { _liveSignals.value = it }
            
            _loading.value = false
        }
    }

    fun triggerAnalysis() {
        viewModelScope.launch {
            repository.triggerAnalysis().onSuccess {
                fetchData()
            }
        }
    }
}
