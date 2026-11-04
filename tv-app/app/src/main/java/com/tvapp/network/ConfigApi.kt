package com.tvapp.network

import com.tvapp.data.AggregateConfig
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * 从 GitHub 仓库读取聚合接口。
 * 默认地址：本仓库 output/my_api.json 的 raw 链接。
 */
object ConfigApi {
    private const val RAW_URL =
        "https://raw.githubusercontent.com/lsx9988/tv-source-aggregator/main/output/my_api.json"

    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    suspend fun fetchConfig(url: String = RAW_URL): Result<AggregateConfig> =
        withContext(Dispatchers.IO) {
            runCatching {
                val req = Request.Builder().url(url).build()
                client.newCall(req).execute().use { resp ->
                    if (!resp.isSuccessful) error("HTTP ${resp.code}")
                    val body = resp.body?.string().orEmpty()
                    AggregateConfig.fromJson(JSONObject(body))
                }
            }
        }
}
