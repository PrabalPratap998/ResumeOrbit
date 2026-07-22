"""
LinkedIn Easy Apply automation helpers.

This module intentionally supports only a conservative "Easy Apply" flow.
Use dry_run mode first to validate reachable jobs and detect Easy Apply buttons.
"""

from __future__ import annotations

import time
from typing import Dict, List, Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _build_driver(headless: bool = True) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,1000")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    return webdriver.Chrome(options=options)


def _find_first(driver: webdriver.Chrome, selectors: List[str]) -> Optional[webdriver.remote.webelement.WebElement]:
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            return elements[0]
    return None


def _click_button_by_text(driver: webdriver.Chrome, wait: WebDriverWait, texts: List[str]) -> bool:
    for text in texts:
        xpath = (
            "//button["
            "contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
            f"'{text.lower()}')"
            "]"
        )
        buttons = driver.find_elements(By.XPATH, xpath)
        for button in buttons:
            if not button.is_displayed() or not button.is_enabled():
                continue
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            wait.until(lambda d: button.is_displayed())
            button.click()
            return True
    return False


def _dismiss_dialog_if_present(driver: webdriver.Chrome) -> None:
    dismiss = _find_first(
        driver,
        [
            "button[aria-label*='Dismiss']",
            "button[aria-label*='Close']",
            "button[data-control-name='discard_application_confirm_btn']",
        ],
    )
    if dismiss is not None:
        try:
            dismiss.click()
        except Exception:
            pass


def login_linkedin(driver: webdriver.Chrome, email: str, password: str, timeout: int = 20) -> Dict:
    wait = WebDriverWait(driver, timeout)
    driver.get("https://www.linkedin.com/login")

    try:
        email_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_input = wait.until(EC.presence_of_element_located((By.ID, "password")))
    except TimeoutException:
        return {"success": False, "message": "LinkedIn login page did not load in time."}

    email_input.clear()
    email_input.send_keys(email)
    password_input.clear()
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)

    try:
        wait.until(
            lambda d: (
                "checkpoint" in d.current_url.lower()
                or "feed" in d.current_url.lower()
                or "linkedin.com/jobs" in d.current_url.lower()
            )
        )
    except TimeoutException:
        return {
            "success": False,
            "message": "LinkedIn login timed out. Verify credentials or complete security challenge manually.",
        }

    if "checkpoint" in driver.current_url.lower():
        return {
            "success": False,
            "message": "LinkedIn requested checkpoint verification (MFA/security). Complete it manually and retry.",
        }

    return {"success": True, "message": "LinkedIn login successful."}


def apply_to_single_job(
    driver: webdriver.Chrome,
    job: Dict,
    dry_run: bool,
    timeout: int = 15,
    max_steps: int = 8,
) -> Dict:
    wait = WebDriverWait(driver, timeout)

    job_id = job.get("job_id")
    job_url = str(job.get("job_url") or "").strip()
    title = str(job.get("title") or "")
    company = str(job.get("company") or "")

    if not job_url:
        return {
            "job_id": job_id,
            "job_url": job_url,
            "title": title,
            "company": company,
            "status": "skipped",
            "message": "Missing job URL.",
        }

    driver.get(job_url)
    time.sleep(1.5)

    easy_apply = _find_first(
        driver,
        [
            "button.jobs-apply-button",
            "button[aria-label*='Easy Apply']",
            "button[aria-label*='Apply to']",
        ],
    )

    if easy_apply is None:
        return {
            "job_id": job_id,
            "job_url": job_url,
            "title": title,
            "company": company,
            "status": "skipped",
            "message": "Easy Apply button not found.",
        }

    if dry_run:
        return {
            "job_id": job_id,
            "job_url": job_url,
            "title": title,
            "company": company,
            "status": "would_apply",
            "message": "Easy Apply detected (dry run).",
        }

    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", easy_apply)
        easy_apply.click()
    except Exception as exc:
        return {
            "job_id": job_id,
            "job_url": job_url,
            "title": title,
            "company": company,
            "status": "failed",
            "message": f"Unable to click Easy Apply: {exc}",
        }

    for _ in range(max_steps):
        time.sleep(1.0)

        # If user must manually attach docs/answer questions, stop here.
        blockers = _find_first(
            driver,
            [
                "input[type='file']",
                "textarea[aria-label*='Cover letter']",
                "select",
            ],
        )
        if blockers is not None:
            _dismiss_dialog_if_present(driver)
            return {
                "job_id": job_id,
                "job_url": job_url,
                "title": title,
                "company": company,
                "status": "needs_review",
                "message": "Application has extra questions/attachments. Manual review required.",
            }

        if _click_button_by_text(driver, wait, ["submit application"]):
            return {
                "job_id": job_id,
                "job_url": job_url,
                "title": title,
                "company": company,
                "status": "applied",
                "message": "Application submitted.",
            }

        if _click_button_by_text(driver, wait, ["review", "next"]):
            continue

        break

    _dismiss_dialog_if_present(driver)
    return {
        "job_id": job_id,
        "job_url": job_url,
        "title": title,
        "company": company,
        "status": "needs_review",
        "message": "Could not auto-complete all application steps.",
    }


def auto_apply_linkedin_jobs(
    linkedin_email: str,
    linkedin_password: str,
    jobs: List[Dict],
    max_applications: int = 5,
    dry_run: bool = True,
    headless: bool = True,
) -> Dict:
    if not linkedin_email or not linkedin_password:
        return {
            "success": False,
            "message": "LinkedIn credentials are required.",
            "results": [],
            "summary": {},
        }

    max_applications = max(1, int(max_applications or 1))
    candidate_jobs = [job for job in jobs if "linkedin.com" in str(job.get("job_url", "")).lower()]

    if not candidate_jobs:
        return {
            "success": False,
            "message": "No LinkedIn job URLs were provided.",
            "results": [],
            "summary": {},
        }

    driver = _build_driver(headless=headless)
    results: List[Dict] = []

    try:
        login_result = login_linkedin(driver, linkedin_email, linkedin_password)
        if not login_result.get("success"):
            return {
                "success": False,
                "message": login_result.get("message", "LinkedIn login failed."),
                "results": [],
                "summary": {},
            }

        applied_count = 0
        for job in candidate_jobs:
            if applied_count >= max_applications:
                break

            result = apply_to_single_job(driver, job, dry_run=dry_run)
            results.append(result)

            if result.get("status") in {"applied", "would_apply"}:
                applied_count += 1

        summary = {
            "total_candidates": len(candidate_jobs),
            "processed": len(results),
            "applied": len([r for r in results if r.get("status") == "applied"]),
            "would_apply": len([r for r in results if r.get("status") == "would_apply"]),
            "needs_review": len([r for r in results if r.get("status") == "needs_review"]),
            "skipped": len([r for r in results if r.get("status") == "skipped"]),
            "failed": len([r for r in results if r.get("status") == "failed"]),
            "dry_run": bool(dry_run),
        }

        return {
            "success": True,
            "message": "Auto-apply run completed.",
            "results": results,
            "summary": summary,
        }
    finally:
        try:
            driver.quit()
        except Exception:
            pass
