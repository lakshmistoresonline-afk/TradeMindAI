package com.webcraft.trademindai.ui.dashboard

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.TrendingDown
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.webcraft.trademindai.domain.model.Stock

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val stocks by viewModel.stocks.collectAsState()
    val marketStats by viewModel.marketStats.collectAsState()
    val loading by viewModel.loading.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("TradeMind AI", fontWeight = FontWeight.Bold) },
                actions = {
                    IconButton(onClick = { viewModel.triggerAnalysis() }) {
                        Icon(Icons.Default.PlayArrow, contentDescription = "Trigger Analysis")
                    }
                }
            )
        }
    ) { padding ->
        if (loading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .padding(padding)
                    .fillMaxSize()
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    Text("Market Stats", style = MaterialTheme.typography.titleLarge)
                }

                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        marketStats.forEach { (name, stats) ->
                            MarketStatCard(
                                name = name,
                                value = stats.value.toString(),
                                change = "${stats.change}%",
                                isPositive = stats.change >= 0,
                                modifier = Modifier.weight(1f)
                            )
                        }
                    }
                }

                item {
                    Text("AI Signals", style = MaterialTheme.typography.titleLarge)
                }

                items(stocks.filter { it.analysis != null }) { stock ->
                    StockSignalCard(stock)
                }
            }
        }
    }
}

@Composable
fun MarketStatCard(
    name: String,
    value: String,
    change: String,
    isPositive: Boolean,
    modifier: Modifier = Modifier
) {
    Card(modifier = modifier) {
        Column(modifier = Modifier.padding(12.dp)) {
            Text(name, style = MaterialTheme.typography.labelMedium, color = Color.Gray)
            Text(value, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Text(
                text = change,
                style = MaterialTheme.typography.bodySmall,
                color = if (isPositive) Color(0xFF10b981) else Color.Red
            )
        }
    }
}

@Composable
fun StockSignalCard(stock: Stock) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        )
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(stock.symbol, fontWeight = FontWeight.Bold)
                Text(stock.name ?: "", style = MaterialTheme.typography.bodySmall)
            }
            
            val isBuy = stock.analysis?.consensus?.contains("BUY", ignoreCase = true) == true
            Text(
                text = stock.analysis?.consensus ?: "HOLD",
                color = if (isBuy) Color(0xFF10b981) else Color.Gray,
                fontWeight = FontWeight.Bold
            )
        }
    }
}
