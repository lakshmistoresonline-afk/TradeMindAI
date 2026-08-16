package com.webcraft.trademindai.ui.papertrading

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.History
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
import com.webcraft.trademindai.ui.dashboard.DashboardViewModel
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PaperTradingScreen(
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val auditData by viewModel.performanceAudit.collectAsState()
    val loading by viewModel.loading.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Signal Validation", fontWeight = FontWeight.Bold) })
        }
    ) { padding ->
        if (loading && auditData.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier.padding(padding).fillMaxSize(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                item {
                    AuditHeader(auditData)
                }

                item {
                    Text("Historical Verification Log", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Text("Signals verified against 30-day price action.", style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                }

                items(auditData) { signal ->
                    AuditSignalCard(signal)
                }
                
                item {
                    Spacer(modifier = Modifier.height(16.dp))
                }
            }
        }
    }
}

@Composable
fun AuditHeader(data: List<Map<String, Any>>) {
    val total = data.size
    val successCount = data.count { it["success"] == true }
    val winRate = if (total > 0) (successCount.toFloat() / total * 100) else 0f
    val avgProfit = if (total > 0) data.sumOf { (it["profit_pct"] as? Number)?.toDouble() ?: 0.0 } / total else 0.0

    Card(
        modifier = Modifier.fillMaxWidth().padding(bottom = 16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.2f))
    ) {
        Row(
            modifier = Modifier.padding(16.dp).fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            HeaderStat(label = "WIN RATE", value = "${String.format(Locale.US, "%.1f", winRate)}%", color = MaterialTheme.colorScheme.primary)
            HeaderStat(label = "AVG P&L", value = "+${String.format(Locale.US, "%.2f", avgProfit)}%", color = Color(0xFF10b981))
            HeaderStat(label = "AUDITS", value = "$total", color = MaterialTheme.colorScheme.onSurface)
        }
    }
}

@Composable
fun HeaderStat(label: String, value: String, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, style = MaterialTheme.typography.labelSmall, color = Color.Gray)
        Text(value, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black, color = color)
    }
}

@Composable
fun AuditSignalCard(signal: Map<String, Any>) {
    val symbol = signal["symbol"] as? String ?: "---"
    val date = signal["date"] as? String ?: "---"
    val entry = (signal["entry"] as? Number)?.toDouble() ?: 0.0
    val target = (signal["target"] as? Number)?.toDouble() ?: 0.0
    val stopLoss = (signal["stop_loss"] as? Number)?.toDouble() ?: 0.0
    val profit = (signal["profit_pct"] as? Number)?.toDouble() ?: 0.0
    val outcome = signal["outcome"] as? String ?: "EXPIRED"

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f))
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(symbol, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
                    Text(date, style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                }
                
                Row(verticalAlignment = Alignment.CenterVertically) {
                    val color = if (outcome == "TARGET_HIT") Color(0xFF10b981) else if (outcome == "STOP_LOSS") Color.Red else Color.Gray
                    val icon = if (outcome == "TARGET_HIT") Icons.Default.CheckCircle else if (outcome == "STOP_LOSS") Icons.Default.Error else Icons.Default.History
                    val label = outcome.replace("_", " ")
                    
                    Icon(icon, contentDescription = null, tint = color, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(label, color = color, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.labelSmall)
                }
            }

            HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp), thickness = 0.5.dp, color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.1f))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                PriceItem(label = "ENTRY", value = "₹${entry.toInt()}")
                PriceItem(label = "TARGET", value = "₹${target.toInt()}", color = Color(0xFF10b981))
                PriceItem(label = "STOP LOSS", value = "₹${stopLoss.toInt()}", color = Color.Red)
                PriceItem(
                    label = "RESULT %", 
                    value = "${if (profit >= 0) "+" else ""}${String.format(Locale.US, "%.2f", profit)}%",
                    color = if (profit >= 0) Color(0xFF10b981) else Color.Red
                )
            }
        }
    }
}

@Composable
fun PriceItem(label: String, value: String, color: Color = MaterialTheme.colorScheme.onSurface) {
    Column {
        Text(label, style = MaterialTheme.typography.labelSmall, color = Color.Gray)
        Text(value, style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold, color = color)
    }
}
