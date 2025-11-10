import sys
from pathlib import Path

# Ensure src/ is importable
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.append(str(SRC))

from utils.parser import Parser  # noqa: E402

def test_parser_extracts_members_from_script_tag():
    html = """
    <html>
      <head>
        <script id="__SKOOL_DATA__" type="application/json">
        {
          "members": [
            {
              "id": "4a24",
              "name": "Justa Virviciu",
              "email": "",
              "metadata": {
                "bio": "Entrepreneur",
                "linkFacebook": "omitted",
                "linkInstagram": "omitted",
                "linkLinkedin": "omitted",
                "linkTwitter": "omitted",
                "linkWebsite": "omitted",
                "linkYoutube": "omitted",
                "location": "",
                "pictureProfile": "https://assets.skool.com/avatar.jpg"
              },
              "member": {
                "role": "member",
                "createdAt": "2024-06-02T08:59:10.117196Z",
                "lastOffline": "2024-06-02T15:30:21.394724Z"
              }
            }
          ]
        }
        </script>
      </head>
      <body></body>
    </html>
    """
    members = Parser.parse_members(html)
    assert isinstance(members, list)
    assert len(members) == 1
    m = members[0]
    assert m["id"] == "4a24"
    assert m["metadata"]["bio"] == "Entrepreneur"
    assert m["member"]["role"] == "member"

def test_parser_returns_empty_when_no_data():
    html = "<html><head></head><body>No JSON here</body></html>"
    members = Parser.parse_members(html)
    assert members == []