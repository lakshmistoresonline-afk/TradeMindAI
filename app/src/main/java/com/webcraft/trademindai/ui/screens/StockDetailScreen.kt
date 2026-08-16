package com.webcraft.trademindai.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StockDetailScreen(navController: NavController, symbol: String) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(symbol) },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .padding(16.dp)
                .verticalScroll(rememberScrollState())
        ) {
            InfoSection(title = "Technical Analysis", content = "RSI: 65 (Neutral)\nEMA 200: Bullish")
            Spacer(modifier = Modifier.height(16.dp))
            InfoSection(title = "Fundamental Analysis", content = "PE Ratio: 25\nIntrinsic Value: ₹1500")
            Spacer(modifier = Modifier.height(16.dp))
            InfoSection(title = "AI Consensus", content = "Strong Buy\nConfidence: 85%")
        }
    }
}

@Composable
fun InfoSection(title: String, content: String) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(text = title, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.primary)
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = content, style = MaterialTheme.typography.bodyLarge)
        }
    }
}
