# tv-source-aggregator

自动检测、聚合公开 TVBox 影视源（点播 API / 直播 M3U / 聚合接口），生成只含存活源的 `output/my_api.json`。

## 功能

- **点播源检测**：请求 `?ac=list`，验证 JSON 结构
- **直播源检测**：解析 M3U，抽样探测流地址
- **聚合接口检测**：解析 TVBox 格式 JSON，提取 sites / lives
- **GitHub Actions**：每 6 小时自动运行并提交结果，支持手动触发

## 目录结构

```
tv-source-aggregator/
├── .github/workflows/tv-source-check.yml   # Actions 工作流
├── main.py                                  # 主入口
├── config.py                                # 配置
├── requirements.txt
├── scripts/
│   ├── fetch_vod.py
│   ├── fetch_live.py
│   ├── fetch_aggregators.py
│   └── build_output.py
├── sources/
│   ├── vod_seeds.txt
│   ├── live_seeds.txt
│   └── aggregator_seeds.txt
├── output/my_api.json                       # 产物（Actions 自动生成）
└── tv-app/                                  # Android (Kotlin/Compose) 客户端
```

## 手动运行

```bash
pip install -r requirements.txt
python main.py
```

## 验证

- 打开仓库 Actions 页面，确认 `TV Source Check` 工作流最近一次运行成功
- 打开 `output/my_api.json`，检查 `alive_summary` 字段

## 客户端

`tv-app/` 是一个 Kotlin + Jetpack Compose + ExoPlayer 的安卓客户端，启动时自动拉取 `output/my_api.json`，列出存活的点播/直播源并可直接播放，适配手机与 Android TV。
