package com.webcraft.trademindai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.webcraft.trademindai.domain.model.Stock
import com.webcraft.trademindai.ui.viewmodel.DashboardViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    navController: NavController,
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val stocks by viewModel.stocks.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("TradeMind AI") })
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { navController.navigate("chat") }) {
                Icon(Icons.Default.Chat, contentDescription = "Chat")
            }
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            item {
                MarketRegimeBanner()
            }
            items(stocks) { stock ->
                StockItem(stock = stock, onClick = {
                    navController.navigate("stock_detail/${stock.symbol}")
                })
            }
        }
    }
}

@Composable
fun MarketRegimeBanner() {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Market Regime: BULLISH",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            Text(
                text = "Institutional bias is positive. High liquidity environment.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.7f)
            )
        }
    }
}

@Composable
fun StockItem(stock: Stock, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
        onClick = onClick
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = stock.symbol, style = MaterialTheme.typography.headlineSmall)
            Text(text = stock.name ?: "", style = MaterialTheme.typography.bodyMedium)
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = "₹${stock.last_price ?: 0.0}")
                Text(
                    text = "${stock.change_pct ?: 0.0}%",
                    color = if ((stock.change_pct ?: 0.0) >= 0) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error
                )
            }
        }
    }
}
