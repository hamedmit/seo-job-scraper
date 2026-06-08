# 🤖 SEO Job Scraper Bot

ربات اتوماتیک جستجوی شغل SEO ریموت — هر ۶ ساعت آگهی‌های جدید رو پیدا می‌کنه و به تلگرام می‌فرسته.

---

## ✨ قابلیت‌ها

- 🔍 جستجو از **۶+ منبع رایگان** (Remotive, Jobicy, Arbeitnow, Adzuna, FindWork, CF Worker)
- 🧠 تولید **Cover Letter با هوش مصنوعی** (Gemini/OpenAI) + لینک خواندنی
- 📊 **امتیازدهی هوشمند** بر اساس مهارت‌ها و کلمات کلیدی
- ⛔ **فیلتر خودکار** آگهی‌های نامرتبط (سنیور، آژانس، محدود به آمریکا...)
- 📋 ذخیره در **Google Sheets** (اختیاری)
- ⏰ اجرای خودکار با **GitHub Actions** (رایگان)

---

## 🚀 راه‌اندازی قدم‌به‌قدم (مبتدی‌پسند)

### مرحله ۱: ساخت ربات تلگرام (۲ دقیقه)

1. تلگرام رو باز کن
2. `@BotFather` رو سرچ کن و بهش پیام بده
3. بنویس: `/newbot`
4. یه اسم بده (مثلاً: `My SEO Job Bot`)
5. یه username بده (مثلاً: `my_seo_jobs_bot`)
6. BotFather یه **Token** بهت میده — کپی کن (شبیه اینه: `123456:ABC-DEF...`)

### مرحله ۲: پیدا کردن Chat ID (۱ دقیقه)

1. به ربات `@userinfobot` تو تلگرام پیام بده
2. عدد **Id** که نشون میده رو کپی کن (مثلاً: `123456789`)

### مرحله ۳: آپلود پروژه به GitHub (۵ دقیقه)

> GitHub یه سایته که کد رو ذخیره می‌کنه و می‌تونه بصورت خودکار اجراش کنه (رایگان).

1. اگه اکانت GitHub نداری → برو به [github.com](https://github.com) و ثبت‌نام کن
2. بعد لاگین، روی دکمه **+** (بالا سمت راست) بزن → **New repository**
3. اسم: `seo-job-scraper` | نوع: **Private** | بزن **Create repository**
4. فایل‌های زیر رو آپلود کن (دکمه "uploading an existing file"):
   - `bot.py`
   - `requirements.txt`
   - `.github/workflows/run.yml`
   - `cf_worker.js` (اختیاری — فقط اگه Cloudflare Worker می‌خوای)

### مرحله ۴: تنظیم Secrets (متغیرهای محرمانه) — ۳ دقیقه

> Secrets جایی هستن که Token و کلیدها رو امن ذخیره می‌کنی.

1. تو ریپازیتوری GitHub، برو به **Settings** (تب بالا)
2. منوی چپ: **Secrets and variables** → **Actions**
3. دکمه **New repository secret** رو بزن
4. این دو تا رو **حتماً** اضافه کن:

| Name | Value | توضیح |
|------|-------|-------|
| `TELEGRAM_BOT_TOKEN` | Token از BotFather | اجباری |
| `TELEGRAM_CHAT_ID` | عدد Chat ID | اجباری |

5. اینا **اختیاری** هستن (اگه بخوای):

| Name | Value | توضیح |
|------|-------|-------|
| `AI_PROVIDER` | `gemini` | فعال‌سازی Cover Letter هوشمند |
| `AI_API_KEY` | کلید Gemini | از [aistudio.google.com](https://aistudio.google.com/apikey) بگیر (رایگان) |
| `RAPIDAPI_KEY` | کلید RapidAPI | برای JSearch (لینکدین) — [rapidapi.com](https://rapidapi.com) |
| `ADZUNA_APP_ID` | App ID | از [developer.adzuna.com](https://developer.adzuna.com) |
| `ADZUNA_API_KEY` | API Key | همراه ADZUNA_APP_ID |
| `CF_WORKER_URL` | آدرس Worker | اگه Cloudflare Worker راه‌اندازی کردی |
| `CF_WORKER_SECRET` | رمز Worker | امنیت Worker |
| `TELEGRAPH_TOKEN` | توکن Telegraph | جلوگیری از بن شدن (توضیح پایین) |
| `GSHEET_CREDENTIALS` | JSON سرویس اکانت | برای Google Sheets |
| `GSHEET_ID` | ID شیت | از URL شیت |

### مرحله ۵: فعال‌سازی اجرای خودکار — ۱ دقیقه

1. تو ریپازیتوری GitHub، برو به تب **Actions** (بالا)
2. اگه پیام "I understand my workflows" دیدی، تأییدش کن
3. تمام! ربات **هر ۶ ساعت** خودکار اجرا میشه ✅

> 💡 برای اجرای دستی: Actions → "SEO Job Scraper" → "Run workflow" → "Run workflow"

---

## 🧠 Cover Letter هوشمند (اختیاری)

اگه `AI_PROVIDER` و `AI_API_KEY` رو ست کنی، زیر هر آگهی یه دکمه **✍️ Cover Letter** اضافه میشه که یه لینک Telegra.ph بازه با متن Cover Letter سفارشی.

### ارائه‌دهنده‌های پشتیبانی‌شده

| AI_PROVIDER | توضیح | مدل پیش‌فرض |
|-------------|--------|-------------|
| `gemini` | Google Gemini — رایگان | `gemini-2.0-flash` |
| `tokenlb` | TokenLB — Claude, GPT و مدل‌های پریمیوم | `claude-sonnet-4` |
| `openai` | OpenAI مستقیم | `gpt-4o-mini` |
| `custom` | هر API سازگار با OpenAI | — |

### گزینه ۱: Gemini (رایگان)
1. برو به [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. لاگین با Google
3. کلید رو کپی کن
4. تو Secrets اضافه کن: `AI_API_KEY` = کلید، `AI_PROVIDER` = `gemini`

### گزینه ۲: TokenLB (مدل‌های پریمیوم)
با [TokenLB](https://tokenlb.net/sign-up?aff=yNLD) میتونی از Claude, GPT-4.1 و بقیه مدل‌های پریمیوم استفاده کنی.
1. ثبت‌نام در [tokenlb.net](https://tokenlb.net/sign-up?aff=yNLD)
2. کلید API بگیر
3. Secrets:
   - `AI_PROVIDER` = `tokenlb`
   - `AI_API_KEY` = کلید TokenLB
   - `AI_MODEL` = `claude-sonnet-4-6` (یا `gpt-5.5`, `claude-opus-4-7`, ...)

### گزینه ۳: Custom (هر سرویس سازگار با OpenAI)
اگه سرویس دیگه‌ای داری که با API استاندارد OpenAI سازگاره:
- `AI_PROVIDER` = `custom`
- `AI_BASE_URL` = آدرس API (مثلاً `https://api.example.com/v1`)
- `AI_API_KEY` = کلید
- `AI_MODEL` = نام مدل

---

## 📰 Telegraph Token (توصیه میشه)

ربات برای نمایش Cover Letter از Telegra.ph استفاده می‌کنه. بدون `TELEGRAPH_TOKEN`، هر run یه اکانت جدید می‌سازه که باعث بن شدن IP میشه!

**روش دریافت (فقط یکبار):**
1. اولین بار ربات رو اجرا کن (بدون TELEGRAPH_TOKEN)
2. تو لاگ Actions یه پیام مثل این می‌بینی:
   ```
   Telegraph account created. Save this as TELEGRAPH_TOKEN: abc123xyz...
   ```
3. اون مقدار رو کپی کن و به عنوان Secret اضافه کن: `TELEGRAPH_TOKEN`
4. از این به بعد ربات از همون اکانت استفاده می‌کنه ✅

---

## ☁️ Cloudflare Worker (اختیاری — منابع بیشتر)

Worker یه اسکریپت رایگانه که از Remote OK و We Work Remotely آگهی جمع می‌کنه.

**راه‌اندازی (۱۰ دقیقه):**

1. برو به [dash.cloudflare.com](https://dash.cloudflare.com) — ثبت‌نام رایگان
2. منوی چپ: **Workers & Pages** → **Create**
3. اسم بده: `seo-job-worker` → **Deploy**
4. بعد Deploy، دکمه **Edit Code** رو بزن
5. محتوای فایل `cf_worker.js` رو کپی-پیست کن
6. بالا سمت راست: **Save and deploy**
7. URL که بهت میده (مثلاً `https://seo-job-worker.YOUR-NAME.workers.dev`) رو کپی کن
8. تو GitHub Secrets اضافه کن: `CF_WORKER_URL` = اون URL

**امنیت Worker (توصیه میشه):**
1. تو Cloudflare: Workers → سمت چپ **Settings** → **Variables**
2. یه Environment Variable اضافه کن: `WORKER_SECRET` = یه رمز دلخواه
3. تو GitHub Secrets: `CF_WORKER_SECRET` = همون رمز

---

## 📋 Google Sheets (اختیاری)

برای ذخیره تاریخچه آگهی‌ها تو Google Sheets:

1. برو به [console.cloud.google.com](https://console.cloud.google.com)
2. یه پروژه بساز → APIs & Services → Enable: **Google Sheets API** + **Google Drive API**
3. Credentials → Create → **Service Account** → کلید JSON دانلود کن
4. یه Google Sheet بساز و Email سرویس اکانت رو Editor اضافه کن
5. تو Secrets:
   - `GSHEET_CREDENTIALS` = محتوای فایل JSON
   - `GSHEET_ID` = بخش بعد از `/d/` در URL شیت

---

## 📁 ساختار فایل‌ها

```
seo-job-scraper/
├── bot.py                    ← کد اصلی ربات
├── requirements.txt          ← پکیج‌های پایتون
├── cf_worker.js              ← اسکریپت Cloudflare Worker
├── .github/workflows/run.yml ← زمان‌بندی GitHub Actions
├── .env.example              ← نمونه متغیرهای محیطی
├── setup_wizard.html         ← ابزار کمکی تنظیمات
└── seen_jobs.txt             ← کش آگهی‌ها (خودکار ساخته میشه)
```

---

## ❓ مشکلات رایج

| مشکل | راه‌حل |
|------|--------|
| ربات پیام نمیده | Actions → آخرین run رو باز کن → لاگ رو بخون |
| "TELEGRAM_BOT_TOKEN not set" | Secret رو چک کن — اسمش دقیقاً `TELEGRAM_BOT_TOKEN` باشه |
| آگهی کم پیدا میشه | `MIN_FIT_SCORE` رو تو bot.py کمتر کن (مثلاً ۲۵) |
| Cover Letter نداره | `AI_PROVIDER` و `AI_API_KEY` ست شدن؟ |
| Worker کار نمی‌کنه | URL رو تو مرورگر تست کن: `YOUR_URL/jobs` |

---

## 📄 لایسنس

MIT — هر کاری می‌خوای باهاش بکن ✌️



