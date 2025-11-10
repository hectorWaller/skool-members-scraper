import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

import requests

from utils.parser import Parser
from .proxy_manager import ProxyManager

class ScraperEngine:
    """
    Coordinates fetching and parsing of Skool group member pages.
    """

    def __init__(
        self,
        headers: Optional[Dict[str, str]],
        proxy_manager: ProxyManager,
        concurrency: int = 5,
        retries: int = 2,
        timeout: float = 20.0,
        delay: float = 0.5,
    ):
        self.headers = headers or {}
        self.proxy_manager = proxy_manager
        self.concurrency = max(1, int(concurrency))
        self.retries = max(0, int(retries))
        self.timeout = float(timeout)
        self.delay = float(delay)
        self.logger = logging.getLogger(self.__class__.__name__)

    def _fetch(self, url: str) -> str:
        last_exc = None
        for attempt in range(self.retries + 1):
            try:
                proxies = self.proxy_manager.get_requests_proxies()
                resp = requests.get(url, headers=self.headers, proxies=proxies, timeout=self.timeout)
                if resp.status_code >= 400:
                    raise requests.HTTPError(f"HTTP {resp.status_code}")
                return resp.text
            except Exception as e:  # noqa: BLE001
                last_exc = e
                self.logger.warning("Fetch attempt %d failed for %s: %s", attempt + 1, url, e)
                time.sleep(min(2 ** attempt * 0.5, 3))
        raise RuntimeError(f"Failed to fetch {url}: {last_exc}")

    def _process_url(self, url: str) -> List[Dict[str, Any]]:
        html = self._fetch(url)
        parsed = Parser.parse_members(html)
        for record in parsed:
            record["_source_url"] = url
        return parsed

    def scrape(self, urls: List[str]) -> List[Dict[str, Any]]:
        all_records: List[Dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            futures = {executor.submit(self._process_url, u): u for u in urls}
            for fut in as_completed(futures):
                url = futures[fut]
                try:
                    records = fut.result()
                    all_records.extend(records)
                    self.logger.info("Parsed %d records from %s", len(records), url)
                except Exception as e:  # noqa: BLE001
                    self.logger.error("Failed processing %s: %s", url, e)
                time.sleep(self.delay)
        return all_records