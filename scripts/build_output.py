"""把三类检测结果合并成 TVBox 兼容的 my_api.json。

输出结构：
{
  "spider": "",
  "sites": [...],
  "lives": [...],
  "parses": [],
  "flags": [],
  "alive_summary": {
    "vod": 12,
    "live": 5,
    "aggregator": 2,
    "checked_at": "..."
  }
}
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from config import OUTPUT_JSON


def build(vod_results: list[dict], live_results: list[dict], agg_results: list[dict]) -> dict[str, Any]:
    sites: list[dict] = []
    lives: list[dict] = []

    # 聚合接口里的站点（去重，按 api 去重）
    seen_api: set[str] = set()
    for agg in agg_results:
        if not agg["alive"]:
            continue
        for s in agg.get("sites_data", []):
            api = s.get("api") or s.get("url") or ""
            if api and api not in seen_api:
                seen_api.add(api)
                sites.append({
                    "key": s.get("key") or api,
                    "name": s.get("name") or api,
                    "type": s.get("type", 1),
                    "api": api,
                    "searchable": s.get("searchable", 1),
                    "quickSearch": s.get("quickSearch", 1),
                })
        for l in agg.get("lives_data", []):
            lives.append({
                "name": l.get("name", "直播"),
                "type": l.get("type", 0),
                "url": l.get("url", ""),
            })

    # 独立点播源也作为 site 加进来
    for v in vod_results:
        if not v["alive"]:
            continue
        url = v["url"]
        if url not in seen_api:
            seen_api.add(url)
            sites.append({
                "key": url,
                "name": v.get("title") or url.split("//")[-1].split("/")[0],
                "type": 1,
                "api": url,
                "searchable": 1,
                "quickSearch": 1,
            })

    # 独立直播源
    for l in live_results:
        if not l["alive"]:
            continue
        lives.append({
            "name": f"live-{l['channels']}ch",
            "type": 0,
            "url": l["url"],
        })

    summary = {
        "vod_alive": sum(1 for v in vod_results if v["alive"]),
        "vod_total": len(vod_results),
        "live_alive": sum(1 for l in live_results if l["alive"]),
        "live_total": len(live_results),
        "agg_alive": sum(1 for a in agg_results if a["alive"]),
        "agg_total": len(agg_results),
        "sites": len(sites),
        "lives": len(lives),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "spider": "",
        "sites": sites,
        "lives": lives,
        "parses": [],
        "flags": [],
        "alive_summary": summary,
    }


def write(data: dict) -> None:
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[build_output] wrote {OUTPUT_JSON}")
    print(f"[build_output] summary: {json.dumps(data['alive_summary'], ensure_ascii=False)}")
