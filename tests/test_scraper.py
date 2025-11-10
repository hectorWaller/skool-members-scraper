import json
import sys
from pathlib import Path

import pytest

# Ensure src/ is importable
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

from services.scraper_engine import ScraperEngine  # noqa: E402
from services.proxy_manager import ProxyManager  # noqa: E402

MOCK_HTML = """
<html><head>
<script id="__SKOOL_DATA__" type="application/json">
{
  "members": [
    {
      "id": "abc123",
      "name": "Jane Doe",
      "email": "jane@example.com",
      "metadata": {
        "bio": "Builder",
        "linkFacebook": "",
        "linkInstagram": "",
        "linkLinkedin": "",
        "linkTwitter": "",
        "linkWebsite": "",
        "linkYoutube": "",
        "location": "Earth",
        "pictureProfile": "https://cdn/pic.jpg"
      },
      "member": {
        "role": "member",
        "createdAt": "2024-01-01T00:00:00Z",
        "lastOffline": "2024-01-02T00:00:00Z"
      }
    }
  ]
}
</script>
</head><body></body></html>
"""

class DummyEngine(ScraperEngine):
    def _fetch(self, url: str) -> str:  # override network
        return MOCK_HTML

def test_scrape_pipeline(tmp_path):
    engine = DummyEngine(
        headers={"User-Agent": "pytest"},
        proxy_manager=ProxyManager([]),
        concurrency=2,
        retries=0,
        timeout=5,
        delay=0.0,
    )
    urls = ["https://skool.test/group1/members", "https://skool.test/group2/members"]
    records = engine.scrape(urls)
    assert len(records) == 2  # one per URL, same parsed content
    assert all(r["id"] == "abc123" for r in records)
    assert all(r["_source_url"] in urls for r in records)

    # Ensure JSON-serializable
    json.dumps(records)