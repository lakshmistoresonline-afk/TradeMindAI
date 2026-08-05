package com.webcraft.trademindai.ui.analysis

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.webcraft.trademindai.ui.dashboard.DashboardViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AnalysisScreen(
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val stocks by viewModel.stocks.collectAsState()
    val analyzedStocks = stocks.filter { it.analysis != null }

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Institutional Analysis", fontWeight = FontWeight.Bold) })
        }
    ) { padding ->
        if (analyzedStocks.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize().padding(padding), contentAlignment = androidx.compose.ui.Alignment.Center) {
                Text("No analysis available. Run adhoc analysis from dashboard.")
            }
        } else {
            LazyColumn(
                modifier = Modifier.padding(padding).fillMaxSize(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                items(analyzedStocks) { stock ->
                    AnalysisCard(stock)
                }
            }
        }
    }
}

@Composable
fun AnalysisCard(stock: com.webcraft.trademindai.domain.model.Stock) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(stock.symbol, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(8.dp))
            
            stock.analysis?.recommendations?.forEach { recommendation ->
                Text(
                    text = "${recommendation.agent} Agent:",
                    style = MaterialTheme.typography.labelLarge,
                    color = Color(0xFF10b981)
                )
                Text(
                    text = recommendation.analysis,
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
            
            HorizontalDivider(modifier = Modifier.padding(vertical = 8.dp))
            
            Text("Final Consensus:", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            Text(stock.analysis?.consensus ?: "", fontWeight = FontWeight.Bold)
        }
    }
}
