package com.kingfool.cafeprediction.model

import com.google.gson.annotations.SerializedName

data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    val success: Boolean,
    val username: String,
    val role: String,
    val products: List<String>,
    @SerializedName("setup_completed") val setupCompleted: Boolean
)

data class ProductsResponse(
    val username: String,
    val products: List<String>,
    @SerializedName("setup_completed") val setupCompleted: Boolean
)

data class SaleRecordRequest(
    val username: String,
    val product: String,
    val date: String,
    val amount: Double,
    val temperature: Double,
    @SerializedName("is_weekend") val isWeekend: Int,
    @SerializedName("has_promotion") val hasPromotion: Int
)

data class GenericResponse(
    val success: Boolean,
    val message: String
)

data class WeatherResponse(
    @SerializedName("today_temp") val todayTemp: Double,
    @SerializedName("tomorrow_temp") val tomorrowTemp: Double,
    @SerializedName("today_date") val todayDate: String?,
    @SerializedName("tomorrow_date") val tomorrowDate: String?
)

data class PredictionResponse(
    val success: Boolean,
    val prediction: Int?,
    @SerializedName("data_count") val dataCount: Int,
    val message: String?,
    val product: String?,
    @SerializedName("tomorrow_temp") val tomorrowTemp: Double?,
    val engine: String?
)
