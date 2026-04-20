from __future__ import annotations

import hashlib
import html as html_lib
import logging
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable, List, Optional, Sequence, Set, Tuple

_log = logging.getLogger(__name__)

from email_triage_agent.gmail_mcp import EmailAttachment, EmailMessage
from email_triage_agent.vendor_patterns import VendorPattern, classify_url_vendor
from email_triage_agent.link_utils import filter_tracking_urls, classify_link, LinkCategory


_URL_RE = re.compile(r'https?://[^\s<>\"]+')
_EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")

# Word boundary pattern helper - matches whole words only
def _word_match(text: str, keywords: Iterable[str]) -> List[str]:
    """Match keywords as whole words (not substrings) using word boundaries."""
    text_lower = (text or "").lower()
    hits = []
    for kw in keywords:
        # Build pattern with word boundaries for short keywords, looser for phrases
        if " " in kw:
            # For multi-word phrases, just check if phrase exists
            if kw in text_lower:
                hits.append(kw)
        else:
            # For single words, use word boundaries to avoid false positives
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, text_lower):
                hits.append(kw)
    return hits

# Sender domains that are NEVER deal-related (marketing/retail/consumer services)
_SENDER_DOMAIN_DENYLIST = {
    # Retail/Commerce
    "nordstrom.com", "eml.nordstrom.com", "express.com", "b.express.com",
    "costco.com", "amazon.com", "walmart.com", "target.com", "bestbuy.com",
    "macys.com", "kohls.com", "jcpenney.com", "gap.com", "oldnavy.com",
    # Telecom/Tech marketing
    "mintmobile.com", "email.mintmobile.com", "t-mobile.com", "verizon.com", "att.com",
    "microsoftstore.microsoft.com", "store.apple.com", "email.apple.com",
    # Financial marketing (not deal-related)
    "news.paypal.com", "email.chase.com", "email.wellsfargo.com", "email.capitalone.com",
    # Real estate/Consumer services (not M&A deal-related)
    "mail.realtor.com", "e.mail.realtor.com", "zillow.com", "redfin.com", "trulia.com",
    # Social/Dating/Community notifications
    "jigsaw.co", "tinder.com", "bumble.com", "hinge.com", "match.com",
    "notification.circle.so", "email.notification.circle.so",
    # General newsletters
    "substack.com", "mailchimp.com", "constantcontact.com", "sendinblue.com",
    "newsletter.thelegalwire.ai",  # Legal industry newsletter
    # Software/SaaS marketing (receipts, not deals)
    "anthropic.com", "openai.com",
    "bitdefender.com", "info.bitdefender.com",  # Security software
    "notion.so", "slack.com", "github.com", "atlassian.com",  # Dev tools marketing
}


@dataclass(frozen=True)
class LinkEntity:
    type: str  # cim|teaser|dataroom|nda|financials|calendar|docs|other
    url: str
    auth_required: bool
    vendor_hint: Optional[str]


@dataclass(frozen=True)
class TriageClassification:
    classification: str  # DEAL_SIGNAL|OPERATIONAL|NEWSLETTER|SPAM
    urgency: str  # LOW|MED|HIGH
    reason: str


@dataclass(frozen=True)
class TriageDecision:
    classification: TriageClassification
    sender_email: Optional[str]
    company: Optional[str]
    links: List[LinkEntity]
    attachments: List[EmailAttachment]
    labels_to_add: List[str]
    needs_reply: bool
    needs_docs: bool
    quarantine: bool
    eligible_for_llm: bool
    body_fingerprint: str


def sha256_text(text: str) -> str:
    h = hashlib.sha256()
    h.update((text or "").encode("utf-8", errors="replace"))
    return h.hexdigest()


@dataclass(frozen=True)
class NormalizedEmailBody:
    clean_text: str
    clean_text_no_urls: str
    urls: List[str]
    fingerprint: str


_HTML_TAG_RE = re.compile(r"(?s)<[^>]+>")
_HTML_SCRIPT_STYLE_RE = re.compile(r"(?is)<(script|style).*?>.*?</\1>")
_HTML_BR_RE = re.compile(r"(?i)<br\s*/?>")
_HTML_BLOCK_END_RE = re.compile(r"(?i)</(p|div|tr|li|h\d)>")
_WS_RE = re.compile(r"[\t \f\v]+")
_MULTI_NL_RE = re.compile(r"\n{3,}")
_QUOTED_LINE_RE = re.compile(r"(?m)^\s*>.*$")
_REPLY_CUT_MARKERS = [
    re.compile(r"(?im)^\s*-----\s*original message\s*-----\s*$"),
    re.compile(r"(?im)^\s*on\s.+\bwrote:\s*$"),
    re.compile(r"(?im)^\s*from:\s.+$"),
]


def _looks_like_html(text: str) -> bool:
    t = (text or "").lower()
    return "<html" in t or "<body" in t or bool(re.search(r"</\\w+>", t))


class _TextExtractor(HTMLParser):
    """P2: HTMLParser-based text extractor - more robust than regex for nested/malformed HTML."""

    def __init__(self):
        super().__init__()
        self.text_chunks: List[str] = []
        self._skip_data = False

    def handle_starttag(self, tag: str, attrs) -> None:
        tag_lower = tag.lower()
        if tag_lower in ("script", "style", "head"):
            self._skip_data = True
        elif tag_lower in ("br", "p", "div", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6"):
            self.text_chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in ("script", "style", "head"):
            self._skip_data = False
        elif tag.lower() in ("p", "div", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6"):
            self.text_chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip_data:
            self.text_chunks.append(data)

    def get_text(self) -> str:
        return "".join(self.text_chunks)


def _html_to_text(text: str) -> str:
    raw = (text or "")[:1_000_000]  # P2: Cap input size to prevent DoS on huge emails
    if not raw.strip():
        return raw

    # P2: Use HTMLParser for robustness (handles malformed/nested tags better than regex)
    try:
        parser = _TextExtractor()
        parser.feed(raw)
        result = parser.get_text()
        # Unescape any HTML entities that weren't handled
        return html_lib.unescape(result)
    except Exception as e:
        _log.warning("html_parser_fallback reason=%s", str(e)[:100])
        # Fallback to regex-based approach if HTMLParser fails
        raw = _HTML_SCRIPT_STYLE_RE.sub(" ", raw)
        raw = _HTML_BR_RE.sub("\n", raw)
        raw = _HTML_BLOCK_END_RE.sub("\n", raw)
        raw = _HTML_TAG_RE.sub(" ", raw)
        return html_lib.unescape(raw)


def _strip_quoted_blocks(text: str) -> str:
    """
    Best-effort removal of quoted reply blocks.

    This is intentionally conservative: we keep the "top" content and drop the first
    recognized reply-marker block + any quote-prefixed lines.
    """
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    cut = None
    for pat in _REPLY_CUT_MARKERS:
        m = pat.search(raw)
        if m:
            cut = m.start() if cut is None else min(cut, m.start())
    if cut is not None and cut > 0:
        raw = raw[:cut]
    # Drop quote-prefixed lines (> ...)
    raw = _QUOTED_LINE_RE.sub("", raw)
    return raw


def _collapse_whitespace(text: str) -> str:
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for line in raw.split("\n"):
        line = _WS_RE.sub(" ", line).strip()
        lines.append(line)
    # Keep up to 2 consecutive blank lines.
    cooked = "\n".join(lines)
    cooked = _MULTI_NL_RE.sub("\n\n", cooked)
    return cooked.strip()


def strip_urls(text: str) -> str:
    return _URL_RE.sub(" ", text or "")


def normalize_email_body(body_text: str) -> NormalizedEmailBody:
    raw = body_text or ""
    cooked = _html_to_text(raw) if _looks_like_html(raw) else raw
    cooked = _strip_quoted_blocks(cooked)
    cooked = _collapse_whitespace(cooked)

    urls = extract_urls(cooked)
    cooked_no_urls = _collapse_whitespace(strip_urls(cooked))
    fingerprint = sha256_text(cooked_no_urls.lower())

    return NormalizedEmailBody(
        clean_text=cooked,
        clean_text_no_urls=cooked_no_urls,
        urls=urls,
        fingerprint=fingerprint,
    )


def extract_sender_email(sender_header: str) -> Optional[str]:
    m = _EMAIL_RE.search(sender_header or "")
    return m.group(1).lower() if m else None


def extract_urls(text: str) -> List[str]:
    urls: List[str] = []
    seen = set()
    for m in _URL_RE.finditer(text or ""):
        url = m.group(0).rstrip(").,;\"'")
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def _infer_link_type(url: str, vendor: Optional[VendorPattern], context: str) -> Tuple[str, bool, Optional[str]]:
    """
    Infer link type from URL and surrounding context.

    IMPORTANT: We only check context (subject/body) for keywords, NOT the URL path itself,
    to avoid false positives from random URL fragments containing "nda", "cim", etc.
    """
    url_l = (url or "").lower()
    ctx_l = (context or "").lower()

    vendor_hint = (vendor.vendor.lower().replace(" ", "_") if vendor else None)
    auth_required = bool(vendor.auth_required) if vendor and vendor.auth_required is not None else True

    if vendor and vendor.category == "calendar":
        return ("calendar", False, vendor_hint)
    if vendor and vendor.category == "dataroom":
        return ("dataroom", True, vendor_hint)

    # Filename hints (check URL for file extensions only)
    if any(ext in url_l for ext in [".xls", ".xlsx", ".csv"]):
        return ("financials", True, vendor_hint)

    # For keyword-based type inference, only check CONTEXT (not URL) to avoid false positives
    # Use word-boundary matching for short keywords and avoid broad terms like "confidential"
    if ".pdf" in url_l and _word_match(ctx_l, ["cim", "memorandum", "investment memorandum", "confidential information memorandum"]):
        return ("cim", True, vendor_hint)
    if _word_match(ctx_l, ["teaser", "executive summary", "one-pager"]):
        return ("teaser", True, vendor_hint)
    if _word_match(ctx_l, ["nda", "non-disclosure", "confidentiality agreement"]):
        return ("nda", True, vendor_hint)

    if vendor and vendor.category in {"docs", "cloud"}:
        return ("docs", auth_required, vendor_hint)

    return ("other", auth_required, vendor_hint)


def extract_entities(
    *,
    subject: str,
    sender: str,
    body_text: str,
    attachments: Sequence[EmailAttachment],
    vendor_patterns: Iterable[VendorPattern],
) -> Tuple[Optional[str], Optional[str], Optional[str], List[LinkEntity]]:
    sender_email = extract_sender_email(sender)
    broker_email = sender_email
    broker_name = None

    # Best-effort company inference from subject.
    company = None
    subj = (subject or "").strip()
    if subj.lower().startswith("project ") and len(subj) > 8:
        company = subj[8:].strip()
    elif " - " in subj:
        left = subj.split(" - ", 1)[0].strip()
        if 3 <= len(left) <= 80:
            company = left

    urls = extract_urls(body_text)

    # Filter out tracking/click-wrapper URLs to avoid link spam
    # These are URLs like HubSpot, Mailchimp, etc. that wrap destination URLs
    non_tracking_urls, tracking_urls = filter_tracking_urls(urls)
    if tracking_urls:
        _log.debug(f"Filtered {len(tracking_urls)} tracking URLs, kept {len(non_tracking_urls)} links")

    links: List[LinkEntity] = []
    # IMPORTANT: remove URLs from keyword context to avoid false positives from URL path fragments
    # (e.g., "/nda/" causing an NDA link type).
    context_no_urls = strip_urls(f"{subject}\n{body_text}")
    for url in non_tracking_urls:
        # Skip unsubscribe/social links as well
        link_cat = classify_link(url, context_no_urls)
        if link_cat in (LinkCategory.UNSUBSCRIBE, LinkCategory.SOCIAL):
            continue

        vendor = classify_url_vendor(url, vendor_patterns)
        link_type, auth_required, vendor_hint = _infer_link_type(url, vendor, context=context_no_urls)
        links.append(LinkEntity(type=link_type, url=url, auth_required=auth_required, vendor_hint=vendor_hint))

    return company, broker_name, broker_email, links


_DEAL_KEYWORDS = [
    "cim",
    "teaser",
    "confidential",
    "dataroom",
    "data room",
    "vdr",
    "loi",
    "letter of intent",
    "nda",
    "non-disclosure",
    "exclusivity",
    "diligence",
    "due diligence",
    "ebitda",
    "revenue multiple",
    "acquisition",
    "transaction",
    "management presentation",
    "investment memorandum",
]

_DEAL_KEYWORDS_STRONG = [
    "cim",
    "teaser",
    "dataroom",
    "data room",
    "vdr",
    "nda",
    "non-disclosure",
    "confidentiality agreement",
    "letter of intent",
    "loi",
    "ioi",
    "indication of interest",
    "quality of earnings",
    "qofe",
    "investment memorandum",
]

_DEAL_KEYWORDS_WEAK = [
    "acquisition",
    "diligence",
    "due diligence",
    "management presentation",
    "revenue",
    "ebitda",
    "multiple",
    "asking",
    "process",
]

_NON_DEAL_HINTS = [
    "receipt",
    "invoice",
    "order confirmation",
    "your order",
    "transaction was made",
    "credit card",
    "account alert",
    "shipment",
    "shipping",
    "delivery",
    "tracking",
    "payment received",
    "purchase",
]

_ATTACHMENT_DEAL_HINTS = [
    "cim",
    "teaser",
    "nda",
    "non-disclosure",
    "memorandum",
    "investment memorandum",
    "financial",
    "p&l",
    "pnl",
    "income",
    "balance",
    "cash flow",
    "qofe",
]

_ATTACHMENT_NON_DEAL_HINTS = [
    "receipt",
    "invoice",
    "order",
    "confirmation",
    "shipping",
    "shipment",
    "delivery",
    "tracking",
    "statement",
]

_NEWSLETTER_HINTS = ["unsubscribe", "view in browser", "newsletter", "marketing", "preferences"]
_SPAM_HINTS = ["verify your account", "crypto", "investment opportunity", "wire transfer", "urgent action required"]

_URGENCY_HIGH = ["asap", "urgent", "deadline", "by eod", "end of day", "best and final", "final round", "tomorrow", "today", "within 24 hours"]
_URGENCY_MED = ["follow up", "following up", "reminder", "checking in", "quick question"]

_NEWSLETTER_MARKER_RE = [
    re.compile(r"(?i)\bunsubscribe\b"),
    re.compile(r"(?i)\bmanage\s+(?:your\s+)?preferences\b"),
    re.compile(r"(?i)\bupdate\s+(?:your\s+)?preferences\b"),
    re.compile(r"(?i)\bview\s+(?:this\s+)?in\s+(?:a\s+)?browser\b"),
    re.compile(r"(?i)\bopt\s*out\b"),
    re.compile(r"(?i)\byou\s+(?:are|were)\s+receiving\s+this\s+(?:email\s+)?because\b"),
]

_IMAGE_EXTS = {"png", "jpg", "jpeg", "gif", "webp", "svg", "heic", "tif", "tiff", "bmp"}
_OPAQUE_ATTACHMENT_RE = re.compile(r"(?i)^(?:attachment|document|file|scan|image|img|photo)[-_ ]*\d*$")
_HEXISH_RE = re.compile(r"(?i)^[0-9a-f]{12,}$")


def _attachment_base_tokens(filename: str) -> List[str]:
    stem = re.sub(r"\.[A-Za-z0-9]+$", "", (filename or "").strip())
    stem = stem.lower()
    # Normalize separators to spaces (keeps word boundaries stable for ltm/ttm/etc)
    stem = re.sub(r"[^a-z0-9]+", " ", stem)
    return [t for t in stem.split() if t]


def _is_meaningful_attachment_name(filename: str) -> bool:
    base = re.sub(r"\.[A-Za-z0-9]+$", "", (filename or "").strip())
    if not base or len(base) < 6:
        return False
    if _OPAQUE_ATTACHMENT_RE.match(base):
        return False
    if _HEXISH_RE.match(base.replace("-", "").replace("_", "")):
        return False
    alpha = sum(1 for c in base if c.isalpha())
    return alpha >= 3


def _attachment_has_strong_deal_signal(att: EmailAttachment) -> bool:
    ext = (att.ext_lower or "").lower()
    if not ext or ext in _IMAGE_EXTS:
        return False
    if ext not in {"pdf", "xls", "xlsx", "ppt", "pptx", "doc", "docx", "csv", "txt"}:
        return False
    if not _is_meaningful_attachment_name(att.filename or ""):
        return False

    tokens = _attachment_base_tokens(att.filename)
    name_norm = " ".join(tokens)

    # Strong deal-material indicators
    if re.search(r"\b(cim|teaser|nda)\b", name_norm):
        return True
    if re.search(r"\b(non\s+disclosure|confidentiality\s+agreement)\b", name_norm):
        return True
    if re.search(r"\b(investment\s+memorandum|confidential\s+information\s+memorandum|memorandum)\b", name_norm):
        return True
    if re.search(r"\b(financials?|balance\s+sheet|cash\s*flow|income\s+statement|p\s*l|pnl)\b", name_norm):
        return True

    # Short metric tokens (ltm/ttm/t12) are only meaningful with an adjacent metric word.
    if re.search(r"\b(ltm|ttm|t12)\b", name_norm) and re.search(r"\b(revenue|sales|ebitda|earnings|profit)\b", name_norm):
        return True

    return False


def _score_attachments(attachments: Sequence[EmailAttachment]) -> float:
    """
    Deterministic attachment scoring.

    Philosophy:
    - Ignore inline images and opaque/random filenames.
    - Only treat attachments as strong signals when names look meaningful AND contain strong deal indicators.
    """
    score = 0.0
    for att in attachments or []:
        fname_l = (att.filename or "").lower()
        ext = (att.ext_lower or "").lower()
        if ext in _IMAGE_EXTS:
            continue

        # Penalize explicit transactional/receipt filenames (even if safe extension).
        if any(h in fname_l for h in _ATTACHMENT_NON_DEAL_HINTS):
            score -= 2.0
            continue

        if _attachment_has_strong_deal_signal(att):
            score += 1.75
            continue

        # Weak evidence: safe doc extensions, but only if the name looks meaningful.
        if ext in {"pdf", "xls", "xlsx", "ppt", "pptx", "doc", "docx", "csv"} and _is_meaningful_attachment_name(att.filename):
            score += 0.25

    return max(-3.0, min(3.0, score))


def _extract_sender_domain(sender: str) -> Optional[str]:
    """Extract domain from sender email address."""
    email = extract_sender_email(sender)
    if email and "@" in email:
        return email.split("@", 1)[1].lower()
    return None


def _is_denylisted_sender(sender: str) -> bool:
    """Check if sender is from a denylisted marketing/retail domain."""
    domain = _extract_sender_domain(sender)
    if not domain:
        return False
    # Check exact match first
    if domain in _SENDER_DOMAIN_DENYLIST:
        return True
    # Also check parent domain (e.g., "eml.nordstrom.com" matches "nordstrom.com")
    parts = domain.split(".")
    for i in range(len(parts) - 1):
        parent = ".".join(parts[i:])
        if parent in _SENDER_DOMAIN_DENYLIST:
            return True
    return False


def classify_email(
    *,
    subject: str,
    sender: str,
    body_text: str,
    links: Sequence[LinkEntity],
    attachments: Sequence[EmailAttachment],
) -> TriageClassification:
    blob = f"{subject}\n{body_text}".lower()  # Exclude sender from blob to avoid false matches

    # EARLY EXIT: Denylisted senders are NEVER deals (marketing/retail/consumer services)
    if _is_denylisted_sender(sender):
        return TriageClassification(
            classification="NEWSLETTER",
            urgency="LOW",
            reason=f"Sender domain is denylisted (marketing/retail). domain={_extract_sender_domain(sender)}",
        )

    # Score deal-likeness deterministically to avoid flooding quarantine with receipts/invoices.
    reasons: List[str] = []
    score = 0.0

    # Use word-boundary matching to avoid false positives like "nda" in "mandatory"
    strong_hits = _word_match(blob, _DEAL_KEYWORDS_STRONG)
    weak_hits = _word_match(blob, _DEAL_KEYWORDS_WEAK)
    if strong_hits:
        score += min(3.0, 1.25 * len(strong_hits))
        reasons.append(f"strong_keywords={strong_hits[:3]}")
    if weak_hits:
        score += min(1.5, 0.5 * len(weak_hits))
        reasons.append(f"weak_keywords={weak_hits[:3]}")

    # Link typing guardrail: only strong material links count as deal links.
    has_deal_links = any(l.type in {"cim", "teaser", "dataroom", "nda", "financials"} for l in links)
    if has_deal_links:
        score += 1.5
        reasons.append("deal_links")

    # Attachments: treat as weak evidence unless filename strongly suggests deal docs.
    attachment_score = _score_attachments(attachments)
    if attachment_score:
        score += attachment_score
        reasons.append(f"attachments_score={attachment_score:+.2f}")

    non_deal_hits = [h for h in _NON_DEAL_HINTS if h in blob]
    newsletter_markers = any(p.search(blob) for p in _NEWSLETTER_MARKER_RE)

    if any(h in blob for h in _SPAM_HINTS):
        classification = "SPAM"
        reason = "Contains high-risk spam/phishing indicators."
    elif (newsletter_markers or any(h in blob for h in _NEWSLETTER_HINTS)) and (not strong_hits) and (not has_deal_links) and attachment_score <= 0.25 and score < 2.0:
        classification = "NEWSLETTER"
        reason = f"Looks like a newsletter/marketing message (markers detected). deal_score={score:.2f}"
    elif non_deal_hits and score < 2.0:
        classification = "OPERATIONAL"
        reason = f"Looks like a non-deal transactional email ({non_deal_hits[:3]}). deal_score={score:.2f}"
    elif has_deal_links or strong_hits or score >= 2.0:
        classification = "DEAL_SIGNAL"
        reason = f"Contains deal-related signals. deal_score={score:.2f} reasons={'; '.join(reasons[:3])}"
    else:
        classification = "OPERATIONAL"
        reason = f"No strong deal signals detected; treated as operational. deal_score={score:.2f}"

    urgency = "LOW"
    if any(h in blob for h in _URGENCY_HIGH):
        urgency = "HIGH"
    elif any(h in blob for h in _URGENCY_MED) or "?" in (subject or ""):
        urgency = "MED"

    return TriageClassification(classification=classification, urgency=urgency, reason=reason)


def decide_actions_and_labels(
    *,
    email: EmailMessage,
    vendor_patterns: Iterable[VendorPattern],
) -> TriageDecision:
    norm = normalize_email_body(email.body or "")
    company, broker_name, broker_email, links = extract_entities(
        subject=email.subject,
        sender=email.sender,
        body_text=norm.clean_text,
        attachments=email.attachments,
        vendor_patterns=vendor_patterns,
    )

    classification = classify_email(
        subject=email.subject,
        sender=email.sender,
        body_text=norm.clean_text_no_urls,
        links=links,
        attachments=email.attachments,
    )

    needs_docs = any(l.type in {"dataroom", "docs"} for l in links) and classification.classification == "DEAL_SIGNAL"
    needs_reply = classification.classification == "DEAL_SIGNAL" and (
        "?" in norm.clean_text or any(k in norm.clean_text.lower() for k in ["please", "let me know", "confirm"])
    )

    quarantine = any(l.type == "other" and (l.vendor_hint is None) and l.auth_required for l in links)

    labels: List[str] = []
    if classification.classification == "DEAL_SIGNAL":
        labels.append("ZakOps/Deal")
    if classification.classification in {"OPERATIONAL", "NEWSLETTER"}:
        labels.append("ZakOps/NonDeal")
    if classification.classification == "SPAM":
        labels.append("ZakOps/Spam-LowValue")
    if classification.urgency == "HIGH":
        labels.append("ZakOps/Urgent")
    if needs_docs:
        labels.append("ZakOps/Needs-Docs")
    if needs_reply:
        labels.append("ZakOps/Needs-Reply")
    if quarantine:
        labels.append("ZakOps/Quarantine")
    if classification.classification in {"OPERATIONAL", "NEWSLETTER"} and email.attachments:
        labels.append("ZakOps/Needs-Review")
    if classification.classification == "DEAL_SIGNAL" and not (links or email.attachments):
        labels.append("ZakOps/Needs-Review")

    # De-dupe while preserving order.
    deduped: List[str] = []
    seen = set()
    for l in labels:
        if l not in seen:
            deduped.append(l)
            seen.add(l)

    return TriageDecision(
        classification=classification,
        sender_email=broker_email,
        company=company,
        links=links,
        attachments=list(email.attachments),
        labels_to_add=deduped,
        needs_reply=needs_reply,
        needs_docs=needs_docs,
        quarantine=quarantine,
        eligible_for_llm=classification.classification not in {"SPAM", "NEWSLETTER"}
        and "transactional email" not in (classification.reason or "").lower()
        and not _is_denylisted_sender(email.sender),
        body_fingerprint=norm.fingerprint,
    )
