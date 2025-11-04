# WordCrack – Educational Wordlist Generator

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.0%2B-lightgrey)
![License](https://img.shields.io/badge/license-EDU-green)
![Status](https://img.shields.io/badge/status-active-success)

> **Generate realistic, RockYou-style password lists from personal data** — for **educational security research only**.

---

## Features

- 50+ input fields (name, DOB, phone, pet, city, etc.)
- Smart human-like password patterns
- Leet, case, special chars, separators
- Deterministic output (`seed=42`)
- Rate-limited API (`5/min`)
- Watermarked output (`--EDU`)
- Download as `.txt`
- Built with **Flask + TailwindCSS**

---

## Ethical Use Only

> This tool is for **educational purposes only**.  
> Do **not** use on systems without **explicit permission**.

All generated passwords end in `--EDU` to mark them as **synthetic**.

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/WordCrack.git
cd WordCrack
```
2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4.  Run the App
python app.py

5.  Server starts at:
http://localhost:5000