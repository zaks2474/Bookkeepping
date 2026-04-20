"""
Tests for link normalization, classification, and deduplication utilities.
"""

import pytest
from email_triage_agent.link_utils import (
    LinkCategory,
    ClassifiedLink,
    safe_url,
    classify_link,
    filter_tracking_urls,
    generate_canonical_key,
    deduplicate_links,
    classify_and_dedupe_links,
    _is_tracking_domain,
    _is_unsubscribe_url,
    _is_social_url,
)


class TestTrackingDomainDetection:
    """Test tracking/click-wrapper domain detection."""

    def test_hubspot_tracking_domains(self):
        """HubSpot tracking domains should be detected."""
        assert _is_tracking_domain("hubspotlinks.com")
        assert _is_tracking_domain("hubspotlinksstarter.com")
        assert _is_tracking_domain("d13dQH04.na1.hubspotlinksstarter.com")
        assert _is_tracking_domain("track.hubspot.com")

    def test_mailchimp_tracking_domains(self):
        """Mailchimp tracking domains should be detected."""
        assert _is_tracking_domain("list-manage.com")
        assert _is_tracking_domain("mailchi.mp")
        assert _is_tracking_domain("click.mailchimp.com")

    def test_other_tracking_domains(self):
        """Other common tracking domains should be detected."""
        assert _is_tracking_domain("sendgrid.net")
        assert _is_tracking_domain("pardot.com")
        assert _is_tracking_domain("safelinks.protection.outlook.com")

    def test_tracking_domain_patterns(self):
        """Tracking domain patterns (prefixes) should match."""
        assert _is_tracking_domain("click.example.com")
        assert _is_tracking_domain("trk.company.com")
        assert _is_tracking_domain("track.newsletter.net")

    def test_non_tracking_domains(self):
        """Non-tracking domains should not be detected as tracking."""
        assert not _is_tracking_domain("google.com")
        assert not _is_tracking_domain("example.com")
        assert not _is_tracking_domain("axial.net")
        assert not _is_tracking_domain("firmex.com")


class TestLinkClassification:
    """Test link type classification."""

    def test_tracking_url_classification(self):
        """Tracking URLs should be classified as tracking."""
        url = "https://d13dQH04.na1.hubspotlinksstarter.com/Ctc/5E+113/d13dQH04/VWP6ML1sNQB_N4rNJnRlzKzHVfQRxk5FrkhYMBB8Tl3lcq"
        assert classify_link(url) == LinkCategory.TRACKING

    def test_unsubscribe_url_classification(self):
        """Unsubscribe URLs should be classified as unsubscribe."""
        assert classify_link("https://example.com/unsubscribe") == LinkCategory.UNSUBSCRIBE
        assert classify_link("https://example.com/preferences") == LinkCategory.UNSUBSCRIBE
        assert classify_link("https://hs.example.com/hs/manage-preferences/abc") == LinkCategory.UNSUBSCRIBE

    def test_social_url_classification(self):
        """Social media URLs should be classified as social."""
        assert classify_link("https://linkedin.com/in/johndoe") == LinkCategory.SOCIAL
        assert classify_link("https://www.linkedin.com/company/acme") == LinkCategory.SOCIAL
        assert classify_link("https://twitter.com/user") == LinkCategory.SOCIAL
        assert classify_link("https://x.com/user") == LinkCategory.SOCIAL

    def test_regular_url_classification(self):
        """Regular URLs should be classified as other."""
        assert classify_link("https://axial.net/deal/123") == LinkCategory.OTHER
        assert classify_link("https://firmex.com/room/abc") == LinkCategory.OTHER
        assert classify_link("https://example.com/document.pdf") == LinkCategory.OTHER


class TestFilterTrackingUrls:
    """Test tracking URL filtering."""

    def test_filter_mixed_urls(self):
        """Should separate tracking from non-tracking URLs."""
        urls = [
            "https://d13dQH04.na1.hubspotlinksstarter.com/Ctc/5E+113/track1",
            "https://d13dQH04.na1.hubspotlinksstarter.com/Ctc/5E+113/track2",
            "https://axial.net/deal/123",
            "https://firmex.com/room/abc",
            "https://click.mailchimp.com/track/xyz",
        ]

        non_tracking, tracking = filter_tracking_urls(urls)

        assert len(non_tracking) == 2
        assert len(tracking) == 3
        assert "https://axial.net/deal/123" in non_tracking
        assert "https://firmex.com/room/abc" in non_tracking

    def test_filter_all_tracking(self):
        """Should handle all-tracking URL lists."""
        urls = [
            "https://d13dQH04.na1.hubspotlinksstarter.com/Ctc/1",
            "https://d13dQH04.na1.hubspotlinksstarter.com/Ctc/2",
        ]

        non_tracking, tracking = filter_tracking_urls(urls)

        assert len(non_tracking) == 0
        assert len(tracking) == 2

    def test_filter_no_tracking(self):
        """Should handle no-tracking URL lists."""
        urls = [
            "https://axial.net/deal/123",
            "https://firmex.com/room/abc",
        ]

        non_tracking, tracking = filter_tracking_urls(urls)

        assert len(non_tracking) == 2
        assert len(tracking) == 0


class TestSafeUrl:
    """Test URL sanitization."""

    def test_strips_query_params(self):
        """Should strip query parameters."""
        url = "https://example.com/path?token=secret&utm_source=email"
        assert safe_url(url) == "https://example.com/path"

    def test_strips_fragment(self):
        """Should strip URL fragment."""
        url = "https://example.com/path#section"
        assert safe_url(url) == "https://example.com/path"

    def test_preserves_path(self):
        """Should preserve URL path."""
        url = "https://example.com/deep/nested/path"
        assert safe_url(url) == "https://example.com/deep/nested/path"


class TestCanonicalKey:
    """Test canonical key generation."""

    def test_same_url_same_key(self):
        """Same URLs should have same canonical key."""
        url1 = "https://example.com/doc.pdf"
        url2 = "https://example.com/doc.pdf"
        assert generate_canonical_key(url1) == generate_canonical_key(url2)

    def test_different_urls_different_keys(self):
        """Different URLs should have different canonical keys."""
        url1 = "https://example.com/doc1.pdf"
        url2 = "https://example.com/doc2.pdf"
        assert generate_canonical_key(url1) != generate_canonical_key(url2)

    def test_resolved_url_affects_key(self):
        """Resolved URL should affect canonical key."""
        tracking_url = "https://track.example.com/redirect/xyz"
        resolved_url = "https://actual.example.com/doc.pdf"

        key_tracking = generate_canonical_key(tracking_url)
        key_resolved = generate_canonical_key(tracking_url, resolved_url=resolved_url)

        assert key_tracking != key_resolved


class TestDeduplication:
    """Test link deduplication."""

    def test_dedupe_identical_urls(self):
        """Should dedupe identical URLs."""
        links = [
            ClassifiedLink(
                original_url="https://example.com/doc.pdf",
                safe_url="https://example.com/doc.pdf",
                category=LinkCategory.OTHER,
                canonical_key="https://example.com/doc.pdf|other|False",
            ),
            ClassifiedLink(
                original_url="https://example.com/doc.pdf",
                safe_url="https://example.com/doc.pdf",
                category=LinkCategory.OTHER,
                canonical_key="https://example.com/doc.pdf|other|False",
            ),
        ]

        deduped = deduplicate_links(links)
        assert len(deduped) == 1

    def test_dedupe_keeps_unique(self):
        """Should keep unique URLs."""
        links = [
            ClassifiedLink(
                original_url="https://example.com/doc1.pdf",
                safe_url="https://example.com/doc1.pdf",
                category=LinkCategory.OTHER,
                canonical_key="https://example.com/doc1.pdf|other|False",
            ),
            ClassifiedLink(
                original_url="https://example.com/doc2.pdf",
                safe_url="https://example.com/doc2.pdf",
                category=LinkCategory.OTHER,
                canonical_key="https://example.com/doc2.pdf|other|False",
            ),
        ]

        deduped = deduplicate_links(links)
        assert len(deduped) == 2


class TestClassifyAndDedupe:
    """Test the combined classify and dedupe function."""

    def test_classify_and_dedupe_mixed_urls(self):
        """Should classify and dedupe mixed URL list."""
        urls = [
            "https://d13dQH04.na1.hubspotlinksstarter.com/Ctc/track1",
            "https://d13dQH04.na1.hubspotlinksstarter.com/Ctc/track2",
            "https://axial.net/deal/123",
            "https://linkedin.com/in/johndoe",
            "https://example.com/unsubscribe",
        ]

        primary, by_category = classify_and_dedupe_links(urls)

        # Primary list should only contain non-tracking, non-unsubscribe, non-social
        assert len(primary) == 1
        assert primary[0].safe_url == "https://axial.net/deal/123"

        # Categories should be populated
        assert LinkCategory.TRACKING in by_category
        assert len(by_category[LinkCategory.TRACKING]) == 2

        assert LinkCategory.SOCIAL in by_category
        assert len(by_category[LinkCategory.SOCIAL]) == 1

        assert LinkCategory.UNSUBSCRIBE in by_category
        assert len(by_category[LinkCategory.UNSUBSCRIBE]) == 1


class TestRegressionHubspotEmailLinks:
    """Regression tests for the HubSpot email link spam issue."""

    def test_hubspot_email_with_37_tracking_links(self):
        """Should handle email with many HubSpot tracking links (original issue)."""
        # Simulate the original issue: 37 tracking links + 1 unsubscribe
        tracking_urls = [
            f"https://d13dQH04.na1.hubspotlinksstarter.com/Ctc/5E+113/d13dQH04/VWP6ML1sNQB_{i}"
            for i in range(37)
        ]
        urls = tracking_urls + ["https://hs-9012798.s.hubspotstarter.net/preferences/en/manage"]

        primary, by_category = classify_and_dedupe_links(urls)

        # Primary list should be empty (all are tracking/unsubscribe)
        assert len(primary) == 0

        # All tracking links should be in the tracking category
        assert len(by_category.get(LinkCategory.TRACKING, [])) == 37

        # Unsubscribe link should be in unsubscribe category
        assert len(by_category.get(LinkCategory.UNSUBSCRIBE, [])) == 1

    def test_email_with_real_deal_links_and_tracking(self):
        """Should preserve real deal links while filtering tracking."""
        urls = [
            # Real deal links
            "https://axial.net/deal/proj-sunrise/overview",
            "https://firmex.com/dataroom/12345",
            "https://vestedbb.com/opportunity/abc",
            # Tracking links (should be filtered)
            "https://d13dQH04.na1.hubspotlinksstarter.com/Ctc/track1",
            "https://d13dQH04.na1.hubspotlinksstarter.com/Ctc/track2",
            # Unsubscribe (should be filtered)
            "https://example.com/unsubscribe",
            # Social (should be filtered from primary)
            "https://linkedin.com/company/acme",
        ]

        primary, by_category = classify_and_dedupe_links(urls)

        # Should have 3 primary links (the deal platform links)
        assert len(primary) == 3

        # Verify the deal links are preserved
        primary_urls = {l.safe_url for l in primary}
        assert "https://axial.net/deal/proj-sunrise/overview" in primary_urls
        assert "https://firmex.com/dataroom/12345" in primary_urls
        assert "https://vestedbb.com/opportunity/abc" in primary_urls
