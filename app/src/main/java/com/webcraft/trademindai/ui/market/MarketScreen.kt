package com.webcraft.trademindai.ui.market

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.webcraft.trademindai.ui.dashboard.DashboardViewModel

import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MarketScreen(
    viewModel: DashboardViewModel = hiltViewModel(),
    onStockClick: (String) -> Unit
) {
    val stocks by viewModel.stocks.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Market Pulse", fontWeight = FontWeight.Bold) })
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier.padding(padding).fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(stocks) { stock ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    onClick = { onStockClick(stock.symbol) }
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp).fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(stock.symbol, fontWeight = FontWeight.Bold)
                            Text(stock.sector ?: "", style = MaterialTheme.typography.bodySmall)
                        }
                        Text("₹${String.format(Locale.US, "%.2f", stock.last_price ?: 0.0)}", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}
