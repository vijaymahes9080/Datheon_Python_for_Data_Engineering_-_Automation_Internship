"""Pytest fixtures and configuration for StreamForge test suite."""

from __future__ import annotations

import pathlib
import sys
import pytest

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from config.settings import settings


@pytest.fixture(scope="session")
def fixtures_dir() -> pathlib.Path:
    """Return path to test fixtures directory."""
    return settings.DATA_FIXTURES_DIR


@pytest.fixture(scope="session")
def html_fixtures_dir() -> pathlib.Path:
    """Return path to HTML fixtures directory."""
    return settings.HTML_FIXTURES_DIR


@pytest.fixture
def sample_card_html() -> str:
    """Return a single HTML job card for unit parsing tests."""
    return """
    <article class="job-card" id="job-999">
      <div class="job-header">
        <h2 class="job-title"><a class="job-link" href="https://example.com/jobs/999">Lead Systems Architect</a></h2>
        <span class="job-badge">Cloud Systems</span>
      </div>
      <div class="job-meta">
        <span class="job-company">Apex Systems</span> &bull; 
        <span class="job-location">Remote (US)</span> &bull; 
        <span class="job-type">Full-time</span>
      </div>
      <div class="job-details">
        <span class="job-salary">$160,000 - $190,000</span>
        <time class="job-date" datetime="2026-10-21">2026-10-21</time>
      </div>
    </article>
    """


@pytest.fixture
def messy_card_html() -> str:
    """Return an incomplete card to test defensive fallback parsing."""
    return """
    <article class="job-card">
      <h2 class="job-title">Incomplete Listing</h2>
      <!-- Missing company, salary, location, badges -->
    </article>
    """
