"""全局配置：超时、并发、输出路径、请求头。"""
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent
SOURCES_DIR = BASE_DIR / "sources"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 候选源文件
VOD_SEEDS = SOURCES_DIR / "vod_seeds.txt"
LIVE_SEEDS = SOURCES_DIR / "live_seeds.txt"
AGG_SEEDS = SOURCES_DIR / "aggregator_seeds.txt"

# 输出文件
OUTPUT_JSON = OUTPUT_DIR / "my_api.json"

# 网络配置
REQUEST_TIMEOUT = 8          # 单次请求超时（秒）
CONCURRENCY = 20             # 并发检测数
RETRY = 1                    # 失败重试次数

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "*/*",
}

# 点播源检测：请求 ac=list 验证
VOD_TEST_PARAMS = {"ac": "list"}

# 直播源检测：M3U 扩展名
LIVE_M3U_EXT = (".m3u", ".m3u8")

# 聚合接口超时（TVBox 配置可能较大）
AGG_REQUEST_TIMEOUT = 12
