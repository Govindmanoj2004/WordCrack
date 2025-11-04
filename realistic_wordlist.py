# realistic_wordlist.py
import re
import itertools
import random
from typing import List, Dict, Set, Any

# CONFIG
WATERMARK = "--EDU"
MAX_OUTPUT = 5000
MIN_LEN_DEFAULT = 6
MAX_LEN_DEFAULT = 16
COMMON_BLACKLIST = {
    "123456", "password", "qwerty", "admin", "letmein", "welcome",
    "12345678", "123456789", "1234567890", "abc123", "password1"
}
SEED = 42

# HELPERS
def sanitize(s: str) -> str:
    return re.sub(r'\s+', '', s).strip().lower() if s else ""

def extract_tokens(data: Dict[str, Any]) -> List[str]:
    """Extract all non-empty, sanitized tokens from payload."""
    tokens = set()
    skip_keys = {
        "auth_phrase", "count", "min_len", "max_len",
        "include_specials", "include_uppercase",
        "extra_words", "important_years", "apps"
    }
    
    for k, v in data.items():
        if k in skip_keys or not v:
            continue
        if isinstance(v, str):
            tokens.add(sanitize(v))
        elif isinstance(v, list):
            tokens.update(sanitize(x) for x in v if x)
    
    # Add extra words
    if data.get("extra_words"):
        tokens.update(sanitize(x) for x in data["extra_words"] if x)
    
    return [t for t in tokens if t]

def parse_dob(dob: str) -> Dict[str, str]:
    """Parse DD/MM/YYYY → dict of parts."""
    match = re.fullmatch(r'(\d{2})/(\d{2})/(\d{4})', dob or "")
    if not match:
        raise ValueError("DOB must be DD/MM/YYYY")
    dd, mm, yyyy = match.groups()
    return {"dd": dd, "mm": mm, "yyyy": yyyy, "full": f"{dd}{mm}{yyyy}"}

def get_years(data: Dict) -> List[str]:
    """Extract all years: DOB, important_years."""
    years = set()
    if data.get("dob"):
        try:
            years.add(parse_dob(data["dob"])["yyyy"])
        except:
            pass
    if data.get("important_years"):
        years.update(str(y).strip()[-4:] for y in data["important_years"] if y)
    return list(years)

# TRANSFORMS (A–N)
def case_variants(token: str, include_upper: bool) -> List[str]:
    yield token.lower()
    if include_upper:
        yield token.upper()
        yield token.capitalize()
        if len(token) > 1:
            yield ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(token))

def leet_variants(token: str) -> List[str]:
    table = str.maketrans({'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7', 'g': '9', 'b': '8'})
    yield token.translate(table)
    for i, c in enumerate(token):
        if c.lower() in 'aeiostgb':
            yield token[:i] + table.get(c, c) + token[i+1:]

def append_specials(base: str, include: bool) -> List[str]:
    if not include:
        return []
    specials = ['!', '@', '#', '$', '*']
    return [base + s for s in specials] + [s + base for s in specials]

def insert_special(base: str, include: bool) -> List[str]:
    if not include or len(base) < 2:
        return []
    outs = []
    for sp in ['!', '@', '1', '2']:
        for i in range(1, len(base)):
            outs.append(base[:i] + sp + base[i:])
    return outs

def numeric_suffixes(base: str, numbers: List[str]) -> List[str]:
    outs = []
    for n in numbers + ['1', '2', '3', '123', '007', '69', '420', '12', '21']:
        outs.append(base + n)
        outs.append(n + base)
    return outs

def date_variants(dob_parts: Dict) -> List[str]:
    y = dob_parts["yyyy"]
    return [
        dob_parts["full"],
        f"{dob_parts['dd']}{dob_parts['mm']}{y}",
        y, y[-2:],
        str(int(y) - 1), str(int(y) + 1),
        f"{dob_parts['dd']}-{dob_parts['mm']}-{y}"
    ]

# MAIN GENERATOR
def generate_realistic(
    data: Dict[str, Any],
    count: int = 1000,
    min_len: int = MIN_LEN_DEFAULT,
    max_len: int = MAX_LEN_DEFAULT,
    include_specials: bool = True,
    include_uppercase: bool = True
) -> List[str]:
    random.seed(SEED)
    candidates: Set[str] = set()

    def add(w: str):
        if min_len <= len(w) <= max_len and w not in COMMON_BLACKLIST:
            candidates.add(w + WATERMARK)

    tokens = extract_tokens(data)
    if not tokens:
        return []

    dob_parts = {}
    if data.get("dob"):
        try:
            dob_parts = parse_dob(data["dob"])
        except:
            pass

    numbers = get_years(data)
    if data.get("lucky_number"):
        numbers.append(sanitize(data["lucky_number"]))
    if data.get("phone"):
        phone = sanitize(data["phone"])
        if re.fullmatch(r'\d{10}', phone):
            numbers.append(phone[-4:])
            numbers.append(phone)

    name = sanitize(data.get("full_name") or data.get("nickname") or "")
    if name and dob_parts:
        for d in date_variants(dob_parts):
            add(name + d)
            add(d + name)

    if name and data.get("lucky_number"):
        n = sanitize(data["lucky_number"])
        add(name + n)
        add(n + name)

    for a, b in itertools.combinations(tokens, 2):
        add(a + b)
        add(a + '.' + b)
        add(a + '_' + b)

    if include_uppercase:
        for w in list(candidates)[:300]:
            base = w[:-len(WATERMARK)]
            for v in case_variants(base, True):
                add(v)

    for w in list(candidates)[:200]:
        for v in leet_variants(w[:-len(WATERMARK)]):
            add(v)

    if include_specials:
        for w in list(candidates)[:400]:
            base = w[:-len(WATERMARK)]
            for v in append_specials(base, True):
                add(v)
            for v in insert_special(base, True):
                add(v)

    for w in list(candidates)[:300]:
        base = w[:-len(WATERMARK)]
        for v in numeric_suffixes(base, numbers):
            add(v)

    remaining = count - len(candidates)
    if remaining > 0:
        perms = [''.join(p) for r in (2, 3) for p in itertools.permutations(tokens, r)]
        random.shuffle(perms)
        for p in perms:
            if remaining <= 0:
                break
            add(p)
            remaining -= 1

    # Final output
    final = list(candidates)
    random.shuffle(final)
    return final[:min(count, MAX_OUTPUT)]

# FLASK WEB WRAPPER
def generate_web(payload: dict) -> dict:
    if payload.get("auth_phrase") != "I_HAVE_PERMISSION":
        raise ValueError("Incorrect authorization phrase")

    required = ["full_name", "dob", "phone", "email"]
    for field in required:
        if not payload.get(field):
            raise ValueError(f"{field} is required")

    dob = payload["dob"].strip()
    parts = re.split(r'[/-]', dob)
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise ValueError("DOB must be in DD/MM/YYYY format")
    dd, mm, yyyy = map(int, parts)
    if not (1 <= dd <= 31 and 1 <= mm <= 12 and 1900 <= yyyy <= 2100):
        raise ValueError("Invalid date in DOB")
    payload["dob"] = f"{dd:02d}/{mm:02d}/{yyyy}"

    phone = re.sub(r'\D', '', payload["phone"])
    if len(phone) != 10:
        raise ValueError("Phone must be 10 digits")
    payload["phone"] = phone

    email = payload["email"].strip()
    if "@" in email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Invalid email format")
    payload["email"] = email

    count = max(1, min(5000, int(payload.get("count", 500))))
    min_len = max(1, int(payload.get("min_len", 6)))
    max_len = min(50, int(payload.get("max_len", 16)))

    lines = generate_realistic(
        data=payload,
        count=count,
        min_len=min_len,
        max_len=max_len,
        include_specials=payload.get("include_specials", True),
        include_uppercase=payload.get("include_uppercase", True)
    )
    return {"lines": lines, "count": len(lines)}