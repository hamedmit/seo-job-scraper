# 🤖 ربات یابنده شغل ریموت (Remote Job Scraper Bot)

این ربات هر روز آگهی‌های شغلی ریموت و دورکاری رو از سایت‌های مختلف پیدا می‌کنه و مستقیم به تلگرامت می‌فرسته.

**کاملاً رایگانه و هیچ نیازی به خرید سرور یا هاست نداری.** ربات روی GitHub Actions به صورت خودکار اجرا میشه.

> 💡 این ربات الان روی **SEO** تنظیم شده، ولی با چند تغییر ساده می‌تونی برای **هر فیلد شغلی** ازش استفاده کنی.

---

## ✨ چیکار می‌کنه؟

- 🔍 هر روز از **۶+ سایت کاریابی** آگهی‌های ریموت رو جمع می‌کنه
- 📊 آگهی‌ها رو **امتیازدهی** می‌کنه و فقط مرتبط‌ترین‌ها رو می‌فرسته
- ⛔ آگهی‌های نامرتبط رو **خودکار فیلتر** می‌کنه
- 🤖 هر آگهی یک دکمه **"ChatGPT Cover Letter"** داره — کلیک → باز شدن ChatGPT با پرامپت آماده
- ⏰ هر روز صبح **خودش اجرا میشه** — کاری نباید بکنی

---

## 🚀 راه‌اندازی قدم به قدم

### 📌 قدم ۱: Fork کردن پروژه

1. روی دکمه **Fork** بالا سمت راست کلیک کن
2. دکمه سبز **Create Fork** رو بزن
3. حالا یک کپی از پروژه توی اکانت GitHub خودت داری

---

### 📌 قدم ۲: ساخت ربات تلگرام

**۲.۱ ساخت ربات:**

1. تو تلگرام، `BotFather@` رو سرچ کن و باهاش پیام بده
2. بنویس: `/newbot`
3. یک اسم برای رباتت انتخاب کن (مثلاً: `SEO Job Finder`)
4. یک username برای رباتت انتخاب کن (باید با `bot` تموم بشه، مثلاً: `seo_job_finder_bot`)
5. BotFather یک **Token** بهت میده شبیه این: `7812345678:AAFxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **این Token رو کپی کن!**

**۲.۲ گرفتن Chat ID:**

1. تو تلگرام، `userinfobot@` رو سرچ کن و باهاش پیام بده
2. بهت یک عدد میده (مثلاً: `123456789`)
   - **این Chat ID رو هم کپی کن!**

**اگه می‌خوای آگهی‌ها بیاد توی یک کانال تلگرام:**

1. برو به کانالت و روی اسم کانال کلیک کن
2. بخش **Info** → **Management** → **Add Administrator**
3. رباتت رو اضافه کن
4. به رباتت دسترسی **Post Messages** بده
5. از کانالت یک پیام بفرست به `@userinfobot` یا `@raw_userinfobot`
6. Chat ID کانال رو بهت میده (شبیه: `-1001234567890`)

---

### 📌 قدم ۳: وارد کردن تنظیمات در GitHub

**۳.۱ رفتن به بخش Secrets:**

1. توی صفحه ریپوی خودت، روی تب **Settings** کلیک کن
2. از منوی سمت چپ: **Secrets and variables** → **Actions** → **New repository secret**

**۳.۲ اضافه کردن هر Secret:**

برای هر کدام از این موارد، دکمه **New repository secret** رو بزن و Name و Value رو وارد کن:

| Name | Value | توضیح |
|------|-------|-------|
| `TELEGRAM_BOT_TOKEN` | Token ربات (از BotFather) | **اجباری** |
| `TELEGRAM_CHAT_ID` | Chat ID عددی یا کانال | **اجباری** |
| `RAPIDAPI_KEY` | کلید RapidAPI (اختیاری) | برای JSearch |
| `CF_WORKER_URL` | آدرس Cloudflare Worker (اختیاری) | برای Remote OK + We Work Remotely |
| `USER_SKILLS` | مهارت‌های تو (اختیاری) | مثلاً: `python, wordpress, seo` |
| `CL_PROMPT` | پرامپت Cover Letter (اختیاری) | پیش‌فرض: prompt.txt |
| `GSHEET_CREDENTIALS` | JSON سرویس اکانت گوگل (اختیاری) | برای ذخیره در شیت |
| `GSHEET_ID` | ID شیت گوگل (اختیاری) | برای ذخیره در شیت |
| `ADZUNA_APP_ID` | App ID آدزونا (اختیاری) | سایت کاریابی |
| `ADZUNA_API_KEY` | API Key آدزونا (اختیاری) | سایت کاریابی |

---

### 📌 قدم ۴: فعال کردن GitHub Actions

1. برو به تب **Actions** (کنار Pull requests)
2. روی پیام سبز **I understand my workflows...** کلیک کن
3. از منوی سمت چپ، روی **Job Search Bot** کلیک کن
4. سمت راست، دکمه **Run workflow** رو بزن
5. دکمه سبز **Run workflow** رو دوباره بزن

✅ **بعد ۱-۲ دقیقه اولین آگهی‌ها توی ربات تلگرامت میاد!**

از فردا، ربات **هر روز صبح اتوماتیک** اجرا میشه.

---

## ☁️ قدم ۵: راه‌اندازی Cloudflare Worker (اختیاری)

اگه این مرحله رو انجام بدی، آگهی‌های **Remote OK** و **We Work Remotely** هم اضافه میشه.

**۵.۱ ساخت اکانت Cloudflare:**

1. برو به [dash.cloudflare.com](https://dash.cloudflare.com)
2. با ایمیلت ثبت‌نام کن (رایگان)

**۵.۲ ساخت Worker:**

1. توی داشبورد Cloudflare، از منوی سمت چپ: **Workers & Pages**
2. دکمه **Create Application** رو بزن
3. **Create Worker** رو انتخاب کن
4. یک اسم برای Worker بذار (مثلاً: `seo-job-bot`)
5. دکمه **Deploy** رو بزن

**۵.۳ وارد کردن کد:**

1. روی **Edit Code** کلیک کن
2. همه کدهای داخل ویرایشگر رو پاک کن
3. فایل `cf_worker.js` از این ریپو رو باز کن و **همه محتواش** رو کپی کن
4. کد رو paste کن
5. دکمه **Save and Deploy** رو بزن

**۵.۴ کپی کردن URL:**

1. بعد از Deploy شدن، یک URL میبینی شبیه:
   `https://seo-job-bot.your-subdomain.workers.dev`
2. این URL رو کپی کن
3. توی GitHub Secrets اضافه کن:
   - Name: `CF_WORKER_URL`
   - Value: `https://seo-job-bot.your-subdomain.workers.dev/jobs`

---

## 📊 قدم ۶: راه‌اندازی Google Sheets (اختیاری)

اگه می‌خوای همه آگهی‌ها توی یک شیت گوگل ذخیره بشن:

**۶.۱ ساخت پروژه در Google Cloud:**

1. برو به [console.cloud.google.com](https://console.cloud.google.com)
2. دکمه **Select a project** → **New Project**
3. یک اسم بذار و **Create** بزن

**۶.۲ فعال کردن APIها:**

1. از منوی سمت چپ: **APIs & Services** → **Library**
2. این دو تا رو جستجو کن و فعال کن:
   - **Google Sheets API**
   - **Google Drive API**

**۶.۳ ساخت Service Account:**

1. **APIs & Services** → **Credentials** → **Create Credentials** → **Service Account**
2. یک اسم بذار و **Create and continue** بزن
3. نقش رو **Editor** بذار و **Done** بزن
4. روی سرویس اکانتت کلیک کن
5. تب **Keys** → **Add Key** → **Create new key** → **JSON** → **Create**
6. فایل JSON دانلود میشه — **محتواش رو کپی کن**

**۶.۴ ساخت شیت گوگل:**

1. برو به [sheets.google.com](https://sheets.google.com)
2. دکمه **+** رو بزن تا یک شیت جدید بسازه
3. یک اسم بذار (مثلاً: `SEO Jobs`)
4. دکمه **Share** رو بزن
5. ایمیل Service Account رو وارد کن (از فایل JSON، فیلد `client_email`)
6. نقش رو **Editor** بذار و **Done** بزن

**۶.۵ پیدا کردن ID شیت:**

1. از URL شیت، بخش بعد از `/d/` تا قبل از `/edit` رو کپی کن
   - مثلاً URL هست: `https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OlbNiP_Tr/edit`
   - پس ID هست: `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OlbNiP_Tr`

**۶.۶ اضافه کردن Secrets:**

توی GitHub Secrets اضافه کن:
- Name: `GSHEET_CREDENTIALS` → Value: کل محتوای فایل JSON
- Name: `GSHEET_ID` → Value: ID شیت

---

## 🤖 Cover Letter با ChatGPT (رایگان!)

هر آگهی یک دکمه **"ChatGPT Cover Letter"** داره:

1. روی دکمه کلیک کن
2. ChatGPT باز میشه با پرامپت آماده
3. شما توی اکانت خودت Cover Letter می‌نویسی

**نیازی به API key نیست!** از اکانت رایگان ChatGPT خودت استفاده می‌کنی.

### سفارشی‌سازی پرامپت

فایل `prompt.txt` رو ویرایش کن:

```
Write a professional, concise cover letter for the '{title}' position at '{company}'.
Focus on my technical SEO skills.

Job link: {url}

Keep it under 250 words, be targeted to the job requirements, and end with a call to action.
```

متغیرهای موجود: `{title}`، `{company}`، `{url}`

---

## 🎯 سفارشی‌سازی برای فیلدهای شغلی دیگه

### ۱. عبارات جستجو (`JSEARCH_QUERIES`)

فایل `bot.py` رو باز کن و بخش `JSEARCH_QUERIES` رو تغییر بده:

```python
# نمونه SEO (پیش‌فرض):
JSEARCH_QUERIES = {
    1: ["Junior SEO remote", "Technical SEO remote", "SEO Python remote"],
    2: ["SEO Content Editor remote", "WordPress SEO Specialist remote"],
    3: ["on-page SEO specialist remote", "SEO copywriter remote"],
}

# نمونه Front-end Developer:
JSEARCH_QUERIES = {
    1: ["Junior Frontend Developer remote", "React Developer remote"],
    2: ["Vue.js Developer remote", "JavaScript Developer remote"],
    3: ["UI Developer remote", "Frontend Engineer remote"],
}
```

> 💡 عدد ۱ = هر روز، عدد ۲ = هر روز، عدد ۳ = فقط روزهای زوج

### ۲. مهارت‌های شما (`USER_SKILLS`)

توی GitHub Secrets یک Secret جدید بساز:
- Name: `USER_SKILLS`
- Value: مهارت‌هات رو comma-separated بنویس

```
react, javascript, typescript, css, html, tailwind, next.js, git, figma
```

### ۳. کلمات ممنوعه (`BLACKLIST_KEYWORDS`)

آگهی‌هایی که این کلمات رو دارن حذف میشن:

```python
BLACKLIST_KEYWORDS = [
    "us residents only", "must reside in us", "must be located in us",
    "must be based in the us", "must be authorized to work in the us",
    "native english speaker only",
    "10+ years", "8+ years", "7+ years",
    "senior", "lead", "staff", "principal", "director", "head of", "vp of",
]
```

### ۴. کلمات تقویت‌کننده (`BOOST_KEYWORDS`)

آگهی‌هایی که این کلمات رو دارن امتیاز بیشتر می‌گیرن:

```python
BOOST_KEYWORDS = {
    "technical seo": 20, "python": 18, "wordpress": 15,
    "junior": 18, "entry level": 15, "associate": 12,
    "seo specialist": 12, "seo editor": 12, "content editor": 10,
    "on-page": 10, "part-time": 8, "contract": 5,
    "remote-first": 8, "async": 5, "flexible": 4,
}
```
## 🔍 راه اندازی موتور پیشرفته JSearch via RapidAPI (اختیاری)

ربات به طور پیش فرض از منابع رایگان (مثل Remotive و Jobicy) استفاده میکند. اما منابع رایگان فقط اگهی هایی را نشان میدهند که کارفرما مستقیما در خود ان بوردها ثبت کرده باشد. اگر میخواهید ربات تمام سطح وب شامل لینکدین (LinkedIn)، ایندید (Indeed)، زیپ ریکروتر و دایرکتوری های شرکتی را شخم بزند، باید موتور JSearch را روشن کنید.

این موتور از طریق سرویس RapidAPI به سیستم هوشمند Google for Jobs متصل میشود و بالاترین نرخ پوشش اگهی های ریموت در دنیا را دارد.

### ⚠️ قوانین و محدودیت های پلن رایگان:
* پلن رایگان این ای پی ای محدودیت ۲۰ micro-requests یا همان ۲۰۰ درخواست در ماه را دارد.
* مدیریت مصرف بودجه: ربات به صورت هوشمند برای جلوگیری از تمام شدن زودتر از موعد لیمیت، کوئری های اولویت ۳ (Priority 3) را فقط در روزهای زوج سال اجرا میکند تا کلید شما تا اخر ماه دوام بیاورد.

### 🛠️ مراحل قدم به قدم دریافت کلید RAPIDAPI_KEY

۱. **ساخت اکانت:** به سایت [rapidapi.com](https://rapidapi.com) بروید و یک حساب کاربری رایگان بسازید.
۲. **یافتن سرویس:** در باکس جستجوی بالای سایت، عبارت **JSearch** را سرچ کنید و وارد صفحه اختصاصی این API شوید.
۳. **فعال سازی پلن رایگان:** روی تب **Pricing** کلیک کنید و پلن **Basic** (که 200 درخواست رایگان در ماه میدهد) را Subscribe کنید. برای فعال سازی این پلن رایگان نیازی به وارد کردن مشخصات کارت اعتباری نیست.
۴. **کپی کردن کلید اختصاصی:** به تب **Endpoints** برگردید. در منوی سمت راست صفحه و در بخش Request Headers، کدی که در ردیف `x-rapidapi-key` قرار دارد را به طور کامل کپی کنید.

### 🔐 تزریق کلید به گیت هاب (GitHub Secrets)

وارد صفحه ریپازیتوری خود در گیت هاب شوید و مراحل زیر را بروید:
1. به تب **Settings** بروید.
2. از منوی سمت چپ گزینه **Secrets and variables** و سپس **Actions** را انتخاب کنید.
3. روی دکمه **New repository secret** کلیک کنید.
4. اطلاعات را به این صورت وارد کنید:
   * **Name:** `RAPIDAPI_KEY`
   * **Value:** کلید کپی شده از سایت RapidAPI را اینجا پیست کنید.

پس از ذخیره، در اجرای بعدی ربات (یا اجرای دستی ورک فلو)، اسکریپت به طور خودکار وجود کلید را تشخیص داده و خروجی های عمیق گوگل را به تلگرام شما میفرستد.
---

## ❓ مشکلات رایج

| مشکل | راه‌حل |
|------|--------|
| پیام نمیاد | Actions → آخرین run → لاگ رو بخون |
| Token not set | Secret رو چک کن — اسمش دقیقاً درست باشه |
| آگهی کم میاد | طبیعیه! ممکنه بعضی روزها آگهی جدید نباشه |
| Cover Letter کار نمی‌کنه | مطمئن شو لینک آگهی معتبر باشه |
| آگهی‌های نامرتبط میاد | `BOOST_KEYWORDS` و `BLACKLIST_KEYWORDS` رو تنظیم کن |

---

## 📄 لایسنس

MIT — هر کاری می‌خوای باهاش بکن ✌️
