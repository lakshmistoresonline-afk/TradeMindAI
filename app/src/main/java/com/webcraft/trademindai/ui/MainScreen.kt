package com.webcraft.trademindai.ui

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountBalanceWallet
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Dashboard
import androidx.compose.material.icons.filled.MenuBook
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.webcraft.trademindai.ui.analysis.AnalysisScreen
import com.webcraft.trademindai.ui.dashboard.DashboardScreen
import com.webcraft.trademindai.ui.market.MarketScreen
import com.webcraft.trademindai.ui.opportunities.OpportunitiesScreen
import com.webcraft.trademindai.ui.papertrading.PaperTradingScreen
import com.webcraft.trademindai.ui.portfolio.PortfolioScreen

@Composable
fun MainScreen() {
    val navController = rememberNavController()
    Scaffold(
        bottomBar = {
            BottomBar(navController = navController)
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = "dashboard",
            modifier = Modifier.padding(innerPadding)
        ) {
            composable("dashboard") { DashboardScreen() }
            composable("market") { MarketScreen(onStockClick = { /* Navigate to detail */ }) }
            composable("portfolio") { PortfolioScreen() }
            composable("analysis") { AnalysisScreen() }
            composable("opportunities") { OpportunitiesScreen() }
            composable("paper_trading") { PaperTradingScreen() }
        }
    }
}

@Composable
fun BottomBar(navController: NavHostController) {
    val items = listOf(
        BottomNavItem("Home", "dashboard", Icons.Default.Dashboard),
        BottomNavItem("Markets", "market", Icons.Default.TrendingUp),
        BottomNavItem("Signals", "opportunities", Icons.Default.Star),
        BottomNavItem("Portfolio", "portfolio", Icons.Default.AccountBalanceWallet),
        BottomNavItem("AI", "analysis", Icons.Default.AutoAwesome)
    )
    NavigationBar {
        val navBackStackEntry by navController.currentBackStackEntryAsState()
        val currentDestination = navBackStackEntry?.destination
        items.forEach { item ->
            NavigationBarItem(
                icon = { Icon(item.icon, contentDescription = item.title) },
                label = { Text(item.title) },
                selected = currentDestination?.hierarchy?.any { it.route == item.route } == true,
                onClick = {
                    navController.navigate(item.route) {
                        popUpTo(navController.graph.findStartDestination().id) {
                            saveState = true
                        }
                        launchSingleTop = true
                        restoreState = true
                    }
                }
            )
        }
    }
}

data class BottomNavItem(
    val title: String,
    val route: String,
    val icon: androidx.compose.ui.graphics.vector.ImageVector
)
