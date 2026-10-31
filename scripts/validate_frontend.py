"""Static assets and frontend template validation for CI pipeline."""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def validate_manifest(manifest_path: Path):
    print(f"Checking {manifest_path}...")
    assert manifest_path.exists(), f"Manifest file missing at {manifest_path}"
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    required_keys = ["name", "short_name", "start_url", "display", "icons"]
    for key in required_keys:
        assert key in data, f"Manifest missing key: {key}"
    assert len(data["icons"]) > 0, "Manifest icons must not be empty"
    print("  [OK] Manifest JSON is valid.")


def validate_icon(icon_path: Path):
    print(f"Checking {icon_path}...")
    assert icon_path.exists(), f"Icon file missing at {icon_path}"
    ET.parse(icon_path)
    print("  [OK] Icon SVG XML is well-formed.")


def validate_service_worker(sw_path: Path):
    print(f"Checking {sw_path}...")
    assert sw_path.exists(), f"Service worker missing at {sw_path}"
    with open(sw_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "CACHE_NAME" in content, "sw.js missing CACHE_NAME"
    has_install = (
        "addEventListener('install'" in content
        or 'addEventListener("install"' in content
    )
    assert has_install, "sw.js missing install listener"
    has_fetch = (
        "addEventListener('fetch'" in content
        or 'addEventListener("fetch"' in content
    )
    assert has_fetch, "sw.js missing fetch listener"
    print("  [OK] Service worker script passed sanity checks.")


def validate_index_html(html_path: Path):
    print(f"Checking {html_path}...")
    assert html_path.exists(), f"index.html missing at {html_path}"
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    required_dom_ids = [
        "screen1",
        "screen2",
        "screen3",
        "screen4",
        "todayHourlyScroll",
        "btn-ai-prediction",
        "aiPredictionModal",
        "forecast7DayScroll",
        "forecastModelPill",
        "weeklyTrendAnalysisText",
        "detailDayTitle",
        "detailRainPill",
    ]
    for dom_id in required_dom_ids:
        found = (
            f'id="{dom_id}"' in content
            or f"id='{dom_id}'" in content
            or f'class="{dom_id}"' in content
        )
        assert found, f"index.html missing required element/class: {dom_id}"

    # Check for basic JS script blocks
    scripts = re.findall(r"<script>(.*?)</script>", content, re.DOTALL)
    assert len(scripts) > 0, "index.html missing <script> block"
    print("  [OK] index.html DOM structure and script blocks are intact.")


def main():
    root = Path(__file__).resolve().parent.parent
    print("========================================")
    print(" FRONTEND & ASSET INTEGRITY VALIDATOR   ")
    print("========================================")
    validate_manifest(root / "static" / "manifest.json")
    validate_icon(root / "static" / "icon.svg")
    validate_service_worker(root / "static" / "sw.js")
    validate_index_html(root / "templates" / "index.html")
    print("========================================")
    print(" ALL FRONTEND ASSETS & TEMPLATES VALID  ")
    print("========================================")


if __name__ == "__main__":
    main()
