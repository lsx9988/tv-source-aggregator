"""直播源（M3U/M3U8）抓取与连通性检测。

检测逻辑：
  1. 下载 M3U 文件，验证 #EXTM3U 头
  2. 解析出条目（频道名 + 地址）
  3. 对前几个流地址做 HEAD/GET 探测，确认 Content-Type 或状态码可用
"""
from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urljoin

import httpx

from config import (
    CONCURRENCY,
    DEFAULT_HEADERS,
    LIVE_SEEDS,
    REQUEST_TIMEOUT,
    RETRY,
)


def load_seeds(path=LIVE_SEEDS) -> list[str]:
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def parse_m3u(text: str) -> list[dict[str, str]]:
    """解析 M3U，返回 [{name, url}] 列表。"""
    if not text.startswith("#EXTM3U"):
        return []
    items: list[dict[str, str]] = []
    name = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#EXTINF:"):
            # 提取逗号后的频道名
            name = line.split(",", 1)[-1].strip()
        elif line and not line.startswith("#"):
            items.append({"name": name or line, "url": line})
            name = ""
    return items


async def probe_stream(client: httpx.AsyncClient, url: str) -> bool:
    """探测单个流地址是否存活。"""
    try:
        async with client.stream("GET", url, timeout=REQUEST_TIMEOUT) as resp:
            ct = resp.headers.get("content-type", "")
            if resp.status_code == 200 and ("video" in ct or "application" in ct or "octet-stream" in ct or "mpegurl" in ct):
                return True
            # m3u8 常见 content-type: application/vnd.apple.mpegurl, application/x-mpegurl
            if resp.status_code == 200 and "mpegurl" in ct:
                return True
            if resp.status_code == 200:
                # 有些服务器不带 content-type，只要能开流就算活
                return True
        return False
    except httpx.HTTPError:
        return False


async def check_one(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    result = {"url": url, "alive": False, "kind": "live", "error": None, "channels": 0}
    for attempt in range(RETRY + 1):
        try:
            resp = await client.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                result["error"] = f"HTTP {resp.status_code}"
                continue
            text = resp.text
            items = parse_m3u(text)
            if not items:
                result["error"] = "not a valid m3u"
                continue
            result["channels"] = len(items)
            # 探测前 3 个流地址
            probes = [probe_stream(client, urljoin(url, it["url"])) for it in items[:3]]
            ok = await asyncio.gather(*probes)
            if any(ok):
                result["alive"] = True
                result["error"] = None
            else:
                result["error"] = "all sampled streams dead"
            return result
        except httpx.HTTPError as e:
            result["error"] = type(e).__name__
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
