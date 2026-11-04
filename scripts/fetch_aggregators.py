"""TVBox 聚合配置接口检测。

聚合接口通常是一个 JSON，结构：
{
  "sites": [{"key": "py", "name": "华为", "type": 1, "api": "...", ...}, ...],
  "lives": [{"name": "点播", "type": 0, "url": "...m3u"}, ...],
  "parses": [...]
}
检测逻辑：
  1. 拉取 JSON
  2. 验证包含 sites / lives 字段
  3. 统计存活站点数
"""
from __future__ import annotations

import asyncio
from typing import Any

import httpx

from config import (
    AGG_REQUEST_TIMEOUT,
    AGG_SEEDS,
    CONCURRENCY,
    DEFAULT_HEADERS,
    RETRY,
)


def load_seeds(path=AGG_SEEDS) -> list[str]:
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


async def check_one(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    result = {
        "url": url,
        "alive": False,
        "kind": "aggregator",
        "error": None,
        "sites": 0,
        "lives": 0,
        "sites_data": [],
        "lives_data": [],
    }
    for attempt in range(RETRY + 1):
        try:
            resp = await client.get(url, timeout=AGG_REQUEST_TIMEOUT)
            if resp.status_code != 200:
                result["error"] = f"HTTP {resp.status_code}"
                continue
            data = resp.json()
            if not isinstance(data, dict):
                result["error"] = "json root not object"
                continue
            sites = data.get("sites") or []
            lives = data.get("lives") or []
            if not isinstance(sites, list) or not isinstance(lives, list):
                result["error"] = "sites/lives not list"
                continue
            result["sites"] = len(sites)
            result["lives"] = len(lives)
            result["sites_data"] = sites
            result["lives_data"] = lives
            if sites or lives:
                result["alive"] = True
                result["error"] = None
            else:
                result["error"] = "empty sites and lives"
            return result
        except httpx.HTTPError as e:
            result["error"] = type(e).__name__
        except ValueError:
            result["error"] = "not json"
        await asyncio.sleep(0.3)
    return result


async def check_all(urls: list[str]) -> list[dict[str, Any]]:
    if not urls:
        return []
    sem = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient(headers=DEFAULT_HEADERS, follow_redirects=True) as client:
        async def _wrap(u):
            async with sem:
                return await check_one(client, u)
        return await asyncio.gather(*[_wrap(u) for u in urls])


def run() -> list[dict[str, Any]]:
    return asyncio.run(check_all(load_seeds()))


if __name__ == "__main__":
    for r in run():
        print(r)
