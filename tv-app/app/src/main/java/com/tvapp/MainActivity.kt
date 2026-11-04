package com.tvapp

import android.net.Uri
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.*
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.ui.Modifier
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView
import androidx.compose.ui.viewinterop.AndroidView
import com.tvapp.data.AggregateConfig
import com.tvapp.network.ConfigApi
import com.tvapp.ui.HomeScreen
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private val vm = AppViewModel()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(Modifier.fillMaxSize()) {
                    val state by vm.state.collectAsState()
                    if (state.playingUrl != null) {
                        PlayerScreen(url = state.playingUrl!!, onExit = vm::stopPlay)
                    } else {
                        HomeScreen(
                            config = state.config,
                            loading = state.loading,
                            error = state.error,
                            onPlay = vm::play,
                        )
                    }
                }
            }
        }
        vm.load()
    }
}

data class UiState(
    val loading: Boolean = true,
    val config: AggregateConfig? = null,
    val error: String? = null,
    val playingUrl: String? = null,
)

class AppViewModel : ViewModel() {
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state

    fun load() {
        viewModelScope.launch {
            _state.value = _state.value.copy(loading = true, error = null)
            val r = ConfigApi.fetchConfig()
            _state.value = r.fold(
                onSuccess = { cfg -> _state.value.copy(loading = false, config = cfg) },
                onFailure = { e -> _state.value.copy(loading = false, error = e.message ?: "unknown") },
            )
        }
    }

    fun play(url: String) { _state.value = _state.value.copy(playingUrl = url) }
    fun stopPlay() { _state.value = _state.value.copy(playingUrl = null) }
}

@androidx.compose.runtime.Composable
private fun PlayerScreen(url: String, onExit: () -> Unit) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val player = remember { ExoPlayer.Builder(context).build() }
    DisposableEffect(Unit) {
        player.setMediaItem(MediaItem.fromUri(url))
        player.prepare()
        player.playWhenReady = true
        onDispose { player.release() }
    }
    AndroidView(
        factory = { ctx ->
            PlayerView(ctx).apply {
                this.player = player
                setOnClickListener { onExit() }
            }
        },
        modifier = Modifier.fillMaxSize(),
    )
}
