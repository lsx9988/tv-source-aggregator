package com.tvapp.player

import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer

/** 简单封装 ExoPlayer 播放一个 URL。 */
fun ExoPlayer.playUrl(url: String) {
    setMediaItem(MediaItem.fromUri(url))
    prepare()
    playWhenReady = true
}
