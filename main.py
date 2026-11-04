"""主入口：依次检测点播、直播、聚合源，输出聚合 JSON。"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# 让 scripts/ 可作为包导入
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scripts import fetch_vod, fetch_live, fetch_aggregators, build_output


def main() -> int:
    print("=== [1/4] 检测点播源 ===")
    vod = fetch_vod.run()
    for v in vod:
        print(f"  {'OK ' if v['alive'] else 'DEAD'} {v['url']}  {v.get('error') or ''}")

    print("=== [2/4] 检测直播源 ===")
    live = fetch_live.run()
    for l in live:
        print(f"  {'OK ' if l['alive'] else 'DEAD'} {l['url']}  ch={l.get('channels',0)} {l.get('error') or ''}")

    print("=== [3/4] 检测聚合接口 ===")
    agg = fetch_aggregators.run()
    for a in agg:
        print(f"  {'OK ' if a['alive'] else 'DEAD'} {a['url']}  sites={a.get('sites',0)} lives={a.get('lives',0)} {a.get('error') or ''}")

    print("=== [4/4] 构建输出 ===")
    data = build_output.build(vod, live, agg)
    build_output.write(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
