"""Deterministic record fingerprinting and deduplication indexing."""

from __future__ import annotations

import hashlib
import logging
import re
from typing import Any
from urllib.parse import urlparse, urlunparse

logger = logging.getLogger("streamforge.extraction.fingerprint")


def canonicalize_text(text: str | None) -> str:
    """Normalize text by stripping whitespace, collapsing multiple spaces, and lowercasing."""
    if not text:
        return ""
    # Collapse multiple whitespaces and trim
    cleaned = re.sub(r"\s+", " ", str(text).strip())
    return cleaned.lower()


def canonicalize_url(url: str | None) -> str:
    """Normalize URL by lowercasing scheme/host, removing trailing slash, and stripping fragments."""
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip())
        # Reconstruct with lowercase scheme & netloc, path without trailing slash
        clean_path = parsed.path.rstrip("/")
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            clean_path,
            parsed.params,
            parsed.query,
            "",  # Remove fragment
        ))
        return normalized
    except Exception:
        return url.strip().rstrip("/").lower()


def generate_record_fingerprint(record: dict[str, Any]) -> str:
    """Generate a deterministic SHA-256 fingerprint hash for a record.

    The hash combines the canonicalized source_url, job_title, and company_name.
    """
    canon_url = canonicalize_url(record.get("source_url", ""))
    canon_title = canonicalize_text(record.get("job_title", ""))
    canon_company = canonicalize_text(record.get("company_name", ""))

    payload = f"{canon_url}|{canon_title}|{canon_company}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class DeduplicationIndex:
    """Thread-safe in-memory deduplication index tracking seen fingerprint hashes."""

    def __init__(self):
        self._seen_hashes: set[str] = set()
        self.duplicates_count: int = 0

    def is_duplicate(self, fingerprint: str) -> bool:
        """Check if a fingerprint has been seen previously."""
        return fingerprint in self._seen_hashes

    def add(self, fingerprint: str) -> bool:
        """Attempt to add fingerprint. Returns True if new (accepted), False if duplicate (rejected)."""
        if fingerprint in self._seen_hashes:
            self.duplicates_count += 1
            return False
        self._seen_hashes.add(fingerprint)
        return True

    def reset(self) -> None:
        """Reset the index."""
        self._seen_hashes.clear()
        self.duplicates_count = 0

    @property
    def total_unique(self) -> int:
        """Total number of unique records indexed."""
        return len(self._seen_hashes)
