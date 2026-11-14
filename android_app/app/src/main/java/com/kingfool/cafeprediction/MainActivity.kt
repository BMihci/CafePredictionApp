package com.kingfool.cafeprediction

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.kingfool.cafeprediction.model.LoginResponse
import com.kingfool.cafeprediction.ui.screens.DashboardScreen
import com.kingfool.cafeprediction.ui.screens.LoginScreen
import com.kingfool.cafeprediction.ui.theme.BackgroundDark
import com.kingfool.cafeprediction.ui.theme.KingfoolTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            KingfoolTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = BackgroundDark
                ) {
                    var loggedInUser by remember { mutableStateOf<LoginResponse?>(null) }

                    if (loggedInUser == null) {
                        LoginScreen(
                            onLoginSuccess = { user ->
                                loggedInUser = user
                            }
                        )
                    } else {
                        DashboardScreen(
                            user = loggedInUser!!,
                            onLogout = {
                                loggedInUser = null
                            }
                        )
                    }
                }
            }
        }
    }
}
