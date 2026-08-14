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
    val liveSignals by viewModel.liveSignals.collectAsState()
    val marketStats by viewModel.marketStats.collectAsState()
    val regime by viewModel.regime.collectAsState()
    val loading by viewModel.loading.collectAsState()
    val selectedTimeframe by viewModel.selectedTimeframe.collectAsState()

    val timeframes = listOf("ALL", "INTRADAY", "SWING", "POSITION", "LONG_TERM")

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Market Command Center", fontWeight = FontWeight.Bold) },
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
            Column(modifier = Modifier.padding(padding)) {
                ScrollableTabRow(
                    selectedTabIndex = timeframes.indexOf(selectedTimeframe),
                    edgePadding = 16.dp,
                    containerColor = MaterialTheme.colorScheme.surface,
                    contentColor = MaterialTheme.colorScheme.primary,
                    divider = {}
                ) {
                    timeframes.forEach { timeframe ->
                        Tab(
                            selected = selectedTimeframe == timeframe,
                            onClick = { viewModel.setTimeframe(timeframe) },
                            text = { Text(timeframe.replace("_", " ")) }
                        )
                    }
                }

                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item {
                        Spacer(modifier = Modifier.height(16.dp))
                        MarketRegimeSection(
                            regime = regime?.regime ?: "Initializing...",
                            description = regime?.description ?: "Calculating institutional sentiment..."
                        )
                    }

                    item {
                        Text("Market Pulse", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
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
                                        value = statsList[i].second.value?.toString() ?: "0.0",
                                        change = "${statsList[i].second.change ?: 0.0}%",
                                        isPositive = (statsList[i].second.change ?: 0.0) >= 0,
                                        modifier = Modifier.weight(1f)
                                    )
                                    if (i + 1 < statsList.size) {
                                        MarketStatCard(
                                            name = statsList[i + 1].first,
                                            value = statsList[i + 1].second.value?.toString() ?: "0.0",
                                            change = "${statsList[i + 1].second.change ?: 0.0}%",
                                            isPositive = (statsList[i + 1].second.change ?: 0.0) >= 0,
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
                        Text("AI Forensic Signals", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                    }

                    val filteredStocks = stocks.filter { stock ->
                        val timeframe = stock.structured_consensus?.get("timeframe") as? String
                        val targetTf = if (selectedTimeframe == "POSITION") "MID_TERM" else selectedTimeframe
                        (selectedTimeframe == "ALL" || timeframe == targetTf) && stock.analysis != null
                    }

                    val filteredLiveSignals = liveSignals.filter { signal ->
                        val targetTf = if (selectedTimeframe == "POSITION") "MID_TERM" else selectedTimeframe
                        (selectedTimeframe == "ALL" || signal.timeframe == targetTf || signal.timeframe == selectedTimeframe)
                    }

                    if (filteredStocks.isEmpty() && filteredLiveSignals.isEmpty()) {
                        item {
                            Box(modifier = Modifier.fillMaxWidth().padding(32.dp), contentAlignment = Alignment.Center) {
                                Text("No $selectedTimeframe signals detected.", color = Color.Gray)
                            }
                        }
                    }

                    items(filteredLiveSignals) { signal ->
                        LiveSignalCard(signal)
                    }

                    items(filteredStocks) { stock ->
                        StockSignalCard(stock)
                    }
                    
                    item {
                        Spacer(modifier = Modifier.height(16.dp))
                    }
                }
            }
        }
    }
}

@Composable
fun StockSignalCard(stock: Stock) {
    val structured = stock.structured_consensus
    val entry = (structured?.get("entry") as? Number)?.toDouble() ?: stock.last_price ?: 0.0
    val target = (structured?.get("target") as? Number)?.toDouble() ?: 0.0
    val stopLoss = (structured?.get("stop_loss") as? Number)?.toDouble() ?: 0.0
    val conviction = (structured?.get("conviction") as? Number)?.toInt() ?: 0
    val rating = structured?.get("rating") as? String ?: "HOLD"
    val timeframe = structured?.get("timeframe") as? String ?: "SWING"

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)
        ),
        border = androidx.compose.foundation.BorderStroke(
            1.dp, 
            if (rating.contains("BUY")) Color(0xFF10b981).copy(alpha = 0.5f) 
            else if (rating.contains("SELL")) Color.Red.copy(alpha = 0.5f)
            else Color.Gray.copy(alpha = 0.3f)
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(stock.symbol, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Text(timeframe, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.primary)
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    val isBuy = rating.contains("BUY")
                    val color = if (isBuy) Color(0xFF10b981) else if (rating.contains("SELL")) Color.Red else Color.Gray
                    Text(
                        text = rating,
                        color = color,
                        fontWeight = FontWeight.Black,
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text("$conviction% Conviction", style = MaterialTheme.typography.labelSmall, color = Color.Gray)
                }
            }

            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                PriceMetric(label = "ENTRY", value = "₹${entry.toInt()}", color = MaterialTheme.colorScheme.onSurface)
                PriceMetric(label = "TARGET", value = "₹${target.toInt()}", color = Color(0xFF10b981))
                PriceMetric(label = "STOP LOSS", value = "₹${stopLoss.toInt()}", color = Color.Red)
            }

            Spacer(modifier = Modifier.height(12.dp))
            
            val thesis = structured?.get("thesis") as? String ?: stock.analysis?.consensus ?: ""
            Text(
                text = thesis,
                style = MaterialTheme.typography.bodySmall,
                color = Color.Gray,
                maxLines = 2,
                overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis
            )
        }
    }
}

@Composable
fun LiveSignalCard(signal: com.webcraft.trademindai.domain.model.LiveSignal) {
    val isBuy = signal.direction == "LONG" || signal.rating.contains("BUY")
    val color = if (isBuy) Color(0xFF10b981) else if (signal.rating.contains("SELL")) Color.Red else Color.Gray

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)
        ),
        border = androidx.compose.foundation.BorderStroke(
            1.dp, 
            color.copy(alpha = 0.5f)
        )
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(signal.symbol, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Text(signal.timeframe, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.primary)
                }
                
                Column(horizontalAlignment = Alignment.End) {
                    Text(
                        text = signal.rating,
                        color = color,
                        fontWeight = FontWeight.Black,
                        style = MaterialTheme.typography.titleMedium
                    )
                    Text("${signal.conviction.toInt()}% Conviction", style = MaterialTheme.typography.labelSmall, color = Color.Gray)
                }
            }

            Spacer(modifier = Modifier.height(12.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                PriceMetric(label = "ENTRY", value = "₹${signal.entry_price.toInt()}", color = MaterialTheme.colorScheme.onSurface)
                PriceMetric(label = "TARGET", value = "₹${(signal.target_price ?: 0.0).toInt()}", color = Color(0xFF10b981))
                PriceMetric(label = "STOP LOSS", value = "₹${(signal.stop_loss_price ?: 0.0).toInt()}", color = Color.Red)
            }

            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                text = "Live AI Signal - Status: ${signal.status}",
                style = MaterialTheme.typography.bodySmall,
                color = Color.Gray,
                maxLines = 2,
                overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis
            )
        }
    }
}

@Composable
fun PriceMetric(label: String, value: String, color: Color) {
    Column {
        Text(label, style = MaterialTheme.typography.labelSmall, color = Color.Gray)
        Text(value, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = color)
    }
}

@Composable
fun MarketRegimeSection(regime: String, description: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer.copy(alpha = 0.1f))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Institutional Market Regime", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.tertiary)
            Spacer(modifier = Modifier.height(4.dp))
            Text(regime.uppercase(), style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = Color(0xFF10b981))
            Text(description, style = MaterialTheme.typography.bodySmall, color = Color.Gray)
        }
    }
}

@Composable
fun MarketBreadthCard(breadth: com.webcraft.trademindai.data.remote.MarketStatsResponse?) {
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
                    Text("${breadth?.advancing ?: 0}", fontWeight = FontWeight.Bold, color = Color(0xFF10b981))
                }
                Column {
                    Text("Declining", style = MaterialTheme.typography.bodySmall)
                    Text("${breadth?.declining ?: 0}", fontWeight = FontWeight.Bold, color = Color.Red)
                }
                Column {
                    Text("Ratio", style = MaterialTheme.typography.bodySmall)
                    Text("${breadth?.ratio ?: 0.0}", fontWeight = FontWeight.Bold)
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
