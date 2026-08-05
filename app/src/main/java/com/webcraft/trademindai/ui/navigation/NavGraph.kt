package com.webcraft.trademindai.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.webcraft.trademindai.ui.screens.DashboardScreen
import com.webcraft.trademindai.ui.screens.LoginScreen
import com.webcraft.trademindai.ui.screens.SplashScreen
import com.webcraft.trademindai.ui.screens.ChatScreen
import com.webcraft.trademindai.ui.screens.StockDetailScreen

@Composable
fun NavGraph(navController: NavHostController) {
    NavHost(
        navController = navController,
        startDestination = Screen.Splash.route
    ) {
        composable(Screen.Splash.route) {
            SplashScreen(navController)
        }
        composable(Screen.Login.route) {
            LoginScreen(navController)
        }
        composable(Screen.Dashboard.route) {
            DashboardScreen(navController)
        }
        composable(Screen.Treemap.route) {
            // Placeholder for Android Treemap
            androidx.compose.material3.Text("Market Treemap coming to mobile")
        }
        composable(Screen.PaperTrading.route) {
            androidx.compose.material3.Text("Paper Trading terminal coming to mobile")
        }
        composable(Screen.Calendar.route) {
            androidx.compose.material3.Text("Economic Calendar coming to mobile")
        }
        composable(Screen.Chat.route) {
            ChatScreen()
        }
        composable(
            route = "stock_detail/{symbol}"
        ) { backStackEntry ->
            val symbol = backStackEntry.arguments?.getString("symbol") ?: ""
            StockDetailScreen(navController, symbol)
        }
    }
}

sealed class Screen(val route: String) {
    object Splash : Screen("splash")
    object Login : Screen("login")
    object Dashboard : Screen("dashboard")
    object Treemap : Screen("treemap")
    object PaperTrading : Screen("paper_trading")
    object Calendar : Screen("calendar")
    object Chat : Screen("chat")
}
