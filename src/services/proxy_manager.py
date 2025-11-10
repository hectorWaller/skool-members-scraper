import itertools
from typing import Dict, List, Optional

class ProxyManager:
    """
    Rotates through a list of proxies (HTTP/HTTPS).
    Proxies can be provided as full URLs: http://user:pass@host:port or https://host:port
    """

    def __init__(self, proxies: Optional[List[str]] = None):
        self._proxies = [p for p in (proxies or []) if p]
        self._cycle = itertools.cycle(self._proxies) if self._proxies else None

    def next_proxy(self) -> Optional[str]:
        if not self._cycle:
            return None
        return next(self._cycle)

    def get_requests_proxies(self) -> Optional[Dict[str, str]]:
        proxy = self.next_proxy()
        if not proxy:
            return None
        return {"http": proxy, "https": proxy}