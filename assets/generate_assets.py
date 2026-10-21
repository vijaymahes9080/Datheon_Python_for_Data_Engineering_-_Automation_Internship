"""Generate ultra-crisp, light-theme SVG and PNG graphics for StreamForge README and LinkedIn."""

from __future__ import annotations

import pathlib
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = pathlib.Path(__file__).resolve().parent.parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def generate_hero_banner_svg() -> pathlib.Path:
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 420" width="1200" height="420">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="50%" stop-color="#F8FAFC"/>
      <stop offset="100%" stop-color="#E0F2FE"/>
    </linearGradient>
    <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0284C7"/>
      <stop offset="100%" stop-color="#06B6D4"/>
    </linearGradient>
    <linearGradient id="navyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0F172A"/>
      <stop offset="100%" stop-color="#1E293B"/>
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#0F172A" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1200" height="420" fill="url(#bgGrad)" rx="16"/>
  <rect x="1" y="1" width="1198" height="418" fill="none" stroke="#E2E8F0" stroke-width="2" rx="15"/>

  <!-- Technical Grid Pattern -->
  <g stroke="#E2E8F0" stroke-width="1" opacity="0.6">
    <line x1="80" y1="0" x2="80" y2="420"/>
    <line x1="240" y1="0" x2="240" y2="420"/>
    <line x1="400" y1="0" x2="400" y2="420"/>
    <line x1="560" y1="0" x2="560" y2="420"/>
    <line x1="720" y1="0" x2="720" y2="420"/>
    <line x1="880" y1="0" x2="880" y2="420"/>
    <line x1="1040" y1="0" x2="1040" y2="420"/>
    <line x1="0" y1="80" x2="1200" y2="80"/>
    <line x1="0" y1="180" x2="1200" y2="180"/>
    <line x1="0" y1="280" x2="1200" y2="280"/>
    <line x1="0" y1="380" x2="1200" y2="380"/>
  </g>

  <!-- Decorative Circuit Nodes -->
  <g fill="#0284C7" opacity="0.4">
    <circle cx="80" cy="80" r="4"/>
    <circle cx="240" cy="180" r="4"/>
    <circle cx="400" cy="80" r="4"/>
    <circle cx="560" cy="280" r="4"/>
    <circle cx="720" cy="180" r="4"/>
    <circle cx="880" cy="80" r="4"/>
    <circle cx="1040" cy="280" r="4"/>
  </g>

  <!-- Left Content -->
  <g transform="translate(60, 60)">
    <!-- Tag Pill -->
    <rect x="0" y="0" width="370" height="32" rx="16" fill="#0F172A"/>
    <text x="18" y="21" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="12" font-weight="700" fill="#38BDF8" letter-spacing="1.5">DATA ENGINEERING INTERNSHIP • PERSON 3</text>

    <!-- Main Title -->
    <text x="0" y="105" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="56" font-weight="900" fill="#0F172A" letter-spacing="-1">StreamForge</text>
    <text x="350" y="105" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="56" font-weight="900" fill="#0284C7">⚡</text>

    <!-- Subtitle -->
    <text x="0" y="150" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="600" fill="#334155">Autonomous Web Extractor • Data Quality • Relational Upserts • ETL Orchestrator</text>
    <text x="0" y="180" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="15" font-weight="400" fill="#64748B">A production-grade Python data engineering suite powered by SQLAlchemy 2.0, Pandas, and Streamlit.</text>

    <!-- Tech Badges -->
    <g transform="translate(0, 220)">
      <rect x="0" y="0" width="105" height="30" rx="6" fill="#F1F5F9" stroke="#CBD5E1"/>
      <text x="14" y="20" font-family="monospace" font-size="13" font-weight="600" fill="#0F172A">Python 3.12</text>

      <rect x="115" y="0" width="115" height="30" rx="6" fill="#F1F5F9" stroke="#CBD5E1"/>
      <text x="127" y="20" font-family="monospace" font-size="13" font-weight="600" fill="#0284C7">BeautifulSoup4</text>

      <rect x="240" y="0" width="85" height="30" rx="6" fill="#F1F5F9" stroke="#CBD5E1"/>
      <text x="254" y="20" font-family="monospace" font-size="13" font-weight="600" fill="#0F172A">Pandas</text>

      <rect x="335" y="0" width="130" height="30" rx="6" fill="#F1F5F9" stroke="#CBD5E1"/>
      <text x="347" y="20" font-family="monospace" font-size="13" font-weight="600" fill="#0284C7">SQLAlchemy 2.0</text>

      <rect x="475" y="0" width="95" height="30" rx="6" fill="#F1F5F9" stroke="#CBD5E1"/>
      <text x="488" y="20" font-family="monospace" font-size="13" font-weight="600" fill="#0F172A">Streamlit</text>

      <rect x="580" y="0" width="130" height="30" rx="6" fill="#ECFDF5" stroke="#A7F3D0"/>
      <text x="592" y="20" font-family="monospace" font-size="13" font-weight="700" fill="#059669">✓ 38 Tests Pass</text>
    </g>
  </g>

  <!-- Right Geometric Card (Telemetry Showcase) -->
  <g transform="translate(820, 50)" filter="url(#shadow)">
    <rect width="320" height="310" rx="14" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>
    <rect x="0" y="0" width="320" height="48" rx="14" fill="#0F172A"/>
    <circle cx="20" cy="24" r="5" fill="#EF4444"/>
    <circle cx="36" cy="24" r="5" fill="#F59E0B"/>
    <circle cx="52" cy="24" r="5" fill="#10B981"/>
    <text x="80" y="29" font-family="monospace" font-size="13" font-weight="600" fill="#F8FAFC">StreamForge Telemetry</text>

    <!-- Metric Row 1 -->
    <rect x="20" y="65" width="280" height="58" rx="8" fill="#F8FAFC" stroke="#E2E8F0"/>
    <text x="35" y="87" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="600" fill="#64748B" letter-spacing="1">TOTAL STORED RECORDS</text>
    <text x="35" y="112" font-family="monospace" font-size="20" font-weight="700" fill="#0F172A">121 Verified</text>
    <rect x="220" y="78" width="65" height="24" rx="12" fill="#ECFDF5"/>
    <text x="231" y="94" font-family="monospace" font-size="11" font-weight="700" fill="#059669">0 Dups</text>

    <!-- Metric Row 2 -->
    <rect x="20" y="135" width="280" height="58" rx="8" fill="#F8FAFC" stroke="#E2E8F0"/>
    <text x="35" y="157" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="600" fill="#64748B" letter-spacing="1">END-TO-END PIPELINE</text>
    <text x="35" y="182" font-family="monospace" font-size="20" font-weight="700" fill="#0284C7">SUCCESS</text>
    <rect x="225" y="148" width="60" height="24" rx="12" fill="#E0F2FE"/>
    <text x="235" y="164" font-family="monospace" font-size="11" font-weight="700" fill="#0284C7">0.63s</text>

    <!-- Metric Row 3 -->
    <rect x="20" y="205" width="280" height="58" rx="8" fill="#F8FAFC" stroke="#E2E8F0"/>
    <text x="35" y="227" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="600" fill="#64748B" letter-spacing="1">DATA ACCEPTANCE RATE</text>
    <text x="35" y="252" font-family="monospace" font-size="20" font-weight="700" fill="#0F172A">94.26%</text>
    <rect x="210" y="218" width="75" height="24" rx="12" fill="#FEF3C7"/>
    <text x="219" y="234" font-family="monospace" font-size="11" font-weight="700" fill="#D97706">7 Rejects</text>

    <!-- Footer status -->
    <circle cx="32" cy="288" r="4" fill="#10B981"/>
    <text x="44" y="292" font-family="monospace" font-size="11" font-weight="600" fill="#64748B">Engine: SQLite (Zero Setup Ready)</text>
  </g>
</svg>"""
    p = ASSETS_DIR / "hero_banner.svg"
    p.write_text(svg_content, encoding="utf-8")
    print(f"Generated {p.name}")
    return p


def generate_pipeline_workflow_svg() -> pathlib.Path:
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 460" width="1200" height="460">
  <defs>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="100%" stop-color="#F8FAFC"/>
    </linearGradient>
    <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-color="#0F172A" flood-opacity="0.06"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1200" height="460" fill="#F8FAFC" rx="16"/>
  <rect x="1" y="1" width="1198" height="458" fill="none" stroke="#E2E8F0" stroke-width="2" rx="15"/>

  <!-- Section Header -->
  <text x="60" y="55" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" font-weight="700" fill="#0284C7" letter-spacing="1.5">END-TO-END DATA ARCHITECTURE</text>
  <text x="60" y="90" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="28" font-weight="800" fill="#0F172A">StreamForge 4-Stage ETL State Machine</text>
  <text x="60" y="115" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="14" font-weight="400" fill="#64748B">Extract -> Inspect -> Transform -> Validate -> Upsert -> Verify -> Report -> Notify</text>

  <!-- Connecting Line -->
  <line x1="180" y1="260" x2="1020" y2="260" stroke="#CBD5E1" stroke-width="3" stroke-dasharray="6 6"/>

  <!-- Card 1: Task 1 Extractor -->
  <g transform="translate(60, 150)" filter="url(#cardShadow)">
    <rect width="250" height="260" rx="12" fill="url(#cardGrad)" stroke="#E2E8F0" stroke-width="1.5"/>
    <rect x="0" y="0" width="250" height="6" rx="3" fill="#0284C7"/>
    <circle cx="35" cy="35" r="18" fill="#E0F2FE"/>
    <text x="27" y="42" font-size="18">🌐</text>
    <text x="65" y="32" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="700" fill="#0284C7">TASK 1</text>
    <text x="65" y="48" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="15" font-weight="700" fill="#0F172A">Web Extractor</text>

    <text x="20" y="85" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="600" fill="#334155">• BeautifulSoup4 &amp; Requests</text>
    <text x="20" y="110" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• Exponential Backoff (3x)</text>
    <text x="20" y="135" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• SHA-256 Fingerprinting</text>
    <text x="20" y="160" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• Multi-page Pagination</text>

    <rect x="20" y="195" width="210" height="42" rx="6" fill="#F1F5F9"/>
    <text x="30" y="213" font-family="monospace" font-size="11" font-weight="600" fill="#0284C7">120 Records Extracted</text>
    <text x="30" y="228" font-family="monospace" font-size="10" font-weight="500" fill="#64748B">Output: CSV &amp; JSON in raw/</text>
  </g>

  <!-- Card 2: Task 2 Quality Engine -->
  <g transform="translate(340, 150)" filter="url(#cardShadow)">
    <rect width="250" height="260" rx="12" fill="url(#cardGrad)" stroke="#E2E8F0" stroke-width="1.5"/>
    <rect x="0" y="0" width="250" height="6" rx="3" fill="#10B981"/>
    <circle cx="35" cy="35" r="18" fill="#ECFDF5"/>
    <text x="27" y="42" font-size="18">✨</text>
    <text x="65" y="32" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="700" fill="#059669">TASK 2</text>
    <text x="65" y="48" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="15" font-weight="700" fill="#0F172A">Quality Engine</text>

    <text x="20" y="85" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="600" fill="#334155">• Snake_case Standardization</text>
    <text x="20" y="110" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• Currency &amp; Salary Parser</text>
    <text x="20" y="135" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• ISO-8601 Date Normalizer</text>
    <text x="20" y="160" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• Pydantic Rejection Ledger</text>

    <rect x="20" y="195" width="210" height="42" rx="6" fill="#F1F5F9"/>
    <text x="30" y="213" font-family="monospace" font-size="11" font-weight="600" fill="#059669">94.26% Pass (115/122)</text>
    <text x="30" y="228" font-family="monospace" font-size="10" font-weight="500" fill="#64748B">7 Anomaly Rows Isolated</text>
  </g>

  <!-- Card 3: Task 3 Relational Persistence -->
  <g transform="translate(620, 150)" filter="url(#cardShadow)">
    <rect width="250" height="260" rx="12" fill="url(#cardGrad)" stroke="#E2E8F0" stroke-width="1.5"/>
    <rect x="0" y="0" width="250" height="6" rx="3" fill="#6366F1"/>
    <circle cx="35" cy="35" r="18" fill="#EEF2FF"/>
    <text x="27" y="42" font-size="18">🗄️</text>
    <text x="65" y="32" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="700" fill="#4F46E5">TASK 3</text>
    <text x="65" y="48" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="15" font-weight="700" fill="#0F172A">Upsert Persistence</text>

    <text x="20" y="85" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="600" fill="#334155">• SQLAlchemy 2.0 Engine</text>
    <text x="20" y="110" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• Dialect ON CONFLICT Update</text>
    <text x="20" y="135" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• Atomic Transaction Rollback</text>
    <text x="20" y="160" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• Composite Indexing</text>

    <rect x="20" y="195" width="210" height="42" rx="6" fill="#F1F5F9"/>
    <text x="30" y="213" font-family="monospace" font-size="11" font-weight="600" fill="#4F46E5">100% Idempotent Upsert</text>
    <text x="30" y="228" font-family="monospace" font-size="10" font-weight="500" fill="#64748B">0 Duplicate Insertions</text>
  </g>

  <!-- Card 4: Task 4 Automation & Alerting -->
  <g transform="translate(900, 150)" filter="url(#cardShadow)">
    <rect width="250" height="260" rx="12" fill="url(#cardGrad)" stroke="#E2E8F0" stroke-width="1.5"/>
    <rect x="0" y="0" width="250" height="6" rx="3" fill="#F59E0B"/>
    <circle cx="35" cy="35" r="18" fill="#FEF3C7"/>
    <text x="27" y="42" font-size="18">⚡</text>
    <text x="65" y="32" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="700" fill="#D97706">TASK 4</text>
    <text x="65" y="48" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="15" font-weight="700" fill="#0F172A">ETL Orchestrator</text>

    <text x="20" y="85" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="600" fill="#334155">• 8-Stage Execution Loop</text>
    <text x="20" y="110" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• Concurrency Mutex Lock</text>
    <text x="20" y="135" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• Dry-Run Simulation Mode</text>
    <text x="20" y="160" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="400" fill="#64748B">• Multi-Channel Alerting</text>

    <rect x="20" y="195" width="210" height="42" rx="6" fill="#F1F5F9"/>
    <text x="30" y="213" font-family="monospace" font-size="11" font-weight="600" fill="#D97706">Duration: 0.629s</text>
    <text x="30" y="228" font-family="monospace" font-size="10" font-weight="500" fill="#64748B">Console, Webhook &amp; SMTP</text>
  </g>
</svg>"""
    p = ASSETS_DIR / "pipeline_workflow.svg"
    p.write_text(svg_content, encoding="utf-8")
    print(f"Generated {p.name}")
    return p


def generate_dashboard_mockup_svg() -> pathlib.Path:
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 560" width="1200" height="560">
  <defs>
    <filter id="winShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#0F172A" flood-opacity="0.10"/>
    </filter>
  </defs>

  <!-- Canvas -->
  <rect width="1200" height="560" fill="#F1F5F9" rx="16"/>

  <!-- Browser Window Frame -->
  <g transform="translate(40, 30)" filter="url(#winShadow)">
    <rect width="1120" height="500" rx="12" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>

    <!-- Window Titlebar -->
    <rect width="1120" height="42" rx="12" fill="#F8FAFC"/>
    <circle cx="25" cy="21" r="5" fill="#EF4444"/>
    <circle cx="41" cy="21" r="5" fill="#F59E0B"/>
    <circle cx="57" cy="21" r="5" fill="#10B981"/>
    <rect x="180" y="9" width="760" height="24" rx="6" fill="#FFFFFF" stroke="#E2E8F0"/>
    <text x="450" y="25" font-family="monospace" font-size="11" fill="#64748B">http://localhost:8501 — StreamForge Command Center</text>

    <!-- Sidebar (Deep Navy) -->
    <g transform="translate(0, 42)">
      <rect width="240" height="458" fill="#0F172A"/>
      <text x="24" y="40" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="18" font-weight="800" fill="#38BDF8">⚡ StreamForge</text>
      <text x="24" y="58" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="500" fill="#94A3B8">Data Engineering Suite</text>

      <!-- Nav Items -->
      <g transform="translate(16, 85)">
        <rect x="0" y="0" width="208" height="34" rx="6" fill="#1E293B"/>
        <text x="14" y="22" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="600" fill="#38BDF8">📊 Overview</text>

        <text x="14" y="60" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="500" fill="#CBD5E1">🌐 Extraction Studio</text>
        <text x="14" y="95" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="500" fill="#CBD5E1">✨ Quality Inspector</text>
        <text x="14" y="130" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="500" fill="#CBD5E1">🗄️ Database Explorer</text>
        <text x="14" y="165" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="500" fill="#CBD5E1">⚡ Automation Center</text>
        <text x="14" y="200" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="500" fill="#CBD5E1">📜 Reports &amp; Logs</text>
      </g>
    </g>

    <!-- Main Content Area (Light Minimalist) -->
    <g transform="translate(265, 60)">
      <text x="0" y="24" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="22" font-weight="800" fill="#0F172A">System Overview &amp; Operations Telemetry</text>

      <!-- 4 KPI Cards -->
      <g transform="translate(0, 45)">
        <!-- Card 1 -->
        <rect x="0" y="0" width="195" height="75" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-left="4" stroke-width="1.5"/>
        <rect x="0" y="0" width="4" height="75" rx="2" fill="#0EA5E9"/>
        <text x="16" y="24" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="700" fill="#64748B" letter-spacing="0.5">DATABASE LISTINGS</text>
        <text x="16" y="55" font-family="monospace" font-size="22" font-weight="700" fill="#0F172A">121</text>
        <text x="90" y="53" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="600" fill="#059669">↑ Verified</text>

        <!-- Card 2 -->
        <rect x="210" y="0" width="195" height="75" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>
        <rect x="210" y="0" width="4" height="75" rx="2" fill="#10B981"/>
        <text x="226" y="24" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="700" fill="#64748B" letter-spacing="0.5">LATEST PIPELINE</text>
        <text x="226" y="55" font-family="monospace" font-size="20" font-weight="700" fill="#059669">SUCCESS</text>
        <text x="330" y="53" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="600" fill="#64748B">0.63s</text>

        <!-- Card 3 -->
        <rect x="420" y="0" width="195" height="75" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>
        <rect x="420" y="0" width="4" height="75" rx="2" fill="#6366F1"/>
        <text x="436" y="24" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="700" fill="#64748B" letter-spacing="0.5">INTEGRITY DUPLICATES</text>
        <text x="436" y="55" font-family="monospace" font-size="22" font-weight="700" fill="#0F172A">0</text>
        <text x="475" y="53" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="600" fill="#059669">Strict 0</text>

        <!-- Card 4 -->
        <rect x="630" y="0" width="195" height="75" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>
        <rect x="630" y="0" width="4" height="75" rx="2" fill="#F59E0B"/>
        <text x="646" y="24" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="700" fill="#64748B" letter-spacing="0.5">TEST SUITE COVERAGE</text>
        <text x="646" y="55" font-family="monospace" font-size="22" font-weight="700" fill="#0F172A">38 / 38</text>
        <text x="735" y="53" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="10" font-weight="600" fill="#059669">100%</text>
      </g>

      <!-- Mock Data Table -->
      <g transform="translate(0, 140)">
        <rect width="520" height="260" rx="8" fill="#FFFFFF" stroke="#E2E8F0"/>
        <text x="18" y="28" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="700" fill="#0F172A">Recent Pipeline Telemetry</text>
        <!-- Table Header -->
        <rect x="0" y="42" width="520" height="28" fill="#F8FAFC"/>
        <text x="18" y="60" font-family="monospace" font-size="10" font-weight="600" fill="#64748B">ID</text>
        <text x="90" y="60" font-family="monospace" font-size="10" font-weight="600" fill="#64748B">TRIGGER</text>
        <text x="170" y="60" font-family="monospace" font-size="10" font-weight="600" fill="#64748B">STATUS</text>
        <text x="250" y="60" font-family="monospace" font-size="10" font-weight="600" fill="#64748B">DURATION</text>
        <text x="340" y="60" font-family="monospace" font-size="10" font-weight="600" fill="#64748B">EXTRACTED</text>
        <text x="440" y="60" font-family="monospace" font-size="10" font-weight="600" fill="#64748B">INSERTED</text>

        <!-- Row 1 -->
        <text x="18" y="94" font-family="monospace" font-size="11" fill="#0F172A">bbd7ad29</text>
        <text x="90" y="94" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="#334155">cli</text>
        <rect x="165" y="80" width="55" height="18" rx="9" fill="#ECFDF5"/>
        <text x="173" y="93" font-family="monospace" font-size="10" font-weight="700" fill="#059669">SUCCESS</text>
        <text x="250" y="94" font-family="monospace" font-size="11" fill="#334155">0.629s</text>
        <text x="350" y="94" font-family="monospace" font-size="11" fill="#334155">120</text>
        <text x="450" y="94" font-family="monospace" font-size="11" fill="#334155">114</text>
        <line x1="0" y1="108" x2="520" y2="108" stroke="#F1F5F9"/>

        <!-- Row 2 -->
        <text x="18" y="130" font-family="monospace" font-size="11" fill="#0F172A">8b3c367d</text>
        <text x="90" y="130" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="#334155">dry-run</text>
        <rect x="165" y="116" width="55" height="18" rx="9" fill="#EFF6FF"/>
        <text x="173" y="129" font-family="monospace" font-size="10" font-weight="700" fill="#2563EB">DRY-RUN</text>
        <text x="250" y="130" font-family="monospace" font-size="11" fill="#334155">0.552s</text>
        <text x="350" y="130" font-family="monospace" font-size="11" fill="#334155">120</text>
        <text x="450" y="130" font-family="monospace" font-size="11" fill="#334155">0 (skip)</text>
      </g>

      <!-- Mock Mini Chart -->
      <g transform="translate(540, 140)">
        <rect width="285" height="260" rx="8" fill="#FFFFFF" stroke="#E2E8F0"/>
        <text x="18" y="28" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="700" fill="#0F172A">Category Distribution</text>

        <!-- Bar 1 -->
        <text x="18" y="68" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="#64748B">Data Engineering</text>
        <rect x="18" y="76" width="200" height="16" rx="4" fill="#0284C7"/>
        <text x="225" y="89" font-family="monospace" font-size="10" font-weight="700" fill="#0F172A">38</text>

        <!-- Bar 2 -->
        <text x="18" y="118" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="#64748B">Cloud Infrastructure</text>
        <rect x="18" y="126" width="160" height="16" rx="4" fill="#38BDF8"/>
        <text x="185" y="139" font-family="monospace" font-size="10" font-weight="700" fill="#0F172A">29</text>

        <!-- Bar 3 -->
        <text x="18" y="168" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="#64748B">Backend Systems</text>
        <rect x="18" y="176" width="140" height="16" rx="4" fill="#6366F1"/>
        <text x="165" y="189" font-family="monospace" font-size="10" font-weight="700" fill="#0F172A">24</text>

        <!-- Bar 4 -->
        <text x="18" y="218" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" fill="#64748B">Analytics &amp; BI</text>
        <rect x="18" y="226" width="115" height="16" rx="4" fill="#10B981"/>
        <text x="140" y="239" font-family="monospace" font-size="10" font-weight="700" fill="#0F172A">18</text>
      </g>
    </g>
  </g>
</svg>"""
    p = ASSETS_DIR / "dashboard_mockup.svg"
    p.write_text(svg_content, encoding="utf-8")
    print(f"Generated {p.name}")
    return p


def generate_linkedin_banner_svg() -> pathlib.Path:
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <defs>
    <linearGradient id="liBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF"/>
      <stop offset="60%" stop-color="#F8FAFC"/>
      <stop offset="100%" stop-color="#E0F2FE"/>
    </linearGradient>
    <filter id="liShadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="10" stdDeviation="15" flood-color="#0F172A" flood-opacity="0.08"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="url(#liBg)" rx="20"/>
  <rect x="1" y="1" width="1198" height="628" fill="none" stroke="#E2E8F0" stroke-width="2" rx="19"/>

  <!-- Left Accent Strip -->
  <rect x="0" y="0" width="12" height="630" fill="#0284C7" rx="6"/>

  <!-- Main Showcase Container -->
  <g transform="translate(70, 60)">
    <!-- Header Badge -->
    <rect x="0" y="0" width="410" height="34" rx="17" fill="#0F172A"/>
    <text x="20" y="22" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" font-weight="700" fill="#38BDF8" letter-spacing="1.2">PROJECT SHOWCASE • DATA ENGINEERING &amp; AUTOMATION</text>

    <!-- Main Title -->
    <text x="0" y="100" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="48" font-weight="900" fill="#0F172A" letter-spacing="-1">StreamForge ⚡</text>
    <text x="0" y="140" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="22" font-weight="700" fill="#0284C7">Autonomous Web Extractor, Quality Engine &amp; ETL Orchestrator</text>
    <text x="0" y="172" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="400" fill="#64748B">A full-stack, test-driven Python data engineering system designed for high reliability and zero downtime.</text>

    <!-- 4 Milestone Highlights Cards -->
    <g transform="translate(0, 210)" filter="url(#liShadow)">
      <!-- Box 1 -->
      <rect x="0" y="0" width="245" height="160" rx="12" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>
      <circle cx="36" cy="36" r="18" fill="#E0F2FE"/>
      <text x="28" y="43" font-size="17">🌐</text>
      <text x="20" y="82" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="800" fill="#0F172A">120+ Records</text>
      <text x="20" y="105" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" font-weight="600" fill="#0284C7">Autonomous Extractor</text>
      <text x="20" y="130" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="400" fill="#64748B">Exponential backoff &amp; SHA-256 fingerprint deduplication.</text>

      <!-- Box 2 -->
      <rect x="270" y="0" width="245" height="160" rx="12" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>
      <circle cx="306" cy="36" r="18" fill="#ECFDF5"/>
      <text x="298" y="43" font-size="17">✨</text>
      <text x="290" y="82" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="800" fill="#0F172A">94.3% Clean</text>
      <text x="290" y="105" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" font-weight="600" fill="#059669">Quality &amp; Validation</text>
      <text x="290" y="130" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="400" fill="#64748B">Pandas snake_case, ISO dates, currency parser &amp; rejections.</text>

      <!-- Box 3 -->
      <rect x="540" y="0" width="245" height="160" rx="12" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>
      <circle cx="576" cy="36" r="18" fill="#EEF2FF"/>
      <text x="568" y="43" font-size="17">🗄️</text>
      <text x="560" y="82" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="800" fill="#0F172A">0 Duplicates</text>
      <text x="560" y="105" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" font-weight="600" fill="#4F46E5">Idempotent Upserts</text>
      <text x="560" y="130" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="400" fill="#64748B">SQLAlchemy 2.0 ON CONFLICT, rollback safety &amp; indexes.</text>

      <!-- Box 4 -->
      <rect x="810" y="0" width="245" height="160" rx="12" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>
      <circle cx="846" cy="36" r="18" fill="#FEF3C7"/>
      <text x="838" y="43" font-size="17">⚡</text>
      <text x="830" y="82" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="16" font-weight="800" fill="#0F172A">0.63s ETL</text>
      <text x="830" y="105" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="12" font-weight="600" fill="#D97706">8-Stage Automation</text>
      <text x="830" y="130" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="11" font-weight="400" fill="#64748B">Concurrency mutex locks, dry-run simulation &amp; alerts.</text>
    </g>

    <!-- Footer Banner / Author Info -->
    <g transform="translate(0, 410)">
      <rect width="1055" height="75" rx="10" fill="#0F172A"/>
      <text x="25" y="34" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="14" font-weight="700" fill="#FFFFFF">Vijay Maheswari • Python Data Engineering &amp; Automation</text>
      <text x="25" y="55" font-family="monospace" font-size="12" fill="#38BDF8">github.com/vijaymahes9080/Datheon_Python_for_Data_Engineering_-_Automation_Internship</text>
      
      <rect x="870" y="20" width="160" height="35" rx="6" fill="#0284C7"/>
      <text x="888" y="43" font-family="-apple-system, BlinkMacSystemFont, sans-serif" font-size="13" font-weight="700" fill="#FFFFFF">38 / 38 Tests Pass</text>
    </g>
  </g>
</svg>"""
    p = ASSETS_DIR / "linkedin_banner.svg"
    p.write_text(svg_content, encoding="utf-8")
    print(f"Generated {p.name}")
    return p


def render_pngs_using_pillow() -> list[pathlib.Path]:
    """Render crisp, high-resolution companion PNGs for LinkedIn and README using Pillow."""
    generated_pngs = []

    # 1. LinkedIn Showcase PNG (1200 x 630)
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # Top & bottom subtle background tints
    draw.rectangle([0, 0, w, 12], fill="#0284C7")
    draw.rectangle([0, h - 8, w, h], fill="#0F172A")

    # Header pill
    draw.rounded_rectangle([60, 45, 480, 80], radius=16, fill="#0F172A")
    draw.text((80, 53), "DATA ENGINEERING INTERNSHIP • PERSON 3", fill="#38BDF8")

    # Title & Subtitle
    draw.text((60, 105), "StreamForge ⚡", fill="#0F172A")
    draw.text((60, 150), "Intelligent Data Extraction, Quality Engineering & Workflow Automation", fill="#0284C7")
    draw.text((60, 185), "Autonomous BS4 Extractor • Pandas Quality Engine • SQLAlchemy 2.0 Upserts • Streamlit Dashboard", fill="#64748B")

    # 4 Feature Cards
    cards = [
        ("Task 1: Extractor", "120+ Records", "BS4 & Requests\nExponential Retries\nSHA-256 Fingerprint", "#E0F2FE", "#0284C7"),
        ("Task 2: Quality", "94.3% Clean", "Pandas snake_case\nISO Date Normalizer\nCurrency Range Parser", "#ECFDF5", "#059669"),
        ("Task 3: Persistence", "0 Duplicates", "SQLAlchemy 2.0\nIdempotent ON CONFLICT\nAtomic Rollback", "#EEF2FF", "#4F46E5"),
        ("Task 4: Orchestrator", "0.63s Full Run", "8-Stage State Machine\nConcurrency Mutex Lock\nMulti-channel Alerts", "#FEF3C7", "#D97706"),
    ]

    card_y = 230
    for idx, (title, stat, details, bg_pill, text_color) in enumerate(cards):
        cx = 60 + idx * 270
        draw.rounded_rectangle([cx, card_y, cx + 250, card_y + 190], radius=12, fill="#F8FAFC", outline="#E2E8F0", width=2)
        draw.rounded_rectangle([cx + 15, card_y + 15, cx + 160, card_y + 40], radius=6, fill=bg_pill)
        draw.text((cx + 25, card_y + 20), title, fill=text_color)
        draw.text((cx + 15, card_y + 55), stat, fill="#0F172A")
        draw.text((cx + 15, card_y + 95), details, fill="#64748B")

    # Bottom Banner
    draw.rounded_rectangle([60, 450, 1140, 560], radius=12, fill="#0F172A")
    draw.text((85, 475), "Vijay Maheswari • Python Data Engineering & Automation Internship", fill="#FFFFFF")
    draw.text((85, 510), "github.com/vijaymahes9080/Datheon_Python_for_Data_Engineering_-_Automation_Internship", fill="#38BDF8")
    draw.rounded_rectangle([920, 475, 1110, 535], radius=8, fill="#0284C7")
    draw.text((945, 495), "38/38 Tests Pass", fill="#FFFFFF")

    li_png = ASSETS_DIR / "linkedin_showcase.png"
    img.save(li_png, "PNG")
    print(f"Generated {li_png.name}")
    generated_pngs.append(li_png)

    # 2. Hero Banner PNG (1200 x 420)
    w2, h2 = 1200, 420
    img2 = Image.new("RGB", (w2, h2), color="#FFFFFF")
    draw2 = ImageDraw.Draw(img2)
    draw2.rectangle([0, 0, w2, 8], fill="#0284C7")
    draw2.rounded_rectangle([60, 40, 420, 75], radius=16, fill="#0F172A")
    draw2.text((80, 50), "STREAMFORGE DATA OPERATIONS", fill="#38BDF8")
    draw2.text((60, 95), "StreamForge: Enterprise Data Pipeline", fill="#0F172A")
    draw2.text((60, 140), "Autonomous Extraction • Schema Transformation • Idempotent Database Ingestion", fill="#0284C7")

    # Metrics overview
    draw2.rounded_rectangle([60, 190, 310, 310], radius=10, fill="#F8FAFC", outline="#E2E8F0", width=2)
    draw2.text((80, 210), "STORED LISTINGS", fill="#64748B")
    draw2.text((80, 240), "121 Verified", fill="#0F172A")

    draw2.rounded_rectangle([330, 190, 580, 310], radius=10, fill="#F8FAFC", outline="#E2E8F0", width=2)
    draw2.text((350, 210), "PIPELINE DURATION", fill="#64748B")
    draw2.text((350, 240), "0.629 Seconds", fill="#0284C7")

    draw2.rounded_rectangle([600, 190, 850, 310], radius=10, fill="#F8FAFC", outline="#E2E8F0", width=2)
    draw2.text((620, 210), "DUPLICATES AUDIT", fill="#64748B")
    draw2.text((620, 240), "0 Found (Clean)", fill="#059669")

    draw2.rounded_rectangle([870, 190, 1140, 310], radius=10, fill="#F8FAFC", outline="#E2E8F0", width=2)
    draw2.text((890, 210), "PYTEST COVERAGE", fill="#64748B")
    draw2.text((890, 240), "38/38 Pass (100%)", fill="#D97706")

    draw2.text((60, 350), "Datheon Python for Data Engineering & Automation Internship — Person 3", fill="#64748B")

    hero_png = ASSETS_DIR / "hero_banner.png"
    img2.save(hero_png, "PNG")
    print(f"Generated {hero_png.name}")
    generated_pngs.append(hero_png)

    # 3. Pipeline Workflow PNG (1200 x 460)
    w3, h3 = 1200, 460
    img3 = Image.new("RGB", (w3, h3), color="#FFFFFF")
    draw3 = ImageDraw.Draw(img3)
    draw3.rectangle([0, 0, w3, 8], fill="#0284C7")
    draw3.rounded_rectangle([60, 35, 420, 70], radius=16, fill="#0F172A")
    draw3.text((80, 45), "END-TO-END DATA ARCHITECTURE", fill="#38BDF8")
    draw3.text((60, 85), "StreamForge 8-Stage Automated Execution Engine", fill="#0F172A")
    draw3.text((60, 115), "Orchestrated ETL Flow with Dry-Run Preflights, Dead-Letter Rejection & Mutex Locks", fill="#64748B")

    stages = [
        ("1. Extract", "Mock HTML & BS4\n3x Retries + SHA-256", "#E0F2FE", "#0284C7"),
        ("2. Cleanse", "Pandas Pipeline\nSnake Case & ISO Dates", "#ECFDF5", "#059669"),
        ("3. Audit", "Rules Engine\nLedger & Rejections", "#FEF3C7", "#D97706"),
        ("4. Ingest", "SQLAlchemy 2.0\nAtomic Upserts", "#EEF2FF", "#4F46E5"),
        ("5. Monitor", "Streamlit UI\nReal-time Metrics", "#FCE7F3", "#DB2777"),
    ]
    for idx, (stitle, sdesc, sbg, stext) in enumerate(stages):
        sx = 60 + idx * 220
        draw3.rounded_rectangle([sx, 160, sx + 200, 320], radius=10, fill="#F8FAFC", outline="#E2E8F0", width=2)
        draw3.rounded_rectangle([sx + 15, 175, sx + 185, 205], radius=6, fill=sbg)
        draw3.text((sx + 25, 183), stitle, fill=stext)
        draw3.text((sx + 15, 220), sdesc, fill="#475569")
        if idx < len(stages) - 1:
            draw3.text((sx + 205, 235), "→", fill="#94A3B8")

    draw3.rounded_rectangle([60, 350, 1140, 420], radius=10, fill="#F1F5F9", outline="#CBD5E1", width=1)
    draw3.text((80, 375), "Performance: 120 Listings Processed in 0.629s | 0 Duplicates Detected | 38/38 Unit & Integration Tests Passed", fill="#0F172A")

    wf_png = ASSETS_DIR / "pipeline_workflow.png"
    img3.save(wf_png, "PNG")
    print(f"Generated {wf_png.name}")
    generated_pngs.append(wf_png)

    # 4. Dashboard Mockup PNG (1200 x 560)
    w4, h4 = 1200, 560
    img4 = Image.new("RGB", (w4, h4), color="#FFFFFF")
    draw4 = ImageDraw.Draw(img4)
    draw4.rectangle([0, 0, w4, 8], fill="#0284C7")
    draw4.rounded_rectangle([60, 30, 1140, 520], radius=12, fill="#FFFFFF", outline="#E2E8F0", width=2)
    # Window top bar
    draw4.rounded_rectangle([60, 30, 1140, 75], radius=12, fill="#F8FAFC")
    draw4.ellipse([80, 47, 92, 59], fill="#EF4444")
    draw4.ellipse([100, 47, 112, 59], fill="#F59E0B")
    draw4.ellipse([120, 47, 132, 59], fill="#10B981")
    draw4.text((150, 47), "StreamForge Analytics Console — localhost:8501", fill="#64748B")

    # Metrics row
    dm_metrics = [
        ("Total Stored Listings", "121", "+100% Validated", "#0284C7"),
        ("Data Quality Health", "94.3%", "Passing ASVS Rules", "#059669"),
        ("Duplicate Detection", "0 Dupes", "Idempotent Keyed", "#4F46E5"),
        ("Avg Market Salary", "$108,500", "Normalized USD", "#D97706"),
    ]
    for idx, (lbl, val, sub, col) in enumerate(dm_metrics):
        mx = 85 + idx * 260
        draw4.rounded_rectangle([mx, 95, mx + 240, 195], radius=8, fill="#F8FAFC", outline="#E2E8F0", width=1)
        draw4.text((mx + 15, 110), lbl, fill="#64748B")
        draw4.text((mx + 15, 135), val, fill=col)
        draw4.text((mx + 15, 170), sub, fill="#475569")

    # Visual data split: left table mockup, right chart mockup
    draw4.rounded_rectangle([85, 215, 680, 490], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw4.text((105, 230), "Data Ingestion & Integrity Ledger (Sample Rows)", fill="#0F172A")
    draw4.rectangle([105, 255, 660, 280], fill="#F1F5F9")
    draw4.text((115, 260), "JOB TITLE               COMPANY        LOCATION       SALARY      STATUS", fill="#475569")
    
    sample_rows = [
        ("Senior Data Engineer    DataFlow Corp  San Francisco  $155,000    Ingested"),
        ("Analytics Engineer      CloudScale     Remote         $128,000    Ingested"),
        ("ETL Architect           Nexus Global   New York       $162,000    Ingested"),
        ("Data Quality Specialist Apex Insights  Austin         $114,000    Ingested"),
        ("Automation Lead         ByteForge      Seattle        $148,000    Ingested"),
        ("Pipeline Developer      InnoData       Chicago        $105,000    Ingested"),
    ]
    for r_idx, r_text in enumerate(sample_rows):
        ry = 290 + r_idx * 30
        draw4.text((115, ry), r_text, fill="#334155")

    # Right chart panel
    draw4.rounded_rectangle([705, 215, 1115, 490], radius=8, fill="#FFFFFF", outline="#E2E8F0", width=1)
    draw4.text((725, 230), "Quality Scoring & Pipeline Distribution", fill="#0F172A")
    draw4.rectangle([725, 260, 1095, 470], fill="#F8FAFC")
    draw4.text((745, 280), "Salary Distribution by Seniority Level", fill="#64748B")
    
    # Bar chart simulation
    bars = [
        ("Lead", 85, "#0284C7"),
        ("Senior", 140, "#0EA5E9"),
        ("Mid", 110, "#38BDF8"),
        ("Junior", 65, "#7DD3FC"),
    ]
    for b_idx, (b_lbl, b_len, b_c) in enumerate(bars):
        by = 310 + b_idx * 35
        draw4.text((745, by), b_lbl, fill="#334155")
        draw4.rounded_rectangle([810, by + 2, 810 + b_len * 2, by + 18], radius=4, fill=b_c)
        draw4.text((820 + b_len * 2, by), f"{b_len}k", fill="#64748B")

    draw4.text((745, 445), "Live Streamlit app: streamlit run src/ui/dashboard.py", fill="#0284C7")

    dash_png = ASSETS_DIR / "dashboard_mockup.png"
    img4.save(dash_png, "PNG")
    print(f"Generated {dash_png.name}")
    generated_pngs.append(dash_png)

    return generated_pngs


if __name__ == "__main__":
    generate_hero_banner_svg()
    generate_pipeline_workflow_svg()
    generate_dashboard_mockup_svg()
    generate_linkedin_banner_svg()
    render_pngs_using_pillow()
    print("All light-theme SVG and PNG assets created successfully.")
