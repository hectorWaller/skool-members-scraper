from typing import Dict, Optional

class AuthHandler:
    """
    Handles cookie-based auth for Skool.com scraping.
    Accepts a raw cookie string (e.g., "sid=...; other=...") and builds a headers dict.
    """

    def __init__(self, cookie_string: str = "", user_agent: Optional[str] = None):
        self.cookie_string = (cookie_string or "").strip()
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    def build_headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
        if self.cookie_string:
            headers["Cookie"] = self.cookie_string
        return headers