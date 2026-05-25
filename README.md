
# 🤖 SerialComplainer

> *An automated complaint bot that monitors UK service outages and bad weather, generates witty tweets using a local LLaMA 3 model, and posts them to X (Twitter) every 6 hours — headlessly, on your own machine.*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production](https://img.shields.io/badge/status-production-green.svg)]()

**No cloud costs. No API fees. Just persistent Chrome profiles and email alerts when manual login is needed.**

---

## 📋 Table of Contents

- [What It Does](#-what-it-does)
- [System Requirements](#-system-requirements)
- [Demo – Profile State Machine](#-demo--profile-state-machine)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [How It Works (State Machine)](#-how-it-works-state-machine)
- [Deep Dive – Design Decisions](#-deep-dive--design-decisions)
- [Setup (macOS / Linux)](#-setup-macos--linux)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Author](#author)

---

## 📌 What It Does

| Capability | Description |
|------------|-------------|
| **Scrape Downdetector** | Real‑time service outages (e.g., Virgin Media, Apex Legends, Google) |
| **Scrape weather.com** | UK city weather with **historical temperature thresholds** (compares current temp/humidity to seasonal averages) |
| **Local LLM inference** | Uses `llama-cpp-python` with a LLaMA 3 8B model – no external API calls |
| **Tweet generation** | Random tone selection (sarcastic, existential, passive‑aggressive, British humour, etc.) |
| **Post to X** | Uses a **persistent Chrome profile** to stay logged in; headless mode after first login |
| **Scheduled execution** | Runs every 6 hours via `cron` (or manually) |
| **Email alerts** | Sends SMTP notifications when the Chrome profile is missing or expired |

---

## 💻 System Requirements

| Component | Minimum |
|-----------|---------|
| **OS** | macOS (Intel/Apple Silicon) or Linux (Ubuntu 20.04+) |
| **RAM** | 8GB total (6GB usable for the model) |
| **Disk space** | 5GB free (model + Chrome profile + logs) |
| **Chrome browser** | Latest stable version installed |
| **Python** | 3.11 or higher |

---

## 🎬 Demo – Profile State Machine

The bot autonomously manages its own login session. Replace the placeholder images in `docs/` with your own screenshots/GIFs.

| State | Behaviour | Demo |
|-------|-----------|------|
| **Profile missing** | First run – no profile folder. Sends email alert, creates `.need_refresh` flag, exits. | `![missing](docs/demo_missing.png)` |
| **Profile expired** | Profile exists but X session invalid (login page detected). Sends email alert, creates flag, exits. | `![expired](docs/demo_expired.png)` |
| **Profile valid** | Runs headlessly, posts all complaints, no email. | `![valid](docs/demo_valid.png)` |
| **Email alert** | Example email from the bot asking you to refresh. | `![email](docs/demo_email.png)` |
| **Interactive refresh** | When flag exists, opens visible browser – you log in manually once, profile saved, flag removed. | `![refresh](docs/demo_refresh.gif)` |

> ⚠️ **Note:** Replace the placeholder image links with actual files. Store them in the `docs/` directory.

---

## 🧱 Tech Stack

| Tool | Purpose |
|------|---------|
| [Python](https://www.python.org/) | Core language |
| [Selenium](https://www.selenium.dev/) | Browser automation |
| [undetected‑chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) | Bypass bot detection |
| [selenium‑stealth](https://github.com/diprajpatra/selenium-stealth) | Extra stealth layer |
| [webdriver‑manager](https://github.com/SergeyPirogov/webdriver_manager) | Automatic ChromeDriver management |
| [llama‑cpp‑python](https://github.com/abetlen/llama-cpp-python) | Local LLM inference |
| [LLaMA 3 8B (Q4_K_M)](https://huggingface.co/bartowski/Meta-Llama-3-8B-Instruct-GGUF) | Tweet generation |
| [SMTP](https://docs.python.org/3/library/smtplib.html) | Email alerts |
| [cron](https://man7.org/linux/man-pages/man5/crontab.5.html) | Scheduling (every 6 hours) |
| **Persistent Chrome profiles** | Keep login session alive |

---

## 📁 Project Structure

```
complaint-bot/
├── main.py                 # Orchestrates the pipeline
├── down_detector.py        # Scrapes Downdetector
├── weather_checker.py      # Scrapes weather.com with thresholds
├── complain_writer.py      # LLM prompt engineering
├── twitter.py              # X posting + profile state machine
├── download_model.py       # Downloads LLaMA 3 model from HuggingFace
├── requirements.txt        # Python dependencies
├── docs/                   # Demo images (replace placeholders)
│   ├── demo_missing.png
│   ├── demo_expired.png
│   ├── demo_valid.png
│   ├── demo_email.png
│   └── demo_refresh.gif
└── README.md
```

---

## 🔄 How It Works (State Machine)

The bot uses a persistent Chrome profile stored in `complaint_bot_chrome_profile/`.  
It runs **headlessly** by default, but falls back to visible mode when the profile needs attention.

| Phase | Action |
|-------|--------|
| **Profile missing** | Sends email alert → creates `.need_refresh` flag → exits. Next run: visible browser opens for manual login → profile saved → flag removed. |
| **Profile expired** | Headless check detects login page → sends email alert → creates flag → exits. Next run: visible login → flag removed → headless resumes. |
| **Profile valid** | Runs headlessly → posts all complaints → exits. No email, no flag. |
| **Email alerts** | Uses Gmail SMTP (or any SMTP server) to notify you when intervention is needed. Credentials stored in environment variables. |

---

## 🧠 Deep Dive – Design Decisions

### 🌡️ Historical temperature thresholds
The bot does **not** complain about every hot or humid day. It retrieves the **historical average** for that specific day of the year from weather.com’s internal data. It then calculates the deviation and only posts if the anomaly exceeds a configurable threshold (e.g., +3°C above average). This makes complaints **data‑driven** and less spammy.

### ✍️ LLM prompt engineering

The bot uses a **two‑part prompt**:

#### 1. System prompt – defines the bot’s persona and output constraints

```python
"role": "system",
"content": (
    f"You are a {tone} Twitter user who writes short funny complaint tweets "
    f"about {reason} conditions. "
    "Output ONLY the tweet text. "
    "Mention officials for that region, use hashtags. "
    "Do not explain anything. "
    "Do not add headers, notes, or multiple tweets. "
    "Maximum 1 sentence."
)
```

- **`{tone}`** : randomly selected from a list (e.g., sarcastic, existential, passive‑aggressive, British humour, etc.)  
- **`{reason}`** : either `"website down"` (outages) or `"weather"` (temperature/humidity)

#### 2. User prompt – supplies the raw complaint data

The user prompt is constructed from the output of the scraping modules. For example, weather complaints are generated as:

```python
if data['temp'] > limits['max_temp']:
    weather_complaints.append(f"{city}'s {data['temp']} degree temperature")
elif data['humi'] > limits['max_humi']:
    weather_complaints.append(f"{city}'s {data['humi']}% humidity")
```

These strings (e.g., `"London's 32 degree temperature"`) are then passed to the LLM as the **user message**. The model receives:

**User message example:**
```
London's 32 degree temperature
Glasgow's 87% humidity
```

The LLM then generates a single‑sentence tweet that incorporates this information in the chosen tone, mentions relevant officials, and adds appropriate hashtags – without any extra commentary or explanations.

#### Why this works

- The **system prompt** forces the model to stay in character and obey strict formatting rules.
- The **user prompt** provides only the essential facts, leaving the creativity to the LLM.
- The combination produces consistently short, funny, complaint tweets that feel authentic to the bot’s persona.

### 🚀 Why local instead of GitHub Actions?
Originally the bot ran on GitHub Actions, but headless Chrome was unstable – constant `NoSuchWindowException`, memory limits, and random renderer crashes. Moving to a dedicated local Mac (or Linux server) with a persistent profile eliminated **99%** of the stability issues. The trade‑off: you must keep the machine running, but `cron` makes it effortless.

---

## 🛠️ Setup (macOS / Linux)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/complaint-bot.git
cd complaint-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the LLaMA model (once)
```bash
python download_model.py
```
This downloads `Meta-Llama-3-8B-Instruct-Q4_K_M.gguf` (~4.9GB) into the `model/` directory.  
The model is cached locally, so subsequent runs use the same file.

### 4. Configure email alerts (optional but recommended)
Create a `.env` file or export environment variables:
```bash
export SENDER_EMAIL="your.email@gmail.com"
export SENDER_EMAIL_PASS="your_app_password"   # Gmail App Password
export RECEIVER_EMAIL="your.email@gmail.com"
```
For Gmail, you need an [App Password](https://support.google.com/accounts/answer/185833) (enable 2FA first).

### 5. Add your X credentials (only for the first manual login)
```bash
export X_PASS_EMAIL="your_x_email"
export X_PASS="your_x_password"
```
These are used **only once** during the initial visible login. Later runs use the profile cookies.

### 6. Run the bot to trigger profile creation
```bash
python main.py
```

- **First run** – profile folder missing → you receive an email alert (if configured) and the script exits after creating `.need_refresh`.  
- **Second run** – the flag is detected → the bot opens a **visible Chrome window**.  
- **Log into X manually** in that window, then press **Enter** in the terminal.  
- The profile is saved, and the flag is removed.  
- **From now on**, the bot runs **headlessly** and posts tweets automatically.

### 7. Schedule with `cron` (every 6 hours)
Edit your crontab:
```bash
crontab -e
```
Add the following line (adjust the path to your Python interpreter and script):
```bash
0 */6 * * * cd /path/to/complaint-bot && /usr/local/bin/python3 main.py >> /var/log/complaint-bot.log 2>&1
```

> **Note:** The bot must be able to run headlessly. Chrome will start without a visible window. The persistent profile keeps the session alive for weeks.

---

## ⚙️ Configuration

### Add or remove services (`down_detector.py`)
```python
companies_to_check = [
    {'Apex Legends': 'https://downdetector.co.uk/status/apex-legends/'},
    {'Virgin Media': 'https://downdetector.co.uk/status/virgin-media/'},
    {'Google': 'https://downdetector.com/status/google/'},
]
```

### Add or remove cities (`weather_checker.py`)
```python
cities = ['London', 'Manchester', 'Edinburgh', 'Cardiff']
```

### Change tweet tones (`complain_writer.py`)
```python
tones = [
    "angry", "sarcastic", "dramatic",
    "passive aggressive", "existential",
    "british humour", "chronically online", "overreacting"
]
```

### Adjust historical temperature deviation threshold (`weather_checker.py`)
```python
TEMP_DEVIATION_THRESHOLD = 3     # complain if temperature >3°C above historical average
HUMIDITY_DEVIATION_THRESHOLD = 15 # complain if humidity >15% above average
```

---

## 🧪 Troubleshooting

| Problem | Likely cause | Solution |
|---------|--------------|----------|
| `NoSuchWindowException` | ChromeDriver mismatch or headless instability | Run `python main.py` without headless to refresh the profile. |
| Profile expired repeatedly | X session cookie life is short | Run visible mode again to re‑authenticate. |
| Email not sent | SMTP credentials wrong or Gmail security settings | Use an App Password; check your spam folder. |
| Chrome version mismatch | `get_chrome_version()` returns wrong value | Hardcode your Chrome version in `twitter.py`. |
| Model not found | Download interrupted | Delete the `model/` folder and re‑run `download_model.py`. |
| Cron job not running | Wrong path or permissions | Check cron log: `grep CRON /var/log/syslog` |

---

## 📜 License

This project is licensed under the **MIT License** – you are free to use, modify, distribute, and even complain about the license itself.

---

## 🙋‍♂️ Author

Built as part of the **#100DaysOfCode** challenge.  
Follow the bot’s own X account: [@S_s8877](https://x.com/S_s8877) – **SerialComplainer**.

> *“I complain about all things life.”* – the most accurate bot bio ever written.

---

**Made with ☕, British rage, and a healthy disrespect for CAPTCHAs.**
