package com.kingfool.cafeprediction.network

import com.kingfool.cafeprediction.model.*
import retrofit2.http.*

interface ApiService {
    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): LoginResponse

    @GET("api/products")
    suspend fun getProducts(@Query("username") username: String): ProductsResponse

    @POST("api/sales")
    suspend fun addSale(@Body request: SaleRecordRequest): GenericResponse

    @GET("api/weather")
    suspend fun getWeather(
        @Query("lat") lat: Double = 41.0082,
        @Query("lon") lon: Double = 28.9784
    ): WeatherResponse

    @GET("api/predict")
    suspend fun predict(
        @Query("username") username: String,
        @Query("product") product: String,
        @Query("tomorrow_temp") temp: Double,
        @Query("tomorrow_is_weekend") isWeekend: Int
    ): PredictionResponse
}
