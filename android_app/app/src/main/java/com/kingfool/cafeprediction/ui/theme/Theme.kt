package com.kingfool.cafeprediction.ui.theme

import androidx.compose.material3.*
import androidx.compose.runtime.Composable

private val DarkColorScheme = darkColorScheme(
    primary = GSSari,
    onPrimary = BackgroundDark,
    secondary = GSKirmizi,
    onSecondary = TextLight,
    background = BackgroundDark,
    surface = CardDark,
    onBackground = TextLight,
    onSurface = TextLight
)

@Composable
fun KingfoolTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = DarkColorScheme,
        content = content
    )
}
