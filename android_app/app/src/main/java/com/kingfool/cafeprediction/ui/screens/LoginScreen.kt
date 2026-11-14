package com.kingfool.cafeprediction.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.kingfool.cafeprediction.model.LoginRequest
import com.kingfool.cafeprediction.model.LoginResponse
import com.kingfool.cafeprediction.network.ApiClient
import com.kingfool.cafeprediction.ui.theme.*
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreen(
    onLoginSuccess: (LoginResponse) -> Unit
) {
    var username by remember { mutableStateOf("ornekkafe") }
    var password by remember { mutableStateOf("") }
    var apiUrl by remember { mutableStateOf(ApiClient.baseUrl) }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(BackgroundDark)
            .padding(24.dp),
        contentAlignment = Alignment.Center
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = CardDark),
            shape = RoundedCornerShape(16.dp),
            elevation = CardDefaults.cardElevation(8.dp)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Başlık & Logo
                Text(
                    text = "🃏 KINGFOOL INC.",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold,
                    color = GSSari
                )
                Text(
                    text = "Kafe Satış & Talep Tahmin Sistemi",
                    fontSize = 13.sp,
                    color = TextMuted,
                    modifier = Modifier.padding(bottom = 24.dp)
                )

                // Kullanıcı Adı
                OutlinedTextField(
                    value = username,
                    onValueChange = { username = it },
                    label = { Text("Kullanıcı Adı") },
                    leadingIcon = { Icon(Icons.Default.Person, contentDescription = null, tint = GSSari) },
                    modifier = Modifier.fillMaxWidth(),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = GSSari,
                        unfocusedBorderColor = TextMuted,
                        focusedLabelColor = GSSari,
                        unfocusedLabelColor = TextMuted
                    )
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Şifre
                OutlinedTextField(
                    value = password,
                    onValueChange = { password = it },
                    label = { Text("Şifre") },
                    leadingIcon = { Icon(Icons.Default.Lock, contentDescription = null, tint = GSSari) },
                    visualTransformation = PasswordVisualTransformation(),
                    modifier = Modifier.fillMaxWidth(),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = GSSari,
                        unfocusedBorderColor = TextMuted,
                        focusedLabelColor = GSSari,
                        unfocusedLabelColor = TextMuted
                    )
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Sunucu / API URL Ayarı
                OutlinedTextField(
                    value = apiUrl,
                    onValueChange = {
                        apiUrl = it
                        ApiClient.baseUrl = it
                    },
                    label = { Text("Python API URL") },
                    modifier = Modifier.fillMaxWidth(),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = GSSari,
                        unfocusedBorderColor = TextMuted,
                        focusedLabelColor = GSSari,
                        unfocusedLabelColor = TextMuted
                    )
                )

                if (errorMessage != null) {
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = errorMessage ?: "",
                        color = MaterialTheme.colorScheme.error,
                        fontSize = 13.sp
                    )
                }

                Spacer(modifier = Modifier.height(24.dp))

                // Giriş Butonu
                Button(
                    onClick = {
                        isLoading = true
                        errorMessage = null
                        scope.launch {
                            try {
                                val res = ApiClient.getService().login(LoginRequest(username.trim(), password.trim()))
                                isLoading = false
                                if (res.success) {
                                    onLoginSuccess(res)
                                } else {
                                    errorMessage = "Giriş başarısız!"
                                }
                            } catch (e: Exception) {
                                isLoading = false
                                errorMessage = "Bağlantı Hatası: ${e.localizedMessage ?: "Sunucuya ulaşılamadı"}"
                            }
                        }
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = GSKirmizi,
                        contentColor = TextLight
                    ),
                    enabled = !isLoading
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(color = GSSari, modifier = Modifier.size(24.dp))
                    } else {
                        Text(
                            text = "GİRİŞ YAP",
                            fontWeight = FontWeight.Bold,
                            fontSize = 16.sp
                        )
                    }
                }
            }
        }
    }
}
