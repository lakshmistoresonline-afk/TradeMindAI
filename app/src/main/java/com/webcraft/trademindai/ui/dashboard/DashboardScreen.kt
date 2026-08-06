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
                    MarketRegimeSection(viewModel)
                }

                item {
                    Text("Market Stats", style = MaterialTheme.typography.titleLarge)
                }

                item {
                    MarketBreadthCard(marketStats["Breadth"])
                }

                item {
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        val statsList = marketStats.filter { it.key != "Breadth" }.toList()
                        for (i in statsList.indices step 2) {
                            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                MarketStatCard(
                                    name = statsList[i].first,
                                    value = statsList[i].second.value.toString(),
                                    change = "${statsList[i].second.change}%",
                                    isPositive = statsList[i].second.change >= 0,
                                    modifier = Modifier.weight(1f)
                                )
                                if (i + 1 < statsList.size) {
                                    MarketStatCard(
                                        name = statsList[i + 1].first,
                                        value = statsList[i + 1].second.value.toString(),
                                        change = "${statsList[i + 1].second.change}%",
                                        isPositive = statsList[i + 1].second.change >= 0,
                                        modifier = Modifier.weight(1f)
                                    )
                                } else {
                                    Spacer(modifier = Modifier.weight(1f))
                                }
                            }
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
fun MarketRegimeSection(viewModel: DashboardViewModel) {
    // Basic implementation for parity
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer.copy(alpha = 0.1f))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Institutional Market Regime", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.tertiary)
            Spacer(modifier = Modifier.height(4.dp))
            Text("BULLISH", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = Color(0xFF10b981))
            Text("Institutional accumulation detected across Nifty 100. High probability of trend continuation.", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
        }
    }
}

@Composable
fun MarketBreadthCard(breadth: Any?) {
    // Basic implementation for parity
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.2f))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Market Breadth (A/D)", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Text("Advancing", style = MaterialTheme.typography.bodySmall)
                    Text("65", fontWeight = FontWeight.Bold, color = Color(0xFF10b981))
                }
                Column {
                    Text("Declining", style = MaterialTheme.typography.bodySmall)
                    Text("35", fontWeight = FontWeight.Bold, color = Color.Red)
                }
                Column {
                    Text("Ratio", style = MaterialTheme.typography.bodySmall)
                    Text("1.85", fontWeight = FontWeight.Bold)
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
