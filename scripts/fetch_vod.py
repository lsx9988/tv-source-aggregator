"""点播源（CMS API）抓取与连通性检测。

检测逻辑：
  1. 拼接 ?ac=list 请求接口
  2. 验证返回 JSON 可解析
  3. 粗略检查是否包含常见字段（list / class / data）
"""
from __future__ import annotations

import asyncio
from typing import Any

import httpx

from config import (
    CONCURRENCY,
    DEFAULT_HEADERS,
    REQUEST_TIMEOUT,
    RETRY,
    VOD_SEEDS,
    VOD_TEST_PARAMS,
)


def load_seeds(path=VOD_SEEDS) -> list[str]:
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


async def check_one(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    """检测单个点播源，返回结果字典。"""
    result = {"url": url, "alive": False, "kind": "vod", "error": None, "title": None}
    test_url = url.rstrip("/")
    sep = "&" if "?" in test_url else "?"
    test_url = f"{test_url}{sep}ac=list"

    for attempt in range(RETRY + 1):
        try:
            resp = await client.get(test_url, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                result["error"] = f"HTTP {resp.status_code}"
                continue
            data = resp.json()
            # TVBox 点播常见返回结构：{"class": [...], "list": [...]} 或 {"code":1,"data":{...}}
            if isinstance(data, dict):
                if any(k in data for k in ("class", "list", "data", "result", "home")):
                    result["alive"] = True
                    result["title"] = data.get("site", {}).get("name") if isinstance(data.get("site"), dict) else None
                    result["error"] = None
                    return result
                result["error"] = "json missing known fields"
            else:
                result["error"] = "json root not object"
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
    urls = load_seeds()
    return asyncio.run(check_all(urls))


if __name__ == "__main__":
    for r in run():
        print(r)
