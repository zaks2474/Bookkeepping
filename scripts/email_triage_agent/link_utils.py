"""
Link normalization, classification, and deduplication utilities.

Handles:
- Tracking/click-wrapper URL detection
- Link type classification (tracking, unsubscribe, social, portal, etc.)
- Optional redirect resolution with caching
- Canonical key generation for deduplication
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse, urlunsplit

_log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Link Type Classification
# ─────────────────────────────────────────────────────────────────────────────

class LinkCategory:
    """Link category constants."""
    DEAL_MATERIAL = "deal_material"  # CIM, teaser, NDA, dataroom, financials
    TRACKING = "tracking"            # Click-wrapper/tracking URLs
    UNSUBSCRIBE = "unsubscribe"      # Unsubscribe/preferences links
    SOCIAL = "social"                # LinkedIn, Twitter, etc.
    PORTAL = "portal"                # Vendor portals, deal platforms
    CONTACT = "contact"              # mailto:, tel:, calendly, etc.
    OTHER = "other"                  # Unknown/uncategorized


# Known tracking/click-wrapper domains
# These domains wrap destination URLs with tracking parameters
TRACKING_DOMAINS = {
    # HubSpot
    "hubspotlinks.com",
    "hubspotlinksstarter.com",
    "hubspotstarter.net",
    "hs-sites.com",
    "track.hubspot.com",
    # Mailchimp
    "list-manage.com",
    "mailchi.mp",
    "click.mailchimp.com",
    "eepurl.com",
    # Constant Contact
    "constantcontact.com",
    "r20.constantcontact.com",
    # Sendgrid
    "sendgrid.net",
    "u1234567.ct.sendgrid.net",  # Pattern: u*.ct.sendgrid.net
    # Mailjet
    "mjt.lu",
    # Campaign Monitor
    "cmail19.com",
    "cmail20.com",
    "createsend.com",
    # Salesforce/Pardot
    "pardot.com",
    "pardot-email.com",
    "go.pardot.com",
    # Marketo
    "mktossl.com",
    "mkt2.com",
    "mkt1.com",
    # ActiveCampaign
    "activehosted.com",
    "lt.aceapp.io",
    # Other common
    "trk.klclick.com",
    "links.email.gov",
    "links.govdelivery.com",
    "url.emailprotection.link",
    "safelinks.protection.outlook.com",
}

# Patterns for tracking domains that use subdomains
TRACKING_DOMAIN_PATTERNS = [
    re.compile(r"^[a-z0-9]+\.na\d*\.hubspotlinks", re.IGNORECASE),  # *.na1.hubspotlinks*
    re.compile(r"^[a-z0-9]+\.ct\.sendgrid\.net$", re.IGNORECASE),   # *.ct.sendgrid.net
    re.compile(r"^t\d*\.mail\.hubspot\.net$", re.IGNORECASE),       # t*.mail.hubspot.net
    re.compile(r"^click\.", re.IGNORECASE),                          # click.*
    re.compile(r"^trk\.", re.IGNORECASE),                            # trk.*
    re.compile(r"^track\.", re.IGNORECASE),                          # track.*
    re.compile(r"^links\.", re.IGNORECASE),                          # links.*
    re.compile(r"^r\d+\.", re.IGNORECASE),                           # r20.*, r19.*
]

# Known unsubscribe/preferences URL patterns
UNSUBSCRIBE_PATTERNS = [
    re.compile(r"\bunsubscribe\b", re.IGNORECASE),
    re.compile(r"\bpreferences?\b", re.IGNORECASE),
    re.compile(r"\bopt[_-]?out\b", re.IGNORECASE),
    re.compile(r"\bmanage[_-]?subscriptions?\b", re.IGNORECASE),
    re.compile(r"/hs/manage-preferences/", re.IGNORECASE),
]

# Known social media domains
SOCIAL_DOMAINS = {
    "linkedin.com",
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "tiktok.com",
    "pinterest.com",
    "github.com",
}

# Contact-related domains
CONTACT_DOMAINS = {
    "calendly.com",
    "acuityscheduling.com",
    "calendarhero.com",
    "doodle.com",
    "meetingbird.com",
    "cal.com",
    "savvycal.com",
}


@dataclass
class ClassifiedLink:
    """A link with classification and normalization metadata."""
    original_url: str
    safe_url: str              # URL with query/fragment stripped
    category: str              # LinkCategory value
    resolved_url: Optional[str] = None  # Destination URL if tracking was resolved
    canonical_key: str = ""    # Key for deduplication
    auth_required: bool = False
    vendor_hint: Optional[str] = None
    link_type: str = "other"   # Original link type (nda, cim, etc.)
    source_context: Optional[str] = None  # For debugging
    # Meaning labels (Phase 4 enhancement)
    meaning_label: Optional[str] = None  # Human-readable label (e.g., "NDA Document", "Data Room")
    doc_type: Optional[str] = None  # Document type hint (nda, cim, teaser, financials, etc.)
    confidence: float = 0.0  # Confidence in classification (0-1)


# Meaning label patterns for heuristic classification
MEANING_LABEL_PATTERNS = {
    # Data rooms
    r"(dataroom|data-room|dealroom|deal-room|vdr)": ("Data Room", "dataroom", 0.9),
    r"(box\.com|sharefile|dropbox\.com|onedrive|drive\.google)": ("File Share", "fileshare", 0.7),
    # NDA
    r"(nda|non-disclosure|confidential|agreement)": ("NDA / Agreement", "nda", 0.8),
    r"(docusign|hellosign|pandadoc).*sign": ("Document Signing", "esign", 0.8),
    # CIM/Teaser
    r"(cim|confidential.*information.*memorandum|teaser|executive.*summary)": ("CIM / Teaser", "cim", 0.8),
    # Financials
    r"(financials|p&l|balance.*sheet|income.*statement|cash.*flow)": ("Financial Document", "financials", 0.8),
    # Calendar
    r"(calendly|cal\.com|schedule|book.*meeting|appointment)": ("Schedule Meeting", "calendar", 0.9),
    # Portal/Login
    r"(portal|login|signin|sign-in|dashboard|account)": ("Portal / Login", "portal", 0.7),
    # Contact
    r"^mailto:": ("Email Contact", "email", 0.95),
    r"^tel:": ("Phone Contact", "phone", 0.95),
    # Unsubscribe
    r"(unsubscribe|opt-out|preferences|manage.*subscription)": ("Unsubscribe", "unsubscribe", 0.9),
}


def _infer_meaning_label(url: str, link_type: str = "other") -> Tuple[Optional[str], Optional[str], float]:
    """
    Infer a human-readable meaning label for a link.

    Returns: (meaning_label, doc_type, confidence)
    """
    import re

    url_lower = url.lower()

    # First check if link_type gives us a hint
    if link_type in ("nda", "non-disclosure"):
        return ("NDA / Agreement", "nda", 0.9)
    elif link_type in ("cim", "teaser"):
        return ("CIM / Teaser", "cim", 0.9)
    elif link_type in ("dataroom", "data_room"):
        return ("Data Room", "dataroom", 0.9)
    elif link_type in ("calendar", "schedule"):
        return ("Schedule Meeting", "calendar", 0.9)

    # Check patterns
    for pattern, (label, doc_type, confidence) in MEANING_LABEL_PATTERNS.items():
        if re.search(pattern, url_lower):
            return (label, doc_type, confidence)

    # Default based on domain
    domain = _extract_domain(url)
    if domain:
        if any(d in domain for d in ("axial", "dealnexus", "bizbuysell", "businessforsale")):
            return ("Business Listing", "listing", 0.7)
        if any(d in domain for d in ("linkedin", "twitter", "facebook")):
            return ("Social Media", "social", 0.8)

    return (None, None, 0.0)


def safe_url(url: str) -> str:
    """Strip query/fragment to avoid persisting access tokens."""
    try:
        parts = urlparse(url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    except Exception:
        return (url or "").split("?", 1)[0].split("#", 1)[0]


def _extract_domain(url: str) -> str:
    """Extract the domain from a URL."""
    try:
        parsed = urlparse(url)
        return (parsed.hostname or "").lower()
    except Exception:
        return ""


def _is_tracking_domain(domain: str) -> bool:
    """Check if a domain is a known tracking/click-wrapper service."""
    if not domain:
        return False

    # Direct match
    for td in TRACKING_DOMAINS:
        if domain == td or domain.endswith("." + td):
            return True

    # Pattern match
    for pattern in TRACKING_DOMAIN_PATTERNS:
        if pattern.match(domain):
            return True

    return False


def _is_unsubscribe_url(url: str) -> bool:
    """Check if URL is an unsubscribe/preferences link."""
    url_lower = url.lower()
    for pattern in UNSUBSCRIBE_PATTERNS:
        if pattern.search(url_lower):
            return True
    return False


def _is_social_url(url: str) -> bool:
    """Check if URL is a social media link."""
    domain = _extract_domain(url)
    for sd in SOCIAL_DOMAINS:
        if domain == sd or domain.endswith("." + sd):
            return True
    return False


def _is_contact_url(url: str) -> bool:
    """Check if URL is a contact/scheduling link."""
    url_lower = url.lower()
    if url_lower.startswith("mailto:") or url_lower.startswith("tel:"):
        return True

    domain = _extract_domain(url)
    for cd in CONTACT_DOMAINS:
        if domain == cd or domain.endswith("." + cd):
            return True
    return False


def classify_link(url: str, context: str = "") -> str:
    """
    Classify a link into a category.

    Args:
        url: The URL to classify
        context: Optional surrounding text for classification hints

    Returns:
        One of LinkCategory values
    """
    if not url:
        return LinkCategory.OTHER

    domain = _extract_domain(url)

    # Check tracking first (most common case for duplicates)
    if _is_tracking_domain(domain):
        return LinkCategory.TRACKING

    # Check unsubscribe (even non-tracking domains can have these)
    if _is_unsubscribe_url(url):
        return LinkCategory.UNSUBSCRIBE

    # Check social
    if _is_social_url(url):
        return LinkCategory.SOCIAL

    # Check contact
    if _is_contact_url(url):
        return LinkCategory.CONTACT

    return LinkCategory.OTHER


# ─────────────────────────────────────────────────────────────────────────────
# Redirect Resolution (with caching)
# ─────────────────────────────────────────────────────────────────────────────

class RedirectResolver:
    """
    Resolve click-wrapper URLs to their destination.

    Uses HEAD requests with strict limits to avoid abuse.
    Results are cached locally to avoid repeated network calls.
    """

    DEFAULT_CACHE_PATH = Path.home() / ".cache" / "link_redirect_cache.json"
    DEFAULT_TIMEOUT = 5
    DEFAULT_MAX_REDIRECTS = 5
    CACHE_TTL_SECONDS = 86400 * 7  # 7 days

    def __init__(
        self,
        cache_path: Optional[Path] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_redirects: int = DEFAULT_MAX_REDIRECTS,
    ):
        self.cache_path = cache_path or self.DEFAULT_CACHE_PATH
        self.timeout = timeout
        self.max_redirects = max_redirects
        self._cache: Dict[str, Tuple[str, float]] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cache from disk."""
        try:
            if self.cache_path.exists():
                data = json.loads(self.cache_path.read_text())
                now = time.time()
                # Filter out expired entries
                self._cache = {
                    k: (v[0], v[1])
                    for k, v in data.items()
                    if now - v[1] < self.CACHE_TTL_SECONDS
                }
        except Exception as e:
            _log.debug(f"Failed to load redirect cache: {e}")
            self._cache = {}

    def _save_cache(self) -> None:
        """Save cache to disk."""
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps(self._cache))
        except Exception as e:
            _log.debug(f"Failed to save redirect cache: {e}")

    def resolve(self, url: str) -> Optional[str]:
        """
        Resolve a tracking URL to its destination.

        Returns None if resolution fails or URL is not a tracking URL.
        """
        domain = _extract_domain(url)
        if not _is_tracking_domain(domain):
            return None

        # Check cache
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key][0]

        # Try to resolve
        resolved = self._do_resolve(url)
        if resolved and resolved != url:
            self._cache[cache_key] = (resolved, time.time())
            self._save_cache()
            return resolved

        return None

    def _do_resolve(self, url: str) -> Optional[str]:
        """Actually perform the redirect resolution."""
        try:
            import urllib.request
            import ssl

            # Create opener that doesn't follow redirects automatically
            class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, headers, newurl):
                    return None  # Don't follow redirects automatically

            opener = urllib.request.build_opener(NoRedirectHandler())

            current_url = url
            for _ in range(self.max_redirects):
                try:
                    req = urllib.request.Request(
                        current_url,
                        method="HEAD",
                        headers={"User-Agent": "ZakOps-LinkResolver/1.0"},
                    )
                    # Use default SSL context
                    ctx = ssl.create_default_context()
                    resp = opener.open(req, timeout=self.timeout, context=ctx)
                    # No more redirects, return current URL
                    return current_url
                except urllib.error.HTTPError as e:
                    if e.code in (301, 302, 303, 307, 308):
                        new_url = e.headers.get("Location")
                        if new_url:
                            # Handle relative URLs
                            if new_url.startswith("/"):
                                parsed = urlparse(current_url)
                                new_url = f"{parsed.scheme}://{parsed.netloc}{new_url}"
                            current_url = new_url
                            continue
                    return None
                except Exception:
                    return None

            return current_url
        except Exception as e:
            _log.debug(f"Failed to resolve redirect for {url}: {e}")
            return None


# ─────────────────────────────────────────────────────────────────────────────
# Deduplication
# ─────────────────────────────────────────────────────────────────────────────

def generate_canonical_key(
    url: str,
    resolved_url: Optional[str] = None,
    link_type: str = "other",
    auth_required: bool = False,
) -> str:
    """
    Generate a canonical key for deduplication.

    Two links with the same canonical key are considered duplicates.
    """
    # Use resolved URL if available, otherwise original
    effective_url = resolved_url or url
    effective_url = safe_url(effective_url)

    # Create a key that includes type and auth requirement
    key_parts = [effective_url.lower(), link_type, str(auth_required)]
    return "|".join(key_parts)


def deduplicate_links(
    links: List[ClassifiedLink],
    *,
    prefer_resolved: bool = True,
) -> List[ClassifiedLink]:
    """
    Deduplicate links by canonical key.

    When duplicates are found, keeps the first occurrence.
    If prefer_resolved is True and a resolved URL is available,
    that version is preferred.

    Args:
        links: List of classified links
        prefer_resolved: Whether to prefer resolved URLs over tracking URLs

    Returns:
        Deduplicated list of links
    """
    seen_keys: Set[str] = set()
    result: List[ClassifiedLink] = []

    for link in links:
        if link.canonical_key in seen_keys:
            continue
        seen_keys.add(link.canonical_key)
        result.append(link)

    return result


def classify_and_dedupe_links(
    urls: List[str],
    *,
    resolve_redirects: bool = False,
    resolver: Optional[RedirectResolver] = None,
    context: str = "",
) -> Tuple[List[ClassifiedLink], Dict[str, List[ClassifiedLink]]]:
    """
    Classify, normalize, and deduplicate a list of URLs.

    Args:
        urls: List of URLs to process
        resolve_redirects: Whether to resolve tracking URL redirects
        resolver: Optional resolver instance (created if needed)
        context: Optional context text for classification

    Returns:
        Tuple of:
        - Deduplicated list of non-tracking links
        - Dictionary of categorized links (tracking, unsubscribe, social)
    """
    if resolve_redirects and resolver is None:
        resolver = RedirectResolver()

    classified: List[ClassifiedLink] = []

    for url in urls:
        category = classify_link(url, context)
        resolved = None

        if resolve_redirects and category == LinkCategory.TRACKING and resolver:
            resolved = resolver.resolve(url)

        # Infer meaning label for non-tracking links
        meaning_label, doc_type, confidence = (None, None, 0.0)
        if category != LinkCategory.TRACKING:
            meaning_label, doc_type, confidence = _infer_meaning_label(url)

        link = ClassifiedLink(
            original_url=url,
            safe_url=safe_url(url),
            category=category,
            resolved_url=resolved,
            canonical_key=generate_canonical_key(url, resolved),
            meaning_label=meaning_label,
            doc_type=doc_type,
            confidence=confidence,
        )
        classified.append(link)

    # Group by category
    by_category: Dict[str, List[ClassifiedLink]] = {}
    for link in classified:
        if link.category not in by_category:
            by_category[link.category] = []
        by_category[link.category].append(link)

    # Deduplicate each category
    for cat in by_category:
        by_category[cat] = deduplicate_links(by_category[cat])

    # Return non-tracking links as the primary list
    primary = []
    for cat in [LinkCategory.DEAL_MATERIAL, LinkCategory.PORTAL, LinkCategory.OTHER]:
        primary.extend(by_category.get(cat, []))

    return deduplicate_links(primary), by_category


# ─────────────────────────────────────────────────────────────────────────────
# Integration helpers
# ─────────────────────────────────────────────────────────────────────────────

def filter_tracking_urls(urls: List[str]) -> Tuple[List[str], List[str]]:
    """
    Separate tracking URLs from regular URLs.

    Returns:
        Tuple of (non_tracking_urls, tracking_urls)
    """
    non_tracking = []
    tracking = []

    for url in urls:
        if _is_tracking_domain(_extract_domain(url)):
            tracking.append(url)
        else:
            non_tracking.append(url)

    return non_tracking, tracking


def count_links_by_category(links: List[ClassifiedLink]) -> Dict[str, int]:
    """Count links by category."""
    counts: Dict[str, int] = {}
    for link in links:
        counts[link.category] = counts.get(link.category, 0) + 1
    return counts


# ─────────────────────────────────────────────────────────────────────────────
# CLI for backfilling existing bundles
# ─────────────────────────────────────────────────────────────────────────────

def backfill_links(
    root_dir: Path,
    *,
    overwrite: bool = False,
    dry_run: bool = False,
) -> Dict[str, int]:
    """
    Backfill classified_links.json for existing deal bundles.

    Finds all links.json files under root_dir and creates/updates
    classified_links.json with properly categorized and deduped links.

    Args:
        root_dir: Root directory to search (e.g., DataRoom/00-PIPELINE/Inbound)
        overwrite: If True, overwrite existing classified_links.json files
        dry_run: If True, only print what would be done without writing

    Returns:
        Dict with counts: processed, skipped, errors
    """
    stats = {"processed": 0, "skipped": 0, "errors": 0, "created": 0}

    # Find all links.json files
    for links_path in root_dir.rglob("links.json"):
        classified_path = links_path.parent / "classified_links.json"

        # Skip if classified already exists and not overwriting
        if classified_path.exists() and not overwrite:
            _log.debug(f"Skipping {links_path} (classified_links.json exists)")
            stats["skipped"] += 1
            continue

        try:
            # Read raw links
            raw_data = json.loads(links_path.read_text(encoding="utf-8"))
            if not isinstance(raw_data, dict):
                raw_data = {"links": []}
            raw_links = raw_data.get("links", [])
            if not isinstance(raw_links, list):
                raw_links = []

            # Classify and dedupe
            primary, by_category = classify_and_dedupe_links(
                [l.get("url", "") for l in raw_links if isinstance(l, dict) and l.get("url")]
            )

            # Build classified structure
            classified_data = {
                "deal_id": raw_data.get("deal_id"),
                "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "links": [
                    {
                        "url": l.safe_url,
                        "category": l.category,
                        "canonical_key": l.canonical_key,
                        "original_url": l.original_url,
                    }
                    for l in primary
                ],
                "summary": {
                    "material_count": len(primary),
                    "tracking_count": len(by_category.get(LinkCategory.TRACKING, [])),
                    "unsubscribe_count": len(by_category.get(LinkCategory.UNSUBSCRIBE, [])),
                    "social_count": len(by_category.get(LinkCategory.SOCIAL, [])),
                    "contact_count": len(by_category.get(LinkCategory.CONTACT, [])),
                    "total_raw": len(raw_links),
                },
                "_tracking_links": [
                    {"url": l.safe_url, "original_url": l.original_url}
                    for l in by_category.get(LinkCategory.TRACKING, [])
                ],
                "_unsubscribe_links": [
                    {"url": l.safe_url, "original_url": l.original_url}
                    for l in by_category.get(LinkCategory.UNSUBSCRIBE, [])
                ],
                "_social_links": [
                    {"url": l.safe_url, "original_url": l.original_url}
                    for l in by_category.get(LinkCategory.SOCIAL, [])
                ],
                "_all_links_raw": raw_links,
            }

            if dry_run:
                print(f"[DRY RUN] Would create {classified_path}")
                print(f"  Primary: {len(primary)}, Tracking: {len(by_category.get(LinkCategory.TRACKING, []))}")
            else:
                classified_path.write_text(
                    json.dumps(classified_data, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                _log.info(f"Created {classified_path}")

            stats["processed"] += 1
            stats["created"] += 1

        except Exception as e:
            _log.error(f"Error processing {links_path}: {e}")
            stats["errors"] += 1

    return stats


def main():
    """CLI entry point for link_utils."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m email_triage_agent.link_utils",
        description="Link normalization and classification utilities",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # backfill command
    backfill_parser = subparsers.add_parser(
        "backfill",
        help="Backfill classified_links.json for existing deal bundles",
    )
    backfill_parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Root directory to search for links.json files",
    )
    backfill_parser.add_argument(
        "--overwrite-links",
        action="store_true",
        help="Overwrite existing classified_links.json files",
    )
    backfill_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without writing files",
    )

    args = parser.parse_args()

    if args.command == "backfill":
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

        if not args.root.exists():
            print(f"Error: Root directory does not exist: {args.root}")
            return 1

        print(f"Backfilling classified links in {args.root}...")
        stats = backfill_links(
            args.root,
            overwrite=args.overwrite_links,
            dry_run=args.dry_run,
        )

        print(f"\nResults:")
        print(f"  Processed: {stats['processed']}")
        print(f"  Created:   {stats['created']}")
        print(f"  Skipped:   {stats['skipped']}")
        print(f"  Errors:    {stats['errors']}")
        return 0 if stats["errors"] == 0 else 1

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
