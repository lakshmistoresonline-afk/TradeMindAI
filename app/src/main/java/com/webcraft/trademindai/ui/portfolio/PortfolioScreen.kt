package com.webcraft.trademindai.ui.portfolio

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.webcraft.trademindai.ui.dashboard.DashboardViewModel
import com.webcraft.trademindai.ui.dashboard.StockSignalCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PortfolioScreen(
    viewModel: DashboardViewModel = hiltViewModel()
) {
    val stocks by viewModel.stocks.collectAsState()
    val myStocks = stocks.filter { it.analysis != null }

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Portfolio", fontWeight = FontWeight.Bold) })
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { /* Add symbol */ }) {
                Icon(Icons.Default.Add, contentDescription = "Add Symbol")
            }
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier.padding(padding).fillMaxSize(),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                Text("Watchlist Performance", style = MaterialTheme.typography.titleLarge)
            }
            
            items(myStocks) { stock ->
                StockSignalCard(stock)
            }
        }
    }
}
