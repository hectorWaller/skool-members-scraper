import json
from typing import List, Dict, Any
from bs4 import BeautifulSoup

class Parser:
    """
    Parses Skool member data out of HTML.
    Strategy:
      1) Look for a script tag with id="__SKOOL_DATA__" containing JSON with 'members' array.
      2) Fallback: try to locate any <script type="application/json"> whose JSON contains 'members'.
    Returns a list of normalized member dicts.
    """

    @staticmethod
    def _normalize_member(raw: Dict[str, Any]) -> Dict[str, Any]:
        metadata = raw.get("metadata", {}) or {}
        member = raw.get("member", {}) or {}

        return {
            "id": raw.get("id") or raw.get("uid") or "",
            "name": raw.get("name") or f"{raw.get('firstName','')} {raw.get('lastName','')}".strip(),
            "email": raw.get("email", "") or metadata.get("email", ""),
            "metadata": {
                "bio": metadata.get("bio", ""),
                "linkFacebook": metadata.get("linkFacebook", ""),
                "linkInstagram": metadata.get("linkInstagram", ""),
                "linkLinkedin": metadata.get("linkLinkedin", ""),
                "linkTwitter": metadata.get("linkTwitter", ""),
                "linkWebsite": metadata.get("linkWebsite", ""),
                "linkYoutube": metadata.get("linkYoutube", ""),
                "location": metadata.get("location", ""),
                "pictureProfile": metadata.get("pictureProfile", ""),
            },
            "member": {
                "role": member.get("role", ""),
                "createdAt": member.get("createdAt", ""),
                "lastOffline": member.get("lastOffline", ""),
            },
        }

    @classmethod
    def parse_members(cls, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")

        # Try exact script id first
        script = soup.find("script", id="__SKOOL_DATA__")
        if script and script.string:
            try:
                payload = json.loads(script.string)
                members = payload.get("members") or payload.get("data", {}).get("members") or []
                return [cls._normalize_member(m) for m in members if isinstance(m, dict)]
            except json.JSONDecodeError:
                pass

        # Fallback: any application/json script containing 'members'
        for sc in soup.find_all("script", type="application/json"):
            if not sc.string:
                continue
            try:
                payload = json.loads(sc.string)
            except json.JSONDecodeError:
                continue
            members = None
            if isinstance(payload, dict):
                if "members" in payload and isinstance(payload["members"], list):
                    members = payload["members"]
                elif "data" in payload and isinstance(payload["data"], dict) and isinstance(
                    payload["data"].get("members"), list
                ):
                    members = payload["data"]["members"]
            if members is not None:
                return [cls._normalize_member(m) for m in members if isinstance(m, dict)]

        # If nothing found, return empty list
        return []