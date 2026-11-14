package com.kingfool.cafeprediction.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.ExitToApp
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.kingfool.cafeprediction.model.*
import com.kingfool.cafeprediction.network.ApiClient
import com.kingfool.cafeprediction.ui.theme.*
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    user: LoginResponse,
    onLogout: () -> Unit
) {
    val scope = rememberCoroutineScope()
    var products by remember { mutableStateOf(user.products.ifEmpty { listOf("Cold Brew", "Iced Latte", "Iced Americano", "Brownie") }) }
    var todayTemp by remember { mutableStateOf(25.0) }
    var tomorrowTemp by remember { mutableStateOf(26.0) }
    var predictionResult by remember { mutableStateOf<String?>(null) }
    var isPredicting by remember { mutableStateOf(false) }
    var activeProductForPrediction by remember { mutableStateOf(products.firstOrNull() ?: "Cold Brew") }

    // Satış Girişi Durumları
    var selectedProductForSale by remember { mutableStateOf<String?>(null) }
    var saleAmountInput by remember { mutableStateOf("") }
    var isSavingSale by remember { mutableStateOf(false) }
    var statusMessage by remember { mutableStateOf<String?>(null) }

    val todayStr = remember { SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(Date()) }

    // İlk açılışta hava durumunu çek
    LaunchedEffect(Unit) {
        try {
            val weather = ApiClient.getService().getWeather()
            todayTemp = weather.todayTemp
            tomorrowTemp = weather.tomorrowTemp
        } catch (_: Exception) {}
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("Kingfool Inc.", fontWeight = FontWeight.Bold, color = GSSari, fontSize = 18.sp)
                        Text("Kullanıcı: ${user.username}", color = TextMuted, fontSize = 12.sp)
                    }
                },
                actions = {
                    IconButton(onClick = onLogout) {
                        Icon(Icons.Default.ExitToApp, contentDescription = "Çıkış", tint = GSSari)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = CardDark)
            )
        },
        containerColor = BackgroundDark
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // 1. Canlı Hava Durumu Kartı
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = CardDark),
                    shape = RoundedCornerShape(14.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.WbSunny, contentDescription = null, tint = GSSari, modifier = Modifier.size(36.dp))
                            Spacer(modifier = Modifier.width(12.dp))
                            Column {
                                Text("Canlı Hava Durumu", fontWeight = FontWeight.Bold, color = TextLight, fontSize = 15.sp)
                                Text("Bugün: ${todayTemp}°C  |  Yarın: ${tomorrowTemp}°C", color = TextMuted, fontSize = 13.sp)
                            }
                        }
                    }
                }
            }

            // 2. Yapay Zeka Tahmini Bölümü
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = SurfaceDark),
                    shape = RoundedCornerShape(14.dp)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.AutoAwesome, contentDescription = null, tint = GSSari)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Yarın İçin Yapay Zeka Satış Tahmini", fontWeight = FontWeight.Bold, color = GSSari, fontSize = 15.sp)
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        Text("Tahmin Edilecek Ürün: $activeProductForPrediction", color = TextLight, fontSize = 14.sp)

                        if (predictionResult != null) {
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = predictionResult ?: "",
                                fontWeight = FontWeight.Bold,
                                color = GSSariAcik,
                                fontSize = 16.sp
                            )
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        Button(
                            onClick = {
                                isPredicting = true
                                predictionResult = null
                                scope.launch {
                                    try {
                                        val cal = Calendar.getInstance()
                                        cal.add(Calendar.DAY_OF_YEAR, 1)
                                        val isWeekend = if (cal.get(Calendar.DAY_OF_WEEK) in listOf(Calendar.SATURDAY, Calendar.SUNDAY)) 1 else 0

                                        val res = ApiClient.getService().predict(
                                            username = user.username,
                                            product = activeProductForPrediction,
                                            temp = tomorrowTemp,
                                            isWeekend = isWeekend
                                        )
                                        isPredicting = false
                                        if (res.success && res.prediction != null) {
                                            predictionResult = "🎯 Tahmini Talep: ${res.prediction} Adet (${res.dataCount} gün eğitildi)"
                                        } else {
                                            predictionResult = res.message ?: "Tahmin yapılamadı."
                                        }
                                    } catch (e: Exception) {
                                        isPredicting = false
                                        predictionResult = "Hata: ${e.localizedMessage}"
                                    }
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = GSKirmizi),
                            modifier = Modifier.fillMaxWidth(),
                            enabled = !isPredicting
                        ) {
                            if (isPredicting) {
                                CircularProgressIndicator(color = GSSari, modifier = Modifier.size(20.dp))
                            } else {
                                Text("YARININ TAHMİNİNİ HESAPLA")
                            }
                        }
                    }
                }
            }

            // Durum Bildirimi
            if (statusMessage != null) {
                item {
                    Text(
                        text = statusMessage ?: "",
                        color = GSSari,
                        fontWeight = FontWeight.Medium,
                        fontSize = 14.sp
                    )
                }
            }

            // 3. Ürünler Listesi (Hızlı Satış Girişi)
            item {
                Text(
                    text = "Ürünler & Günlük Satış Girişi",
                    fontWeight = FontWeight.Bold,
                    color = TextLight,
                    fontSize = 16.sp,
                    modifier = Modifier.padding(top = 8.dp)
                )
            }

            items(products) { prod ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = CardDark),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(prod, fontWeight = FontWeight.Bold, color = TextLight, fontSize = 15.sp)
                            Text("Bugün: $todayStr", color = TextMuted, fontSize = 12.sp)
                        }

                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            // Tahmin için seç
                            OutlinedButton(
                                onClick = {
                                    activeProductForPrediction = prod
                                    predictionResult = null
                                },
                                colors = ButtonDefaults.outlinedButtonColors(contentColor = GSSari)
                            ) {
                                Text("Tahmin", fontSize = 12.sp)
                            }

                            // Satış Gir
                            Button(
                                onClick = { selectedProductForSale = prod },
                                colors = ButtonDefaults.buttonColors(containerColor = GSKirmizi)
                            ) {
                                Text("Satış Gir", fontSize = 12.sp)
                            }
                        }
                    }
                }
            }
        }

        // Satış Girişi Modal / Dialog
        if (selectedProductForSale != null) {
            AlertDialog(
                onDismissRequest = { selectedProductForSale = null },
                containerColor = CardDark,
                title = { Text("${selectedProductForSale} Satış Girişi", color = GSSari) },
                text = {
                    Column {
                        Text("Tarih: $todayStr  |  Sıcaklık: ${todayTemp}°C", color = TextMuted, fontSize = 12.sp)
                        Spacer(modifier = Modifier.height(12.dp))
                        OutlinedTextField(
                            value = saleAmountInput,
                            onValueChange = { saleAmountInput = it },
                            label = { Text("Satılan Adet") },
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                            colors = OutlinedTextFieldDefaults.colors(
                                focusedBorderColor = GSSari,
                                focusedLabelColor = GSSari
                            )
                        )
                    }
                },
                confirmButton = {
                    Button(
                        onClick = {
                            val amount = saleAmountInput.toDoubleOrNull()
                            if (amount != null && amount >= 0) {
                                isSavingSale = true
                                scope.launch {
                                    try {
                                        val cal = Calendar.getInstance()
                                        val isWeekend = if (cal.get(Calendar.DAY_OF_WEEK) in listOf(Calendar.SATURDAY, Calendar.SUNDAY)) 1 else 0

                                        val res = ApiClient.getService().addSale(
                                            SaleRecordRequest(
                                                username = user.username,
                                                product = selectedProductForSale!!,
                                                date = todayStr,
                                                amount = amount,
                                                temperature = todayTemp,
                                                isWeekend = isWeekend,
                                                hasPromotion = 0
                                            )
                                        )
                                        isSavingSale = false
                                        statusMessage = "✅ ${res.message}"
                                        selectedProductForSale = null
                                        saleAmountInput = ""
                                    } catch (e: Exception) {
                                        isSavingSale = false
                                        statusMessage = "❌ Hata: ${e.localizedMessage}"
                                    }
                                }
                            }
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = GSKirmizi)
                    ) {
                        Text("KAYDET")
                    }
                },
                dismissButton = {
                    TextButton(onClick = { selectedProductForSale = null }) {
                        Text("İptal", color = TextMuted)
                    }
                }
            )
        }
    }
}
