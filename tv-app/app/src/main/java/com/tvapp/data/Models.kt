package com.tvapp.data

import org.json.JSONObject

/** 聚合配置数据模型（与 Python 端 my_api.json 对应）。 */
data class Site(
    val key: String,
    val name: String,
    val api: String,
    val type: Int,
)

data class Live(
    val name: String,
    val url: String,
    val type: Int,
)

data class AliveSummary(
    val vodAlive: Int,
    val liveAlive: Int,
    val aggAlive: Int,
    val sites: Int,
    val lives: Int,
    val checkedAt: String,
)

data class AggregateConfig(
    val sites: List<Site>,
    val lives: List<Live>,
    val summary: AliveSummary?,
) {
    companion object {
        fun fromJson(obj: JSONObject): AggregateConfig {
            val sites = obj.optJSONArray("sites")?.let { arr ->
                (0 until arr.length()).map { i ->
                    val o = arr.getJSONObject(i)
                    Site(
                        key = o.optString("key"),
                        name = o.optString("name"),
                        api = o.optString("api"),
                        type = o.optInt("type", 1),
                    )
                }
            }.orEmpty()

            val lives = obj.optJSONArray("lives")?.let { arr ->
                (0 until arr.length()).map { i ->
                    val o = arr.getJSONObject(i)
                    Live(
                        name = o.optString("name"),
                        url = o.optString("url"),
                        type = o.optInt("type", 0),
                    )
                }
            }.orEmpty()

            val summary = obj.optJSONObject("alive_summary")?.let { s ->
                AliveSummary(
                    vodAlive = s.optInt("vod_alive"),
                    liveAlive = s.optInt("live_alive"),
                    aggAlive = s.optInt("agg_alive"),
                    sites = s.optInt("sites"),
                    lives = s.optInt("lives"),
                    checkedAt = s.optString("checked_at"),
                )
            }

            return AggregateConfig(sites, lives, summary)
        }
    }
}
