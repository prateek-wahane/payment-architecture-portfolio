"""Optional real-browser smoke check. Requires Playwright and a Chromium executable."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

import assistant
from agent_lab import ScriptedModel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromium", help="Use an existing Chromium binary instead of Playwright's download")
    parser.add_argument("--artifacts", type=Path, required=True)
    args = parser.parse_args()
    from playwright.sync_api import sync_playwright
    repo = Path(__file__).resolve().parents[2]
    token = "browser-test-only-token-not-for-deployment"
    servers, threads, urls = [], [], []
    args.artifacts.mkdir(parents=True, exist_ok=True)
    try:
        for device, folder in [("technical-docs", "docs"), ("project-notes", "case-studies")]:
            server = assistant.make_server("127.0.0.1", 0, token,
                                           corpus=assistant.Corpus(repo / folder, device))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            servers.append(server)
            threads.append(thread)
            urls.append(f"http://127.0.0.1:{server.server_port}")
        coordinator = assistant.make_server("127.0.0.1", 0, token, workers=urls,
            lab_model=ScriptedModel(), worker_labels=["technical_docs", "project_notes"])
        servers.append(coordinator)
        thread = threading.Thread(target=coordinator.serve_forever, daemon=True)
        thread.start()
        threads.append(thread)
        base = f"http://127.0.0.1:{coordinator.server_port}"
        with sync_playwright() as playwright:
            options = {"headless": True}
            if args.chromium:
                options["executable_path"] = args.chromium
            browser = playwright.chromium.launch(**options)
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1100})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(base)
                page.locator("#token").fill(token)
                page.locator("#submit").click()
                page.wait_for_function("document.querySelector('#status').textContent.startsWith('COMPLETED')")
                assert page.locator("#simulation").is_visible()
                assert "pass 2" in page.locator("#review").inner_text()
                assert "project_notes: available" in page.locator("#coverage").inner_text()
                assert page.locator("#answer a").count() > 0
                page.locator("#answer a").first.click()
                assert page.locator("#source-1").evaluate("e => e.open")
                with page.expect_download() as download:
                    page.locator("#download").click()
                data = json.loads(Path(download.value.path()).read_text())
                assert data["simulation"] and data["state"] == "completed"
                assert token not in json.dumps(data)
                page.screenshot(path=str(args.artifacts / "dashboard-desktop.png"), full_page=True)
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                page.screenshot(path=str(args.artifacts / "dashboard-mobile.png"), full_page=True)

                report = args.artifacts / "orchestration-results.json"
                if report.exists():
                    raise ValueError("Artifacts already contain a report; choose a new directory")
                result = subprocess.run([sys.executable, "-B", "benchmark.py", "--coordinator", base,
                                         "--limit", "3", "--output", str(report)],
                                        cwd=Path(__file__).resolve().parent,
                                        env={**os.environ, "RESEARCH_TOKEN": token},
                                        capture_output=True, text=True, timeout=30)
                assert result.returncode == 0, result.stderr
                page.locator("#report").set_input_files(str(report))
                page.wait_for_function("document.querySelector('#comparison').textContent.includes('baseline:')")
                assert "SCRIPTED SIMULATION" in page.locator("#comparison").inner_text()

                servers[1].shutdown()
                servers[1].server_close()
                page.locator("#submit").click()
                page.wait_for_function("document.querySelector('#status').textContent.startsWith('COMPLETED')")
                assert "project_notes: unavailable" in page.locator("#coverage").inner_text()
                assert "Partial source coverage" in page.locator("#status").inner_text()
                page.screenshot(path=str(args.artifacts / "dashboard-partial.png"), full_page=True)

                page.locator("#token").fill("wrong-token")
                page.locator("#submit").click()
                page.wait_for_function("document.querySelector('#status').textContent === 'Unauthorized'")
                assert not errors, errors
                print("Browser: review/followup, citations, download, mobile layout, comparison, offline source, and auth passed")
            finally:
                browser.close()
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
            if server.runs:
                for thread in server.runs.threads:
                    thread.join(timeout=5)
        for thread in threads:
            thread.join(timeout=5)


if __name__ == "__main__":
    main()
