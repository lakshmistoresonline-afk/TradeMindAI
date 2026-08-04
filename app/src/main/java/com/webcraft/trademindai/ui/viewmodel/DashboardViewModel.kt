package com.webcraft.trademindai.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.webcraft.trademindai.data.remote.StockDto
import com.webcraft.trademindai.data.repository.StockRepositoryImpl
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val repository: StockRepositoryImpl
) : ViewModel() {

    private val _stocks = MutableStateFlow<List<StockDto>>(emptyList())
    val stocks: StateFlow<List<StockDto>> = _stocks

    init {
        loadStocks()
    }

    private fun loadStocks() {
        viewModelScope.launch {
            repository.getStocks().onSuccess {
                _stocks.value = it
            }
        }
    }
}
