"""
SEO Job Scraper Bot v4.1
========================
منابع شغلی رایگان:
  • Remotive.com
  • Jobicy.com
  • Arbeitnow
  • Adzuna (رایگان با API key)
  • Cloudflare Worker (Remote OK + We Work Remotely)

منابع پولی (اختیاری):
  • JSearch via RapidAPI  — پلن رایگان ۲۰۰ req/ماه

قابلیت‌های AI (اختیاری):
  • Gemini — تولید Cover Letter با دکمه زیر هر آگهی
  • OpenAI (GPT) — جایگزین Gemini
  • هر API سازگار OpenAI

ذخیره‌سازی اختیاری:
  • Google Sheets (Batch append)

متغیرهای محیطی (GitHub Secrets):
  TELEGRAM_BOT_TOKEN   — اجباری
  TELEGRAM_CHAT_ID     — اجباری
  RAPIDAPI_KEY         — اختیاری
  GSHEET_CREDENTIALS   — اختیاری (JSON سرویس اکانت)
  GSHEET_ID            — اختیاری
  CF_WORKER_URL        — اختیاری
  CF_WORKER_SECRET     — اختیاری
  AI_PROVIDER          — اختیاری: gemini | openai | custom
  AI_API_KEY           — اختیاری: کلید API هوش مصنوعی
  AI_MODEL             — اختیاری: مدل (default: gemini-2.0-flash)
  AI_BASE_URL          — اختیاری: آدرس پایه برای API سازگار OpenAI
  ADZUNA_APP_ID        — اختیاری
  ADZUNA_API_KEY       — اختیاری
"""

import html
import json
import logging
import os
import re
import time
import traceback
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

# ── Optional: Google Sheets ──────────────────────────────────────────────────
try:
    import gspread
    from google.oauth2.service_account import Credentials
    SHEETS_AVAILABLE = True
except ImportError:
    SHEETS_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
#  LOGGING
# ══════════════════════════════════════════════════════════════════════════════

# مسیر فایل‌ها نسبت به محل اسکریپت (برای جلوگیری از باگ در CI)
SCRIPT_DIR = Path(__file__).parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════════════════════

load_dotenv()

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set")
if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID not set")

RAPIDAPI_KEY       = os.environ.get("RAPIDAPI_KEY", "")
GSHEET_CREDENTIALS = os.environ.get("GSHEET_CREDENTIALS", "")
GSHEET_ID          = os.environ.get("GSHEET_ID", "")
GSHEET_SHEET_NAME  = "Jobs"

CF_WORKER_URL    = os.environ.get("CF_WORKER_URL", "")
CF_WORKER_SECRET = os.environ.get("CF_WORKER_SECRET", "")

# ── AI Config (اختیاری) ─────────────────────────────────────────────────────
AI_PROVIDER = os.environ.get("AI_PROVIDER", "").lower()       # gemini | openai | tokenlb | custom
AI_API_KEY  = os.environ.get("AI_API_KEY", "")
AI_MODEL    = os.environ.get("AI_MODEL", "gemini-2.0-flash")
AI_BASE_URL = os.environ.get("AI_BASE_URL", "")

# TokenLB: اگه provider برابر tokenlb بود، base_url خودکار ست میشه
if AI_PROVIDER == "tokenlb":
    AI_BASE_URL = "https://tokenlb.net/v1"

# ── Telegraph (اختیاری — cache token برای جلوگیری از بن شدن) ─────────────────
TELEGRAPH_TOKEN = os.environ.get("TELEGRAPH_TOKEN", "")

# ── Adzuna (اختیاری) ────────────────────────────────────────────────────────
ADZUNA_APP_ID  = os.environ.get("ADZUNA_APP_ID", "")
ADZUNA_API_KEY = os.environ.get("ADZUNA_API_KEY", "")

# ── مسیر فایل seen_jobs نسبت به اسکریپت ─────────────────────────────────────
SEEN_JOBS_FILE   = SCRIPT_DIR / "seen_jobs.txt"
MAX_SEEN_JOBS    = 3000
MAX_JOBS_PER_RUN = 20
MIN_FIT_SCORE    = 35
MAX_JOB_AGE_DAYS = 7       # ۷ روز — چون لینکدین دیرتر ایندکس می‌کنه

# ── JSearch Queries ──────────────────────────────────────────────────────────
JSEARCH_QUERIES = {
    1: ["Junior SEO remote", "Technical SEO remote", "SEO Python remote"],
    2: ["SEO Content Editor remote", "WordPress SEO Specialist remote"],
    3: ["on-page SEO specialist remote", "SEO copywriter remote"],
}

# ── مهارت‌ها (از env یا پیش‌فرض) ─────────────────────────────────────────────
_DEFAULT_SKILLS = [
    "python", "wordpress", "technical seo", "on-page seo",
    "screaming frog", "ahrefs", "semrush", "google analytics",
    "google search console", "content", "keyword research",
    "html", "cms", "link building", "schema",
]
_user_skills_env = os.environ.get("USER_SKILLS", "")
MY_SKILLS = [s.strip().lower() for s in _user_skills_env.split(",") if s.strip()] if _user_skills_env else _DEFAULT_SKILLS

# ── رزومه/پروفایل کاربر (اختیاری — AI ازش استفاده می‌کنه) ────────────────────
USER_RESUME = os.environ.get("USER_RESUME", "")

# ── کلمات ممنوعه ─────────────────────────────────────────────────────────────
BLACKLIST_KEYWORDS = [
    "us residents only", "must reside in us", "must be located in us",
    "must be based in the us", "must be based in us",
    "must be authorized to work in the us",
    "senior seo", "head of seo", "director of seo", "vp of",
    "agency", "full stack", "fullstack",
    "native english speaker only",
    "10+ years", "8+ years", "7+ years",
]

# ── کلمات تقویت‌کننده ────────────────────────────────────────────────────────
BOOST_KEYWORDS = {
    "technical seo": 20, "python": 18, "wordpress": 15,
    "junior": 18, "entry level": 15, "associate": 12,
    "seo specialist": 12, "seo editor": 12, "content editor": 10,
    "on-page": 10, "part-time": 8, "contract": 5,
    "remote-first": 8, "async": 5, "flexible": 4,
}

# ── Regex patterns برای Fit Score (word boundary) ────────────────────────────
_SKILL_PATTERNS = {skill: re.compile(r"\b" + re.escape(skill) + r"\b", re.IGNORECASE)
                   for skill in MY_SKILLS}
_BOOST_PATTERNS = {kw: re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)
                   for kw in BOOST_KEYWORDS}
_BLACKLIST_PATTERNS = {kw: re.compile(r"\b" + re.escape(kw.lower()) + r"\b", re.IGNORECASE)
                       for kw in BLACKLIST_KEYWORDS}

# ══════════════════════════════════════════════════════════════════════════════
#  AI COVER LETTER (اختیاری — Gemini / OpenAI / Custom)
# ══════════════════════════════════════════════════════════════════════════════

def ai_available() -> bool:
    """بررسی اینکه AI فعال شده یا نه"""
    return bool(AI_PROVIDER and AI_API_KEY)


def generate_cover_letter(job: dict, matched_skills: list) -> str:
    """
    تولید Cover Letter با AI — فقط بر اساس matched_skills.
    اگه AI تنظیم نشده باشه، خالی برمی‌گردونه.
    هیچوقت باعث crash نمی‌شه.
    """
    if not ai_available():
        return ""

    title   = job.get("title", "")
    company = job.get("company", "")
    desc    = (job.get("description") or "")[:1500]
    
    # فقط مهارت‌های تطابق‌یافته رو بده — نه همه MY_SKILLS
    skills_str = ', '.join(matched_skills) if matched_skills else ', '.join(MY_SKILLS[:5])

    # اگه کاربر رزومه داده، اضافه کن
    resume_section = ""
    if USER_RESUME:
        resume_section = f"\nApplicant's background: {USER_RESUME[:500]}\n"

    prompt = (
        f"Write a professional, concise cover letter for this job:\n\n"
        f"Title: {title}\n"
        f"Company: {company}\n"
        f"Description: {desc}\n\n"
        f"The applicant has these RELEVANT skills: {skills_str}\n"
        f"{resume_section}\n"
        f"Rules:\n"
        f"- Keep it under 250 words\n"
        f"- Be laser-targeted to the job requirements\n"
        f"- ONLY mention skills from the provided list that match the job\n"
        f"- If background info is provided, weave it naturally into the letter\n"
        f"- Show enthusiasm but stay professional\n"
        f"- End with a call to action\n"
        f"- Do NOT use any Markdown formatting like **bold** or *italics*. Use only plain text."
    )

    try:
        if AI_PROVIDER == "gemini":
            return _call_gemini(prompt)
        elif AI_PROVIDER in ("openai", "custom", "tokenlb"):
            return _call_openai_compatible(prompt)
        else:
            log.warning(f"Unknown AI_PROVIDER: {AI_PROVIDER}")
            return ""
    except Exception as e:
        log.error(f"AI cover letter error: {e}")
        return ""


def _call_gemini(prompt: str) -> str:
    """Google Gemini API"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{AI_MODEL}:generateContent?key={AI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
        }
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # استخراج متن از پاسخ Gemini
    candidates = data.get("candidates", [])
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        return ""
    return parts[0].get("text", "").strip()


def _call_openai_compatible(prompt: str) -> str:
    """OpenAI یا هر API سازگار (مثل Together, Groq, etc.)"""
    base_url = AI_BASE_URL or "https://api.openai.com/v1"
    url = f"{base_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": "You write professional cover letters for job applications."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    choices = data.get("choices", [])
    if not choices:
        return ""
    return choices[0].get("message", {}).get("content", "").strip()

# ══════════════════════════════════════════════════════════════════════════════
#  SEEN JOBS CACHE — OrderedDict برای حفظ ترتیب ورود
# ══════════════════════════════════════════════════════════════════════════════

def load_seen_jobs() -> OrderedDict:
    """
    بارگذاری دیتابیس آگهی‌های دیده‌شده.
    از OrderedDict استفاده می‌کنیم تا ترتیب ورود حفظ بشه
    و هنگام prune شدن، آگهی‌های قدیمی (نه جدید) حذف بشن.
    """
    seen = OrderedDict()
    if SEEN_JOBS_FILE.exists():
        for line in SEEN_JOBS_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                seen[line] = True
        log.info(f"Loaded {len(seen)} seen IDs")
    else:
        log.info("No cache — starting fresh")
    return seen


def save_seen_jobs(seen: OrderedDict) -> None:
    """
    ذخیره دیتابیس. اگه تعداد از MAX_SEEN_JOBS بیشتر بود،
    قدیمی‌ترین‌ها (اول لیست) حذف میشن — نه جدیدها.
    """
    ids = list(seen.keys())
    if len(ids) > MAX_SEEN_JOBS:
        # حذف قدیمی‌ترین‌ها (از ابتدا)
        ids = ids[-MAX_SEEN_JOBS:]
    SEEN_JOBS_FILE.write_text("\n".join(ids), encoding="utf-8")
    log.info(f"Saved {len(ids)} IDs to cache")

# ══════════════════════════════════════════════════════════════════════════════
#  FIT SCORE — با Regex word boundary (جلوگیری از false positive)
# ══════════════════════════════════════════════════════════════════════════════

def calculate_fit_score(job: dict) -> tuple:
    """برمی‌گردونه: (score: int 0-100, matched_skills: list[str])"""
    score = 0
    matched_skills = []

    title    = (job.get("title") or "").lower()
    desc     = (job.get("description") or "").lower()
    combined = f"{title} {desc}"

    # Boost keywords — با word boundary
    for kw, pts in BOOST_KEYWORDS.items():
        if _BOOST_PATTERNS[kw].search(combined):
            score += pts

    # Skills — با word boundary (جلوگیری از seo in baseon)
    for skill in MY_SKILLS:
        if _SKILL_PATTERNS[skill].search(combined):
            matched_skills.append(skill)
            score += 7

    if re.search(r"\bseo\b", title):
        score += 12
    if job.get("salary"):
        score += 10
    if job.get("remote"):
        score += 8
    if any(re.search(r"\b" + w + r"\b", title) for w in ["junior", "associate", "entry", "jr"]):
        score += 10

    return min(score, 100), matched_skills[:4]

# ══════════════════════════════════════════════════════════════════════════════
#  FREE SOURCES
# ══════════════════════════════════════════════════════════════════════════════

def fetch_remotive() -> list:
    """Remotive.com — رایگان، بدون API key"""
    endpoints = [
        "https://remotive.com/api/remote-jobs?category=seo&limit=20",
        "https://remotive.com/api/remote-jobs?search=technical+seo&limit=10",
        "https://remotive.com/api/remote-jobs?search=seo+content&limit=10",
    ]
    results = []
    for url in endpoints:
        try:
            resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            for j in resp.json().get("jobs", []):
                results.append({
                    "id":           f"remotive_{j.get('id', '')}",
                    "title":        j.get("title", ""),
                    "company":      j.get("company_name", ""),
                    "description":  j.get("description", ""),
                    "salary":       j.get("salary", ""),
                    "remote":       True,
                    "url":          j.get("url", ""),
                    "source":       "Remotive",
                    "source_emoji": "🌐",
                    "posted_at":    (j.get("publication_date") or "")[:10],
                    "location":     "Remote",
                })
        except Exception as e:
            log.error(f"Remotive error: {e}")
        time.sleep(1)
    log.info(f"Remotive -> {len(results)} jobs")
    return results


def fetch_jobicy() -> list:
    """Jobicy.com — رایگان، بدون API key"""
    endpoints = [
        "https://jobicy.com/api/v2/remote-jobs?tag=seo&count=20",
        "https://jobicy.com/api/v2/remote-jobs?tag=content-marketing&count=15",
        "https://jobicy.com/api/v2/remote-jobs?tag=wordpress&count=10",
    ]
    results = []
    for url in endpoints:
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            for j in resp.json().get("jobs", []):
                sal = ""
                lo = j.get("annualSalaryMin")
                hi = j.get("annualSalaryMax")
                cur = j.get("annualSalaryCurrency", "USD")
                if lo and hi:
                    sal = f"{cur} {int(lo):,}-{int(hi):,}/yr"
                elif lo:
                    sal = f"{cur} {int(lo):,}+/yr"
                results.append({
                    "id":           f"jobicy_{j.get('id', '')}",
                    "title":        j.get("jobTitle", ""),
                    "company":      j.get("companyName", ""),
                    "description":  j.get("jobDescription", ""),
                    "salary":       sal,
                    "remote":       True,
                    "url":          j.get("url", ""),
                    "source":       "Jobicy",
                    "source_emoji": "🟢",
                    "posted_at":    (j.get("pubDate") or "")[:10],
                    "location":     "Remote",
                })
        except Exception as e:
            log.error(f"Jobicy error: {e}")
        time.sleep(1)
    log.info(f"Jobicy -> {len(results)} jobs")
    return results


def fetch_arbeitnow() -> list:
    """Arbeitnow — رایگان، بدون API key"""
    SEO_TERMS = ["seo", "search engine optimization", "content editor",
                 "technical seo", "wordpress seo"]
    try:
        resp = requests.get(
            "https://arbeitnow.com/api/job-board-api",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.raise_for_status()
        results = []
        for j in resp.json().get("data", []):
            if not j.get("remote"):
                continue
            title = (j.get("title") or "").lower()
            desc = (j.get("description") or "").lower()[:300]
            if not any(t in title or t in desc for t in SEO_TERMS):
                continue
            results.append({
                "id":           f"arbeitnow_{j.get('slug', '')}",
                "title":        j.get("title", ""),
                "company":      j.get("company_name", ""),
                "description":  j.get("description", ""),
                "salary":       "",
                "remote":       True,
                "url":          j.get("url", ""),
                "source":       "Arbeitnow",
                "source_emoji": "🔷",
                "posted_at":    datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "location":     "Remote",
            })
        log.info(f"Arbeitnow -> {len(results)} jobs")
        return results
    except Exception as e:
        log.error(f"Arbeitnow error: {e}")
        return []


def fetch_adzuna() -> list:
    """Adzuna — رایگان با API key (اختیاری)"""
    if not ADZUNA_APP_ID or not ADZUNA_API_KEY:
        return []

    queries = ["seo", "technical seo", "seo specialist"]
    results = []

    for q in queries:
        try:
            resp = requests.get(
                f"https://api.adzuna.com/v1/api/jobs/us/search/1",
                params={
                    "app_id": ADZUNA_APP_ID,
                    "app_key": ADZUNA_API_KEY,
                    "what": q,
                    "what_or": "remote",
                    "max_days_old": 7,
                    "results_per_page": 15,
                    "content-type": "application/json",
                },
                timeout=15,
            )
            resp.raise_for_status()
            for j in resp.json().get("results", []):
                results.append({
                    "id":           f"adzuna_{j.get('id', '')}",
                    "title":        j.get("title", ""),
                    "company":      (j.get("company") or {}).get("display_name", ""),
                    "description":  j.get("description", ""),
                    "salary":       f"${int(float(j['salary_min'])):,}-${int(float(j.get('salary_max') or j.get('salary_min'))):,}/yr" if j.get("salary_min") else "",
                    "remote":       True,
                    "url":          j.get("redirect_url", ""),
                    "source":       "Adzuna",
                    "source_emoji": "🟡",
                    "posted_at":    (j.get("created") or "")[:10],
                    "location":     j.get("location", {}).get("display_name", "Remote"),
                })
        except Exception as e:
            log.error(f"Adzuna error ({q}): {e}")
        time.sleep(1)

    log.info(f"Adzuna -> {len(results)} jobs")
    return results


def fetch_findwork() -> list:
    """
    FindWork.dev — رایگان (۱۰۰ req/روز)، بدون API key.
    مخصوص شغل‌های تکنولوژی و remote.
    """
    SEO_TERMS = ["seo", "search engine", "content editor", "wordpress",
                 "technical seo", "organic", "keyword"]
    try:
        resp = requests.get(
            "https://findwork.dev/api/jobs/",
            params={"search": "seo", "remote": "true", "order_by": "-date_posted"},
            headers={"User-Agent": "Mozilla/5.0 (compatible; SEOJobBot/4.1)"},
            timeout=15,
        )
        if resp.status_code == 403:
            log.warning("FindWork.dev: access denied (may need API key in future)")
            return []
        resp.raise_for_status()
        results = []
        for j in resp.json().get("results", []):
            title = (j.get("role") or "").lower()
            desc = (j.get("text") or "").lower()[:500]
            # فیلتر بر اساس SEO terms
            if not any(t in title or t in desc for t in SEO_TERMS):
                continue
            results.append({
                "id":           f"findwork_{j.get('id', '')}",
                "title":        j.get("role", ""),
                "company":      j.get("company_name", ""),
                "description":  j.get("text", ""),
                "salary":       "",
                "remote":       j.get("remote", True),
                "url":          j.get("url", ""),
                "source":       "FindWork",
                "source_emoji": "🟣",
                "posted_at":    (j.get("date_posted") or "")[:10],
                "location":     j.get("location") or "Remote",
            })
        log.info(f"FindWork -> {len(results)} jobs")
        return results
    except Exception as e:
        log.error(f"FindWork error: {e}")
        return []


def _normalize_cf_worker_url(url: str) -> str:
    """اطمینان از اینکه URL ورکر به /jobs ختم بشه"""
    url = url.rstrip("/")
    if not url.endswith("/jobs"):
        url += "/jobs"
    return url


def fetch_cloudflare_worker() -> list:
    """Cloudflare Worker — Remote OK + We Work Remotely"""
    if not CF_WORKER_URL:
        return []

    worker_url = _normalize_cf_worker_url(CF_WORKER_URL)

    headers = {"User-Agent": "SEOJobBot/4.1"}
    if CF_WORKER_SECRET:
        headers["X-Worker-Secret"] = CF_WORKER_SECRET

    try:
        resp = requests.get(worker_url, headers=headers, timeout=20)
        if resp.status_code in (401, 404):
            log.error(f"CF Worker: {resp.status_code}")
            return []
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "ok":
            return []

        jobs = []
        for j in data.get("jobs", []):
            if not j.get("id") or not j.get("title"):
                continue
            jobs.append({
                "id":           str(j.get("id", "")),
                "title":        j.get("title", ""),
                "company":      j.get("company", ""),
                "description":  j.get("description", ""),
                "salary":       j.get("salary", ""),
                "remote":       j.get("remote", True),
                "url":          j.get("url", ""),
                "source":       j.get("source", "CF Worker"),
                "source_emoji": j.get("source_emoji", "☁️"),
                "posted_at":    (j.get("posted_at") or "")[:10],
                "location":     j.get("location", "Remote"),
            })
        log.info(f"CF Worker -> {len(jobs)} jobs")
        return jobs
    except Exception as e:
        log.error(f"CF Worker error: {e}")
        return []

# ══════════════════════════════════════════════════════════════════════════════
#  JSEARCH API (اختیاری) — با محدودیت P3 روزهای زوج
# ══════════════════════════════════════════════════════════════════════════════

def _should_run_p3() -> bool:
    """P3 queries فقط روزهای زوج اجرا میشن (صرفه‌جویی در سقف رایگان)"""
    return datetime.now(timezone.utc).day % 2 == 0


def search_jsearch(query: str) -> list:
    if not RAPIDAPI_KEY:
        return []

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
    }
    params = {
        "query": query,
        "num_pages": "1",
        "date_posted": "week",       # ۷ روز — لینکدین دیرتر ایندکس می‌کنه
        "work_from_home": "true",
    }

    for attempt in range(1, 4):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=20)
            if resp.status_code == 429:
                log.warning("JSearch rate limit — waiting 60s")
                time.sleep(60)
                continue
            if resp.status_code == 403:
                log.error("JSearch 403 — invalid key or quota exceeded")
                return []
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") != "OK":
                return []
            return [_normalize_jsearch(j) for j in data.get("data", [])]
        except requests.exceptions.Timeout:
            log.warning(f"JSearch timeout {attempt}/3")
        except Exception as e:
            log.error(f"JSearch error: {e}")
            return []
        if attempt < 3:
            time.sleep(5 * attempt)
    return []


def _normalize_jsearch(j: dict) -> dict:
    salary = ""
    if j.get("job_salary_string"):
        salary = j["job_salary_string"]
    elif j.get("job_min_salary"):
        lo = int(j["job_min_salary"])
        hi = int(j.get("job_max_salary") or lo)
        per = {"year": "/yr", "month": "/mo", "hour": "/hr"}.get(
              (j.get("job_salary_period") or "").lower(), "")
        salary = f"${lo:,}-${hi:,}{per}" if lo != hi else f"${lo:,}+{per}"

    city = j.get("job_city") or ""
    country = j.get("job_country") or ""
    # ساخت location — filter برای حذف بخش‌های خالی
    loc_parts = [p for p in (city, country) if p]
    loc = ", ".join(loc_parts) or "Remote"

    return {
        "id":           j.get("job_id", ""),
        "title":        j.get("job_title", ""),
        "company":      j.get("employer_name", ""),
        "description":  j.get("job_description", ""),
        "salary":       salary,
        "remote":       True,
        "url":          j.get("job_apply_link") or j.get("job_google_link") or "",
        "source":       j.get("job_publisher", "JSearch"),
        "source_emoji": "🔍",
        "posted_at":    (j.get("job_posted_at_datetime_utc") or "")[:10],
        "location":     loc,
    }

# ══════════════════════════════════════════════════════════════════════════════
#  FILTERS
# ══════════════════════════════════════════════════════════════════════════════

def is_blacklisted(job: dict) -> tuple:
    title = (job.get("title") or "").lower()
    desc  = (job.get("description") or "").lower()[:2000]
    text  = f"{title} {desc}"
    for kw, pattern in _BLACKLIST_PATTERNS.items():
        if pattern.search(text):
            return True, kw
    return False, ""


def is_too_old(job: dict) -> bool:
    posted = (job.get("posted_at") or "")[:10]
    if not posted:
        return False
    try:
        dt = datetime.strptime(posted, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).days > MAX_JOB_AGE_DAYS
    except Exception:
        return False

# ══════════════════════════════════════════════════════════════════════════════
#  TELEGRAM — با link_preview_options جدید
# ══════════════════════════════════════════════════════════════════════════════

def _score_bar(score: int) -> str:
    filled = round(score / 10)
    return "█" * filled + "░" * (10 - filled)


def format_job(job: dict, score: int, skills: list) -> str:
    title   = html.escape(job.get("title") or "No Title")
    company = html.escape(job.get("company") or "Unknown")
    salary  = job.get("salary") or ""
    url     = job.get("url") or ""
    source  = html.escape(job.get("source") or "")
    semoji  = job.get("source_emoji", "🌐")
    posted  = job.get("posted_at") or ""
    loc     = html.escape(job.get("location") or "Remote")

    lines = [
        f"💼 <b>{title}</b>",
        f"🏢 {company}",
        f"📍 {loc}",
    ]
    if salary:
        lines.append(f"💰 <b>{html.escape(str(salary))}</b>")
    lines.append(f"📊 {_score_bar(score)} {score}/100")
    if skills:
        lines.append(f"✅ {', '.join(html.escape(s) for s in skills)}")
    lines.append(f"{semoji} {source}")
    if posted:
        lines.append(f"📅 {posted}")
    if url:
        lines.append(f'🔗 <a href="{html.escape(url)}">Apply Now</a>')

    return "\n".join(lines)


def send_telegram(text: str, reply_markup: dict = None, _retries: int = 3) -> bool:
    """
    ارسال پیام به تلگرام — با link_preview_options جدید.
    اگه Flood Wait بخوره، منتظر میمونه و retry می‌کنه.
    """
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "link_preview_options": {"is_disabled": True},
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup

    for attempt in range(1, _retries + 1):
        try:
            resp = requests.post(api_url, json=payload, timeout=15)
            if resp.ok:
                return True

            # Flood Wait handling — تلگرام retry_after رو برمی‌گردونه
            if resp.status_code == 429:
                try:
                    retry_after = resp.json().get("parameters", {}).get("retry_after", 30)
                except Exception:
                    retry_after = 30
                log.warning(f"Telegram Flood Wait — sleeping {retry_after}s (attempt {attempt}/{_retries})")
                time.sleep(retry_after + 1)
                continue

            log.error(f"Telegram {resp.status_code}: {resp.text[:200]}")
            return False
        except requests.exceptions.Timeout:
            log.warning(f"Telegram timeout (attempt {attempt}/{_retries})")
            if attempt < _retries:
                time.sleep(3)
        except Exception as e:
            log.error(f"Telegram error: {e}")
            return False
    return False


# Telegraph token cache — یکبار ساخته میشه و بقیه استفاده می‌کنن
_telegraph_token_cache = {"token": TELEGRAPH_TOKEN}


def _get_telegraph_token() -> str:
    """
    گرفتن Telegraph access_token:
    1. اول از TELEGRAPH_TOKEN (env) استفاده می‌کنه
    2. اگه نبود، فقط یکبار اکانت می‌سازه و cache می‌کنه
    """
    if _telegraph_token_cache["token"]:
        return _telegraph_token_cache["token"]

    try:
        acc_resp = requests.post(
            "https://api.telegra.ph/createAccount",
            json={"short_name": "SEOJobBot", "author_name": "SEO Job Bot"},
            timeout=10,
        )
        acc_data = acc_resp.json()
        if acc_data.get("ok"):
            token = acc_data["result"]["access_token"]
            _telegraph_token_cache["token"] = token
            log.info(f"Telegraph account created. Save this as TELEGRAPH_TOKEN: {token}")
            return token
    except Exception as e:
        log.error(f"Telegraph createAccount error: {e}")
    return ""


def publish_to_telegraph(title: str, content: str) -> str:
    """
    پابلیش متن روی Telegra.ph.
    از token ذخیره‌شده (TELEGRAPH_TOKEN) استفاده می‌کنه — نه ساخت اکانت جدید هر بار.
    اگه ناموفق بود، خالی برمی‌گردونه.
    """
    access_token = _get_telegraph_token()
    if not access_token:
        return ""

    try:
        # ساخت محتوای HTML ساده برای Telegraph
        paragraphs = content.split("\n\n")
        nodes = []
        for para in paragraphs:
            lines = para.strip().split("\n")
            for line in lines:
                if line.strip():
                    nodes.append({"tag": "p", "children": [line.strip()]})

        # پابلیش صفحه
        page_resp = requests.post(
            "https://api.telegra.ph/createPage",
            json={
                "access_token": access_token,
                "title": title[:256],
                "content": nodes or [{"tag": "p", "children": ["No content"]}],
                "author_name": "SEO Job Bot",
            },
            timeout=10,
        )
        page_data = page_resp.json()
        if page_data.get("ok"):
            return page_data["result"]["url"]
        return ""
    except Exception as e:
        log.error(f"Telegraph publish error: {e}")
        return ""


def build_job_buttons(job: dict, cover_letter_url: str = "") -> dict:
    """
    ساخت دکمه‌های زیر هر آگهی.
    - Apply همیشه نشون داده میشه
    - Cover Letter فقط وقتی لینک Telegraph داشته باشیم
    """
    url = job.get("url", "")
    if not url:
        return {}
    rows = [[{"text": "📝 Apply", "url": url}]]

    if cover_letter_url:
        rows.append([{"text": "✍️ Cover Letter", "url": cover_letter_url}])

    return {"inline_keyboard": rows}

# ══════════════════════════════════════════════════════════════════════════════
#  GOOGLE SHEETS (اختیاری) — Batch Append
# ══════════════════════════════════════════════════════════════════════════════

def get_sheets_client():
    if not SHEETS_AVAILABLE or not GSHEET_CREDENTIALS or not GSHEET_ID:
        return None
    try:
        creds = Credentials.from_service_account_info(
            json.loads(GSHEET_CREDENTIALS),
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        log.info("Google Sheets connected")
        return gspread.authorize(creds)
    except Exception as e:
        log.error(f"Sheets auth error: {e}")
        return None


def ensure_sheet_headers(client) -> None:
    if not client:
        return
    try:
        sheet = client.open_by_key(GSHEET_ID).worksheet(GSHEET_SHEET_NAME)
        if not sheet.row_values(1):
            sheet.insert_row(
                ["Job Title", "Company", "Source", "Apply Link",
                 "Posted", "Salary", "Fit Score", "Location",
                 "Saved At (UTC)", "Status", "Cover Letter"],
                1,
            )
    except Exception as e:
        log.error(f"Sheet header error: {e}")


def batch_append_to_sheet(client, rows: list) -> None:
    """
    ارسال دسته‌ای (Batch) ردیف‌ها به Google Sheets.
    به جای یک ریکوئست به‌ازای هر آگهی، همه رو یکجا ارسال می‌کنه.
    """
    if not client or not rows:
        return
    try:
        sheet = client.open_by_key(GSHEET_ID).worksheet(GSHEET_SHEET_NAME)
        sheet.append_rows(
            rows,
            value_input_option="USER_ENTERED",
        )
        log.info(f"Batch appended {len(rows)} rows to Google Sheets")
    except Exception as e:
        log.error(f"Sheet batch append error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    log.info(f"=== SEO Job Scraper v4.1 started at {now} ===")

    seen_jobs = load_seen_jobs()
    sheets = get_sheets_client()
    ensure_sheet_headers(sheets)

    raw_jobs = []
    source_counts = {}

    # ── منابع رایگان ─────────────────────────────────────────────────────────
    free_sources = [
        (fetch_remotive, "Remotive"),
        (fetch_jobicy, "Jobicy"),
        (fetch_arbeitnow, "Arbeitnow"),
        (fetch_adzuna, "Adzuna"),
        (fetch_findwork, "FindWork"),
        (fetch_cloudflare_worker, "CF Worker"),
    ]

    for fn, name in free_sources:
        try:
            jobs = fn()
            source_counts[name] = len(jobs)
            raw_jobs.extend(jobs)
        except Exception as e:
            log.error(f"{name} failed: {e}\n{traceback.format_exc()}")
            source_counts[name] = 0

    # ── JSearch (اختیاری) — P3 فقط روزهای زوج ────────────────────────────────
    jsearch_total = 0
    for priority in sorted(JSEARCH_QUERIES.keys()):
        # P3 فقط روزهای زوج اجرا میشه (صرفه‌جویی در سقف رایگان ۲۰۰ req/ماه)
        if priority == 3 and not _should_run_p3():
            log.info("Skipping P3 JSearch queries (odd day)")
            continue
        for query in JSEARCH_QUERIES[priority]:
            try:
                jobs = search_jsearch(query)
                jsearch_total += len(jobs)
                raw_jobs.extend(jobs)
            except Exception as e:
                log.error(f"JSearch '{query}': {e}")
            time.sleep(1.5)
    source_counts["JSearch"] = jsearch_total

    # ── فیلتر + امتیازدهی ────────────────────────────────────────────────────
    seen_ids = set()
    title_keys = set()
    stats = {"blacklisted": 0, "seen": 0, "old": 0, "low_score": 0}
    qualified = []

    for job in raw_jobs:
        try:
            jid = job.get("id") or job.get("url") or ""
            title_key = f"{(job.get('title') or '').lower().strip()}|{(job.get('company') or '').lower().strip()}"

            if not jid:
                continue
            if jid in seen_jobs or jid in seen_ids:
                stats["seen"] += 1
                continue
            if title_key in title_keys:
                stats["seen"] += 1
                seen_ids.add(jid)
                seen_jobs[jid] = True
                continue

            seen_ids.add(jid)
            seen_jobs[jid] = True
            title_keys.add(title_key)

            bl, matched = is_blacklisted(job)
            if bl:
                stats["blacklisted"] += 1
                continue

            if is_too_old(job):
                stats["old"] += 1
                continue

            score, skills = calculate_fit_score(job)
            if score < MIN_FIT_SCORE:
                stats["low_score"] += 1
                continue

            qualified.append((job, score, skills))
        except Exception as e:
            log.error(f"Processing error: {e}")

    qualified.sort(key=lambda x: x[1], reverse=True)

    log.info(
        f"Qualified: {len(qualified)} | BL: {stats['blacklisted']} | "
        f"Seen: {stats['seen']} | Old: {stats['old']} | Low: {stats['low_score']}"
    )

    # ── ارسال به تلگرام ──────────────────────────────────────────────────────
    active_sources = {k: v for k, v in source_counts.items() if v > 0}
    sources_line = " | ".join(f"{k}: {v}" for k, v in active_sources.items())

    if not qualified:
        send_telegram(
            f"🔍 <b>Daily Report</b>\n📅 {now}\n\n"
            f"No qualified jobs found.\n\n"
            f"📌 {sources_line or 'No sources'}\n"
            f"⛔ {stats['blacklisted']} filtered | "
            f"📉 {stats['low_score']} low score | "
            f"🔁 {stats['seen']} duplicates | "
            f"🕐 {stats['old']} old"
        )
        save_seen_jobs(seen_jobs)
        return

    # Header message
    ai_status = "🧠 AI: ON" if ai_available() else "🧠 AI: OFF"
    send_telegram(
        f"🤖 <b>New SEO Jobs</b>\n"
        f"📅 {now}\n\n"
        f"✅ <b>{len(qualified)}</b> jobs (sorted by fit)\n"
        f"⛔ {stats['blacklisted']} filtered | "
        f"📉 {stats['low_score']} low | "
        f"🔁 {stats['seen']} dupes\n\n"
        f"📌 {sources_line}\n"
        f"{ai_status}\n"
        f"➖➖➖➖➖➖➖➖"
    )
    time.sleep(1.5)

    sent = 0
    cl_count = 0
    MAX_COVER_LETTERS = 5  # محدود کردن CL به top 5 برای صرفه‌جویی در API
    sheet_rows = []  # جمع‌آوری ردیف‌ها برای Batch ارسال به Sheets

    for job, score, skills in qualified[:MAX_JOBS_PER_RUN]:
        try:
            # تولید Cover Letter با AI (اگه فعال باشه) + پابلیش روی Telegraph
            cl_url = ""
            cl_text = ""
            if ai_available() and TELEGRAPH_TOKEN and cl_count < MAX_COVER_LETTERS:
                cl_text = generate_cover_letter(job, skills)
                if cl_text:
                    time.sleep(1)  # delay قبل از Telegraph برای جلوگیری از بن
                    cl_title = f"Cover Letter — {job.get('title', '')[:60]}"
                    cl_url = publish_to_telegraph(cl_title, cl_text)
                    if cl_url:
                        cl_count += 1
                    else:
                        log.warning(f"Telegraph publish failed for: {job.get('title', '')[:40]}")

            # ساخت inline buttons (با یا بدون لینک Cover Letter)
            buttons = build_job_buttons(job, cover_letter_url=cl_url)

            # ارسال آگهی
            msg = format_job(job, score, skills)
            if send_telegram(msg, reply_markup=buttons if buttons else None):
                sent += 1

                # جمع‌آوری ردیف برای Batch append به Sheets
                sheet_rows.append([
                    job.get("title", ""), job.get("company", ""),
                    job.get("source", ""), job.get("url", ""),
                    job.get("posted_at", ""), job.get("salary", ""),
                    score, job.get("location", ""),
                    datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
                    "New", cl_url,  # لینک Cover Letter (Telegraph)
                ])

            time.sleep(1.5)  # جلوگیری از Flood Wait تلگرام
        except Exception as e:
            log.error(f"Send error: {e}")

    # ── Batch ارسال به Google Sheets (خارج از حلقه) ───────────────────────────
    batch_append_to_sheet(sheets, sheet_rows)

    save_seen_jobs(seen_jobs)
    log.info(f"=== Done. Sent {sent}/{len(qualified)} ===")


if __name__ == "__main__":
    main()
