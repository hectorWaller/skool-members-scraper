import argparse
import json
import logging
import os
from pathlib import Path
from typing import List, Dict

from utils.auth_handler import AuthHandler
from utils.export_manager import ExportManager
from services.scraper_engine import ScraperEngine
from services.proxy_manager import ProxyManager

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "input_urls.txt"
DEFAULT_CONFIG = ROOT / "src" / "config" / "settings.json"

def load_settings(path: Path) -> Dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def read_input_urls(path: Path) -> List[str]:
    if not path.exists():
        logging.warning("Input file not found at %s. Creating with an example URL.", path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("https://www.skool.com/some-group/members\n", encoding="utf-8")
    with path.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

def configure_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

def main():
    parser = argparse.ArgumentParser(description="Skool Members Scraper")
    parser.add_argument("--config", type=str, default=str(DEFAULT_CONFIG), help="Path to settings.json")
    parser.add_argument("--input", type=str, default=str(DEFAULT_INPUT), help="Path to input_urls.txt")
    args = parser.parse_args()

    settings = load_settings(Path(args.config))
    configure_logging(settings.get("log_level", "INFO"))
    logger = logging.getLogger("main")

    urls = read_input_urls(Path(args.input))
    if not urls:
        logger.error("No URLs provided in input file.")
        return

    # Auth & proxies
    auth = AuthHandler(
        cookie_string=os.getenv("SKOOL_COOKIES", settings.get("cookies", "")),
        user_agent=settings.get("user_agent"),
    )
    proxy_manager = ProxyManager(settings.get("proxies", []))

    engine = ScraperEngine(
        headers=auth.build_headers(),
        proxy_manager=proxy_manager,
        concurrency=int(settings.get("concurrency", 5)),
        retries=int(settings.get("retries", 2)),
        timeout=float(settings.get("timeout", 20)),
        delay=float(settings.get("delay_seconds", 0.5)),
    )

    all_records = engine.scrape(urls)

    # Export
    exporter = ExportManager()
    out_fmt = settings.get("output", {}).get("format", "json").lower()
    out_path = settings.get("output", {}).get("path", "data/output.json")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    if out_fmt == "json":
        exporter.to_json(all_records, out_path)
    elif out_fmt == "csv":
        exporter.to_csv(all_records, out_path)
    elif out_fmt in {"xlsx", "excel"}:
        exporter.to_xlsx(all_records, out_path)
    else:
        logger.warning("Unknown output format '%s', defaulting to JSON.", out_fmt)
        exporter.to_json(all_records, out_path)

    logger.info("Scraping complete. Wrote %d records to %s", len(all_records), out_path)

if __name__ == "__main__":
    main()