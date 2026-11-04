package com.tvapp.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.tvapp.data.AggregateConfig
import com.tvapp.data.Live
import com.tvapp.data.Site

@Composable
fun HomeScreen(
    config: AggregateConfig?,
    loading: Boolean,
    error: String?,
    onPlay: (String) -> Unit,
) {
    Column(Modifier.fillMaxSize().background(Color(0xFF101418)).padding(16.dp)) {
        Text("TV Box 源聚合", color = Color.White, fontSize = 22.sp)
        Spacer(Modifier.height(8.dp))

        when {
            loading -> CircularProgressIndicator()
            error != null -> Text("加载失败：$error", color = Color(0xFFFF6B6B))
            config == null -> Text("暂无数据", color = Color.Gray)
            else -> {
                config.summary?.let { s ->
                    Text(
                        "点播存活 ${s.vodAlive} | 直播存活 ${s.liveAlive} | 聚合 ${s.aggAlive} | 更新于 ${s.checkedAt.take(19)}",
                        color = Color(0xFF9AA0A6),
                        fontSize = 12.sp,
                    )
                }
                Spacer(Modifier.height(12.dp))
                LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    items(config.sites) { site ->
                        SiteCard(site) { onPlay(site.api) }
                    }
                    items(config.lives) { live ->
                        LiveCard(live) { onPlay(live.url) }
                    }
                }
            }
        }
    }
}

@Composable
private fun SiteCard(site: Site, onClick: () -> Unit) {
    Card(
        shape = RoundedCornerShape(10.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E2530)),
        onClick = onClick,
    ) {
        Column(Modifier.padding(12.dp)) {
            Text(site.name.ifBlank { site.api }, color = Color.White, fontSize = 16.sp)
            Text("点播 · ${site.api}", color = Color(0xFF9AA0A6), fontSize = 11.sp)
        }
    }
}

@Composable
private fun LiveCard(live: Live, onClick: () -> Unit) {
    Card(
        shape = RoundedCornerShape(10.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF2A1F2D)),
        onClick = onClick,
    ) {
        Column(Modifier.padding(12.dp)) {
            Text(live.name.ifBlank { live.url }, color = Color.White, fontSize = 16.sp)
            Text("直播 · ${live.url}", color = Color(0xFF9AA0A6), fontSize = 11.sp)
        }
    }
}
