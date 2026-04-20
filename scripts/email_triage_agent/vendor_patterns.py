from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urlparse


@dataclass(frozen=True)
class VendorPattern:
    vendor: str
    category: str  # dataroom|docs|cloud|marketplace|calendar|signature|other
    pattern: str
    auth_required: Optional[bool]

    def matches(self, url: str) -> bool:
        url_l = (url or "").lower()
        pat = (self.pattern or "").lower().strip()
        if not url_l or not pat:
            return False
        if "*." in pat:
            # "*.box.com" → endswith "box.com"
            suffix = pat.replace("*.", "")
            host = (urlparse(url_l).hostname or "").lower()
            return host.endswith(suffix)
        if "/" in pat:
            return pat in url_l
        host = (urlparse(url_l).hostname or "").lower()
        return host == pat or host.endswith(f".{pat}")


_BACKTICK_RE = re.compile(r"`([^`]+)`")


def _normalize_category(section_title: str) -> str:
    t = (section_title or "").strip().lower()
    if "dataroom" in t or "virtual data room" in t or "vdr" in t:
        return "dataroom"
    if "document sharing" in t:
        return "docs"
    if "cloud storage" in t:
        return "cloud"
    if "deal marketplaces" in t or "networks" in t:
        return "marketplace"
    if "calendar" in t or "scheduling" in t:
        return "calendar"
    if "e-signature" in t or "signature" in t:
        return "signature"
    return "other"


def load_vendor_patterns_md(path: str | Path) -> List[VendorPattern]:
    """
    Best-effort parser for the Agent Builder `vendor_patterns.md` reference file.

    We keep parsing intentionally tolerant: extract the domains inside backticks from each
    markdown table row and tag them by the surrounding section heading.
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")

    patterns: List[VendorPattern] = []
    current_section = ""
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue
        if not line.startswith("|"):
            continue
        # Skip header/separator rows.
        if "---" in line:
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 2:
            continue

        vendor = cols[0].replace("**", "").strip()
        urls_cell = cols[1]
        extracted = _BACKTICK_RE.findall(urls_cell)
        if not extracted:
            continue

        category = _normalize_category(current_section)
        # Auth rules are described in prose, but a few sections imply consistent defaults.
        auth_required: Optional[bool]
        if category in {"dataroom", "marketplace", "signature"}:
            auth_required = True
        elif category == "calendar":
            auth_required = False
        else:
            auth_required = None

        for pat in extracted:
            patterns.append(
                VendorPattern(
                    vendor=vendor or "unknown",
                    category=category,
                    pattern=pat.strip(),
                    auth_required=auth_required,
                )
            )

    return patterns


def classify_url_vendor(url: str, patterns: Iterable[VendorPattern]) -> Optional[VendorPattern]:
    for pat in patterns:
        try:
            if pat.matches(url):
                return pat
        except Exception:
            continue
    return None

