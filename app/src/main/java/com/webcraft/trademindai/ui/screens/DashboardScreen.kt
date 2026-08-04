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
            items(stocks) { stock ->
                StockItem(stock = stock, onClick = {
                    navController.navigate("stock_detail/${stock.symbol}")
                })
            }
        }
    }
}

@Composable
fun StockItem(stock: com.webcraft.trademindai.data.remote.StockDto, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
        onClick = onClick
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = stock.symbol, style = MaterialTheme.typography.headlineSmall)
            Text(text = stock.name, style = MaterialTheme.typography.bodyMedium)
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = "₹${stock.price}")
                Text(
                    text = "${stock.change}%",
                    color = if (stock.change >= 0) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error
                )
            }
        }
    }
}
