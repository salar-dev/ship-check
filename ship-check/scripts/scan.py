#!/usr/bin/env python3
"""Ship Check scanner: one read-only pass over a project.

Prints what the project is built with, where the important files are, what git
tracks, which settings the code reads, a table of server endpoints, and where
each check's search patterns hit. Every secret is masked before printing.

It reads source and config files only. It never opens database or data files,
never writes anything, and never uses the network.

Usage:  python3 scan.py [project_dir]
"""

import json
import os
import re
import subprocess
import sys

MAX_FILE_BYTES = 300_000
MAX_HITS = 18
MAX_LINE = 170

SKIP_DIRS = {
    "node_modules", ".git", ".next", ".nuxt", ".svelte-kit", ".astro", ".output", "dist",
    "build", "out", "vendor", "venv", ".venv", "__pycache__", ".dart_tool", ".turbo",
    ".vercel", ".netlify", ".cache", "coverage", "target", ".idea", ".vscode", "Pods",
    ".gradle", ".expo", ".wrangler", ".firebase", "bower_components", ".pnpm-store", ".yarn",
}
LOCKFILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock", "composer.lock",
    "Gemfile.lock", "poetry.lock", "Pipfile.lock", "Cargo.lock", "pubspec.lock", "uv.lock",
}
CODE_EXT = {
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".astro", ".py", ".rb",
    ".php", ".go", ".java", ".kt", ".cs", ".dart", ".rs", ".html", ".htm", ".ejs", ".hbs",
    ".erb", ".twig",
}
CONFIG_EXT = {".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf", ".rules", ".prisma", ".sql", ".sh", ".graphql"}
UI_EXT = {".jsx", ".tsx", ".vue", ".svelte", ".astro", ".html", ".htm", ".ejs", ".hbs", ".erb", ".twig", ".dart"}
DATA_EXT = {".db", ".sqlite", ".sqlite3", ".dump", ".bak", ".mdb", ".rdb"}
ENV_LIKE = re.compile(r"(^|/)\.env(\.|$)|\.(ini|cfg|properties)$")
ENV_EXAMPLE = re.compile(r"\.env\.(example|sample|template|dist)$|(^|/)env\.example$")
PUBLIC_PREFIX = re.compile(r"^(NEXT_PUBLIC_|VITE_|REACT_APP_|EXPO_PUBLIC_|NUXT_PUBLIC_|PUBLIC_|GATSBY_)")

SERVER_PATH = re.compile(
    r"(^|/)(api|server|backend|routes|controllers|functions|handlers|lambda|actions)(/|$)"
    r"|(^|/)(route|\+server|\+page\.server|middleware|server|app|main|index)\.(js|ts|mjs|cjs|py|php)$"
    r"|(^|/)(views|urls|wsgi|asgi)\.py$|controller", re.I)
SERVER_EXT = {".py", ".rb", ".php", ".go", ".java", ".kt", ".cs", ".rs"}

TOKEN = re.compile(
    r"sk-[A-Za-z0-9_\-]{16,}|sk_(?:live|test)_[A-Za-z0-9]{10,}|rk_(?:live|test)_[A-Za-z0-9]{10,}"
    r"|pk_(?:live|test)_[A-Za-z0-9]{10,}|whsec_[A-Za-z0-9]{8,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}"
    r"|AIza[0-9A-Za-z_\-]{30,}|eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}|xox[baprs]-[A-Za-z0-9\-]{10,}"
    r"|sb_(?:secret|publishable)_[A-Za-z0-9_\-]{10,}|re_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----")
LONG = re.compile(r"\b(?=[A-Za-z0-9_\-]*\d)(?=[A-Za-z0-9_\-]*[A-Za-z])[A-Za-z0-9_\-]{28,}\b")
SECRET_ASSIGN = re.compile(
    r"((?:password|passwd|pwd|secret|token|api[_\-]?key|private[_\-]?key|access[_\-]?key)\w*[\"']?\s*(?:[:=]|\|\||\?\?)\s*)([\"'`])(?![$<{%])([^\"'`$]{3,})\2",
    re.I)


def hide(value):
    """First 4 characters of a long secret, nothing of a short one."""
    return (value[:4] if len(value) >= 16 else "") + "•" * 8


def mask(text):
    text = SECRET_ASSIGN.sub(lambda m: m.group(1) + m.group(2) + hide(m.group(3)) + m.group(2), text)
    text = TOKEN.sub(lambda m: hide(m.group(0)), text)
    text = LONG.sub(lambda m: hide(m.group(0)), text)
    return text


def clip(line):
    line = mask(line.strip())
    return line if len(line) <= MAX_LINE else line[:MAX_LINE] + " ..."


def git(root, *args):
    try:
        out = subprocess.run(["git", "--no-optional-locks", *args], cwd=root, capture_output=True,
                             text=True, timeout=20)
        return out.stdout if out.returncode == 0 else None
    except Exception:
        return None


def walk(root):
    """Yield (relative_path, size) for every file outside the skipped folders."""
    for base, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in sorted(files):
            full = os.path.join(base, name)
            try:
                size = os.path.getsize(full)
            except OSError:
                continue
            yield os.path.relpath(full, root).replace(os.sep, "/"), size


def is_data(rel, size):
    ext = os.path.splitext(rel)[1].lower()
    name = os.path.basename(rel).lower()
    return ext in DATA_EXT or (ext == ".sql" and size > MAX_FILE_BYTES) or name.startswith(("backup", "dump"))


def is_text_candidate(rel):
    name = os.path.basename(rel)
    ext = os.path.splitext(rel)[1].lower()
    if name in LOCKFILES or name.endswith((".min.js", ".min.css", ".map")):
        return False
    return (ext in CODE_EXT or ext in CONFIG_EXT or name.startswith(".env")
            or name in {"Dockerfile", "Procfile", "Makefile", ".gitignore", "README.md", "readme.md"})


def read(root, rel):
    try:
        with open(os.path.join(root, rel), "rb") as f:
            raw = f.read(MAX_FILE_BYTES + 1)
    except OSError:
        return None
    if b"\x00" in raw[:2048] or len(raw) > MAX_FILE_BYTES:
        return None
    return raw.decode("utf-8", errors="replace")


def section(title):
    print("\n## " + title)


def bullets(items, empty="none found"):
    if not items:
        print("- " + empty)
    for item in items:
        print("- " + item)


# ---------------------------------------------------------------- stack

JS_CATEGORIES = [
    ("Framework", r"^(next|nuxt|@sveltejs/kit|astro|@remix-run/.*|react|vue|svelte|@angular/core|express|fastify|hono|@nestjs/core|koa|vite|gatsby|expo|electron)$"),
    ("Database / backend", r"^(@supabase/.*|firebase|firebase-admin|@prisma/client|prisma|drizzle-orm|mongoose|mongodb|pg|mysql2|better-sqlite3|sqlite3|@libsql/client|@neondatabase/serverless|@planetscale/database|convex|appwrite|pocketbase|redis|ioredis|@upstash/redis|typeorm|sequelize|knex)$"),
    ("Login", r"^(next-auth|@auth/.*|@clerk/.*|better-auth|lucia|passport|jsonwebtoken|jose|bcrypt|bcryptjs|argon2|iron-session|express-session)$"),
    ("AI", r"^(openai|@anthropic-ai/sdk|@google/generative-ai|@google/genai|ai|@ai-sdk/.*|langchain|@langchain/.*|replicate|groq-sdk|cohere-ai|@mistralai/.*|ollama)$"),
    ("Payments", r"^(stripe|@stripe/.*|@paddle/.*|@lemonsqueezy/.*|@polar-sh/.*|paypal.*|@paypal/.*)$"),
    ("Email", r"^(resend|nodemailer|postmark|@sendgrid/.*|@aws-sdk/client-ses|mailgun.*|@getbrevo/.*)$"),
    ("Validation", r"^(zod|yup|joi|valibot|class-validator|express-validator|ajv|superstruct)$"),
    ("Rate limiting", r"^(@upstash/ratelimit|express-rate-limit|rate-limiter-flexible|@fastify/rate-limit|express-slow-down)$"),
    ("Monitoring", r"^(@sentry/.*|pino|winston|@logtail/.*|dd-trace|newrelic|@bugsnag/.*|rollbar|posthog-js|posthog-node)$"),
    ("Uploads / storage", r"^(multer|formidable|busboy|uploadthing|@uploadthing/.*|@aws-sdk/client-s3|@vercel/blob|cloudinary)$"),
    ("Tests", r"^(jest|vitest|@playwright/test|cypress|mocha|@testing-library/.*)$"),
]
OTHER_MANIFESTS = ["requirements.txt", "pyproject.toml", "Pipfile", "composer.json", "Gemfile", "go.mod",
                   "pubspec.yaml", "Cargo.toml", "pom.xml", "build.gradle", "build.gradle.kts"]


def report_stack(root, files):
    section("Stack")
    names = {rel for rel, _ in files}
    manifests = [rel for rel in names if os.path.basename(rel) == "package.json" and rel.count("/") <= 3]
    for rel in sorted(manifests):
        try:
            pkg = json.loads(read(root, rel) or "{}")
        except ValueError:
            print(f"- {rel}: could not be parsed")
            continue
        deps = dict(pkg.get("dependencies") or {})
        dev = dict(pkg.get("devDependencies") or {})
        print(f"- `{rel}`: {len(deps)} dependencies, {len(dev)} dev dependencies")
        everything = {**dev, **deps}
        for label, pattern in JS_CATEGORIES:
            found = [f"{n}@{v}" + ("" if n in deps else " (dev)") for n, v in sorted(everything.items()) if re.match(pattern, n)]
            if found:
                print(f"  - {label}: {', '.join(found)}")
        scripts = pkg.get("scripts") or {}
        if scripts:
            print("  - Scripts: " + "; ".join(f"{k} = `{v}`" for k, v in list(scripts.items())[:8]))
    for name in OTHER_MANIFESTS:
        for rel in sorted(n for n in names if os.path.basename(n) == name and n.count("/") <= 2):
            text = read(root, rel) or ""
            lines = [l.strip() for l in text.splitlines() if l.strip() and not l.strip().startswith(("#", "//"))]
            print(f"- `{rel}` ({len(lines)} lines): " + mask("; ".join(lines[:40]))[:900])
    locks = sorted(n for n in names if os.path.basename(n) in LOCKFILES)
    print("- Lockfile: " + (", ".join(f"`{l}`" for l in locks) if locks else "NONE"))
    if not manifests and not any(os.path.basename(n) in OTHER_MANIFESTS for n in names):
        print("- No package manifest found: this may be a plain static site.")


# ---------------------------------------------------------------- layout

CONFIG_NAMES = re.compile(
    r"(^|/)(next\.config\.\w+|nuxt\.config\.\w+|vite\.config\.\w+|svelte\.config\.\w+|astro\.config\.\w+|vercel\.json"
    r"|netlify\.toml|wrangler\.(toml|jsonc?)|firebase\.json|firestore\.rules|storage\.rules|database\.rules\.json"
    r"|Dockerfile|docker-compose\.ya?ml|fly\.toml|render\.yaml|railway\.(json|toml)|Procfile|app\.yaml|schema\.prisma"
    r"|drizzle\.config\.\w+|middleware\.(js|ts)|settings\.py|config\.toml)$")


def report_layout(root, files, texts):
    section("Layout")
    top = {}
    for rel, _ in files:
        head = rel.split("/")[0] if "/" in rel else "(root)"
        top[head] = top.get(head, 0) + 1
    print("- Files per top-level folder: " + ", ".join(f"{k} {v}" for k, v in sorted(top.items(), key=lambda x: -x[1])[:14]))
    longest = sorted(((t.count("\n") + 1, rel) for rel, t in texts.items()
                      if os.path.splitext(rel)[1].lower() in CODE_EXT), reverse=True)[:8]
    print("- Longest source files: " + ", ".join(f"`{rel}` ({n} lines)" for n, rel in longest))
    configs = sorted(rel for rel, _ in files if CONFIG_NAMES.search(rel))
    print("- Config files: " + (", ".join(f"`{c}`" for c in configs[:25]) or "none found"))
    for label, pattern in [
        ("Supabase folder", r"(^|/)supabase/(config\.toml|migrations/)"),
        ("Migrations / schema", r"(^|/)(migrations?|drizzle|prisma)/|schema\.(sql|prisma)$"),
        ("CI workflows", r"^\.github/workflows/"),
        ("Tests", r"(^|/)(__tests__|tests?|spec|e2e)/|\.(test|spec)\.\w+$"),
    ]:
        found = sorted(rel for rel, _ in files if re.search(pattern, rel))
        print(f"- {label}: " + (f"{len(found)} files, e.g. `{found[0]}`" if found else "none found"))
    expected = [
        ("Settings example file (.env.example)", r"\.env\.(example|sample|template|dist)$|(^|/)env\.example$"),
        ("Server-side gate (middleware)", r"(^|/)middleware\.(js|ts|py|php)$|(^|/)hooks\.server\.(js|ts)$"),
        ("Not-found page", r"(^|/)(not-found|404|\+error)\.\w+$|(^|/)404/"),
        ("Error page", r"(^|/)(error|global-error|_error|500|\+error)\.\w+$"),
        ("README", r"(^|/)readme(\.md)?$"),
    ]
    for label, pattern in expected:
        found = sorted(rel for rel, _ in files if re.search(pattern, rel, re.I))
        print(f"- {label}: " + (", ".join(f"`{f}`" for f in found[:4]) if found else "MISSING"))
    pages = sorted(rel for rel in texts if re.search(r"(^|/)(page|\+page|index)\.\w+$|(^|/)pages/[^/]+\.\w+$|\.html?$", rel)
                   and not is_server(rel))
    print(f"- Pages ({len(pages)}): " + ", ".join(f"`{p}`" for p in pages[:40]) + (" ..." if len(pages) > 40 else ""))
    client = sorted(rel for rel, text in texts.items() if re.search(r"^\s*[\"']use client[\"']", text[:300], re.M))
    if client:
        print(f"- Marked to run in the browser ('use client', {len(client)}): " + ", ".join(f"`{c}`" for c in client[:30]))


# ---------------------------------------------------------------- env, data, git

def report_env_and_git(root, files, texts):
    tracked = None
    listing = git(root, "ls-files")
    in_repo = listing is not None
    if in_repo:
        tracked = set(listing.splitlines())

    def state(rel):
        if not in_repo:
            return "no git repo"
        ignored = git(root, "check-ignore", "-q", rel) is not None
        return ("TRACKED by git" if rel in tracked else "not tracked") + (", ignored" if ignored else ", NOT ignored")

    section("Settings files (values are never printed)")
    env_files = sorted(rel for rel, _ in files if os.path.basename(rel).startswith(".env"))
    defined = {}
    for rel in env_files:
        text = read(root, rel) or ""
        names = re.findall(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=", text, re.M)
        for n in names:
            defined.setdefault(n, []).append(rel)
        kind = "example file" if ENV_EXAMPLE.search(rel) else "REAL VALUES"
        print(f"- `{rel}` ({kind}; {state(rel)}):")
        for i, line in enumerate(text.splitlines(), 1):
            m = re.match(r"\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)", line)
            if m:
                value = m.group(2).strip().strip("\"'")
                note = "empty" if not value else f"set, {len(value)} chars"
                plain = re.search(r"URL|HOST|MODEL|REGION|PORT|DOMAIN|ENDPOINT", m.group(1), re.I)
                risky = re.search(r"KEY|SECRET|TOKEN|PASS|PRIVATE|DATABASE|DB_|DSN|CREDENTIAL", m.group(1), re.I)
                if value and plain and not risky and "@" not in value and len(value) <= 80:
                    note += f", value `{mask(value)}`"
                flag = "  <-- sent to every visitor (public prefix)" if PUBLIC_PREFIX.match(m.group(1)) else ""
                print(f"  - line {i}: `{m.group(1)}` ({note}){flag}")
    if not env_files:
        print("- none found")

    section("Settings the code reads")
    reads = {}
    pattern = re.compile(
        r"process\.env\.([A-Za-z_][A-Za-z0-9_]*)|process\.env\[[\"']([A-Za-z_][A-Za-z0-9_]*)[\"']\]"
        r"|import\.meta\.env\.([A-Za-z_][A-Za-z0-9_]*)|os\.environ(?:\.get)?[\[(]\s*[\"']([A-Za-z_][A-Za-z0-9_]*)"
        r"|getenv\(\s*[\"']([A-Za-z_][A-Za-z0-9_]*)|\benv\(\s*[\"']([A-Za-z_][A-Za-z0-9_]*)"
        r"|Deno\.env\.get\(\s*[\"']([A-Za-z_][A-Za-z0-9_]*)|String\.fromEnvironment\(\s*[\"']([A-Za-z_][A-Za-z0-9_]*)")
    for rel, text in texts.items():
        if os.path.basename(rel).startswith(".env"):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for m in pattern.finditer(line):
                name = next(g for g in m.groups() if g)
                reads.setdefault(name, f"{rel}:{i}")
    skip = {"NODE_ENV", "MODE", "DEV", "PROD", "BASE_URL", "SSR"}
    for name in sorted(reads):
        if name in skip:
            continue
        where = defined.get(name)
        note = "defined in " + ", ".join(where) if where else "NOT defined in any settings file"
        print(f"- `{name}` first read at `{reads[name]}`; {note}")
    if not reads:
        print("- none found")
    unused = sorted(n for n in defined if n not in reads)
    if unused:
        print("- Defined but never read by the code: " + ", ".join(f"`{n}`" for n in unused))

    section("Data files (not opened)")
    data = sorted((rel, size) for rel, size in files if is_data(rel, size))
    bullets([f"`{rel}` ({size // 1024} KB; {state(rel)})" for rel, size in data[:20]])

    section("Git")
    if not in_repo:
        print("- Not a git repository (or git is unavailable).")
        return
    remotes = (git(root, "remote") or "").split()
    urls = []
    for r in remotes:
        url = (git(root, "remote", "get-url", r) or "").strip()
        urls.append(f"{r} -> " + re.sub(r"://[^@/\s]+@", "://", url))
    print("- Remotes: " + ("; ".join(urls) if urls else "none (the code has not been pushed anywhere from this folder)"))
    risky = re.compile(r"(^|/)\.env(\.|$)|\.(pem|key|p12|pfx|keystore|jks)$|(^|/)(id_rsa|id_ed25519)$|service-?account.*\.json$|credentials.*\.json$|\.(db|sqlite3?|dump|bak)$", re.I)
    hot = sorted(t for t in tracked if risky.search(t) and not ENV_EXAMPLE.search(t))
    print("- Tracked files that look like secrets or data: " + (", ".join(f"`{h}`" for h in hot) if hot else "none"))
    log = git(root, "log", "--all", "--diff-filter=A", "--name-only", "--pretty=format:@%h %s", "--",
              ".env", ".env.*", "*.pem", "*.key", "*.db", "*.sqlite", "*.sqlite3", "*service-account*.json") or ""
    commit, ever = "", []
    for line in log.splitlines():
        if line.startswith("@"):
            commit = line[1:]
        elif line.strip() and not ENV_EXAMPLE.search(line):
            ever.append(f"`{line.strip()}` first committed in {commit[:60]}")
    print("- Ever committed (even if deleted since): " + ("; ".join(ever[:10]) if ever else "none"))
    count = (git(root, "rev-list", "--all", "--count") or "?").strip()
    print(f"- Commits: {count}")


# ---------------------------------------------------------------- endpoints

def is_server(rel):
    ext = os.path.splitext(rel)[1].lower()
    if ext not in CODE_EXT or ext in {".html", ".htm"}:
        return False
    return bool(SERVER_PATH.search(rel)) or ext in SERVER_EXT


METHODS = re.compile(
    r"export\s+(?:async\s+)?(?:function|const)\s+(GET|POST|PUT|PATCH|DELETE)\b"
    r"|\b(?:app|router|server|api|route)\.(get|post|put|patch|delete|all)\s*\("
    r"|@(?:app|router|api|blueprint|bp)\.(get|post|put|patch|delete|route)\b"
    r"|Route::(get|post|put|patch|delete|any)\b|@(Get|Post|Put|Patch|Delete)Mapping\b"
    r"|\$_(GET|POST|REQUEST)\b|[\"']use server[\"']")
AUTH_WORDS = re.compile(
    r"getServerSession|\bauth\(\)|currentUser|getUser\(|verifyIdToken|verifySession|\bjwt\b|jsonwebtoken|\bsession\b"
    r"|cookies\(\)|req(?:uest)?\.cookies|headers\(\)|\.headers\.get\(|authorization|requireAuth|isAuthenticated"
    r"|login_required|permission_classes|authenticate|passport|clerk|supabase\.auth|getAuth\(|\$_SESSION|Auth::|\bguard\b",
    re.I)
VALIDATION = re.compile(r"safeParse|z\.object|\byup\.|\bJoi\.|valibot|pydantic|BaseModel|class-validator|express-validator|\$request->validate|validator\.", re.I)
ERRORS = re.compile(r"\btry\b|\.catch\(|\bexcept\b|\brescue\b")
RATE = re.compile(r"rate.?limit|throttle|upstash", re.I)
SQL_CONCAT = re.compile(
    r"(SELECT|INSERT INTO|UPDATE|DELETE FROM|WHERE)\b[^\n]*(\$\{|[\"']\s*\+|\+\s*[\"']|%s|\.format\(|\{\w+\})", re.I)
SQL_FSTRING = re.compile(r"\bf[\"'][^\n]*(SELECT|INSERT INTO|UPDATE|DELETE FROM|WHERE)\b", re.I)


def report_endpoints(texts):
    section("Server endpoints (read each one before grading; these columns are hints, not verdicts)")
    rows = []
    for rel in sorted(texts):
        if not is_server(rel):
            continue
        text = texts[rel]
        methods = sorted({(g or "").upper() for m in METHODS.finditer(text) for g in m.groups() if g} |
                         ({"ACTION"} if re.search(r"[\"']use server[\"']", text) else set()))
        if not methods:
            continue
        auth = sorted({m.group(0).lower() for m in AUTH_WORDS.finditer(text)})[:3]
        sql = [str(i) for i, line in enumerate(text.splitlines(), 1) if SQL_CONCAT.search(line) or SQL_FSTRING.search(line)]
        rows.append((rel, ",".join(methods), ", ".join(auth) or "NONE", "yes" if VALIDATION.search(text) else "no",
                     "yes" if ERRORS.search(text) else "no", "yes" if RATE.search(text) else "no", ",".join(sql[:6]) or "-"))
    if not rows:
        print("- No server endpoints recognised. If the project has a backend, find it by hand.")
        return
    print("| File | Methods | Login words in file | Validation | try/catch present | Rate limit | Lines joining input into a query |")
    print("|---|---|---|---|---|---|---|")
    for row in rows[:80]:
        print("| `" + row[0] + "` | " + " | ".join(row[1:]) + " |")
    if len(rows) > 80:
        print(f"- ... and {len(rows) - 80} more endpoint files")


# ---------------------------------------------------------------- pattern hits

def hits(texts, title, pattern, where=None, limit=MAX_HITS, flags=re.I, show=True):
    regex = re.compile(pattern, flags)
    found, total = [], 0
    for rel in sorted(texts):
        if os.path.basename(rel).startswith(".env") or (where and not where(rel)):
            continue
        for i, line in enumerate(texts[rel].splitlines(), 1):
            if regex.search(line):
                total += 1
                if len(found) < limit:
                    found.append(f"`{rel}:{i}`  {clip(line)}" if show else f"`{rel}:{i}`  (line not shown)")
    print(f"\n**{title}** ({total} hit{'s' if total != 1 else ''})")
    for f in found:
        print("- " + f)
    if total > len(found):
        print(f"- ... {total - len(found)} more")


def code(rel):
    return os.path.splitext(rel)[1].lower() in CODE_EXT


def ui(rel):
    return os.path.splitext(rel)[1].lower() in UI_EXT and not is_server(rel)


def not_docs(rel):
    return not rel.lower().endswith(".md")


def report_services(texts):
    section("Outside services the code mentions")
    hosts = {}
    url = re.compile(r"https?://([a-z0-9.\-]+\.[a-z]{2,})", re.I)
    ignore = re.compile(r"w3\.org|schema\.org|example\.|localhost|github\.com/|nextjs\.org|reactjs\.org|json-schema")
    for rel, text in texts.items():
        if rel.lower().endswith(".md"):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for m in url.finditer(line):
                if not ignore.search(m.group(0) + "/"):
                    hosts.setdefault(m.group(1).lower(), f"{rel}:{i}")
    bullets([f"`{h}` (first at `{w}`)" for h, w in sorted(hosts.items())[:25]], "no outside addresses in the code")
    ai = re.compile(r"chat/completions|/v1/messages|generateContent|openai|anthropic|gemini|openrouter|\bgpt-|claude-|\bllm\b|embedding", re.I)
    found = []
    for rel in sorted(texts):
        if not code(rel):
            continue
        for i, line in enumerate(texts[rel].splitlines(), 1):
            if ai.search(line):
                side = "server file" if is_server(rel) else "BROWSER-SIDE or shared file"
                found.append(f"`{rel}:{i}` ({side})  {clip(line)}")
                break
    print("- AI calls or AI settings, first line per file:" + ("" if found else " none found"))
    for f in found[:12]:
        print("  - " + f)


def report_hits(texts):
    section("Pattern hits by check (a hit is a place to look; no hit is not yet a pass)")
    hits(texts, "A1 secret-looking values in files", TOKEN.pattern + r"|(?:password|passwd|secret|token|api[_\-]?key|private[_\-]?key)\w*[\"']?\s*(?:[:=]|\|\|)\s*[\"'`][^\"'`$]{6,}[\"'`]")
    hits(texts, "A1 secret-sounding settings behind a public prefix",
         r"(NEXT_PUBLIC_|VITE_|REACT_APP_|EXPO_PUBLIC_|NUXT_PUBLIC_|PUBLIC_|GATSBY_)[A-Z0-9_]*(KEY|SECRET|TOKEN|PASSWORD|PRIVATE)[A-Z0-9_]*", flags=0)
    hits(texts, "A4 development leftovers", r"localhost|127\.0\.0\.1|DEBUG\s*=\s*True|debug:\s*true|changeme|password123|admin:admin|\b123456\b", lambda r: not_docs(r) and os.path.basename(r) != "package.json")
    hits(texts, "A4 logins or passwords written in docs", r"(password|login|passwd)\s*[:=]|\S+@\S+\s*/\s*\S+", lambda r: r.lower().endswith(".md"), limit=8, show=False)
    hits(texts, "A5 stand-ins where a real service belongs", r"\b(mock|stub|fake|dummy)\b|hard-?coded|not (added|implemented|connected) yet|\bfor now\b|in dev we|TODO|FIXME", is_server)
    hits(texts, "B3 login or roles kept in browser storage", r"localStorage|sessionStorage|AsyncStorage|SharedPreferences", code)
    hits(texts, "B3 B1 role and plan decisions", r"\b(isAdmin|is_admin|role|isPro|plan)\b\s*(===?|!==?|==)\s*[\"']|\.role\b|\.plan\b", code, limit=14)
    hits(texts, "B5 password handling", r"bcrypt|argon2|scrypt|pbkdf2|\bmd5\b|\bsha1\b|createHash|password_hash|hashlib|password", is_server, limit=14)
    hits(texts, "B2 B5 whole rows read from the database (check what is sent back)", r"SELECT\s+\*|\.select\(\s*\)|\.select\(\s*[\"']\*[\"']\s*\)|findMany\(\s*\)|\.find\(\s*\{?\s*\}?\s*\)", is_server, limit=12)
    hits(texts, "C3 raw HTML output", r"innerHTML|dangerouslySetInnerHTML|v-html|\|\s*safe\b|html_safe|\{\{\{|\{@html|bypassSecurityTrust|Html\.Raw")
    hits(texts, "C4 file uploads", r"multer|formidable|busboy|multipart|\.formData\(\)|UploadedFile|request\.files|\$_FILES|type=[\"']file[\"']", code)
    hits(texts, "C5 values taken from the request", r"(amount|price|total|role|plan|userId|user_id|isAdmin|discount)\b[^\n]{0,40}(body|req\.|request\.|params|searchParams|\$_POST|\$_GET)|(body|req\.body|request\.json\(\))[^\n]{0,60}\b(amount|price|total|role|plan|userId|user_id)\b", is_server)
    hits(texts, "D2 error details that may reach the visitor", r"\.stack\b|traceback|err(or)?\.message|e\.message|str\(e\)", is_server, limit=10)
    hits(texts, "D3 rate limiting", RATE.pattern, code, limit=8)
    hits(texts, "D4 error tracking and logging", r"sentry|logtail|\bpino\b|winston|datadog|bugsnag|rollbar|newrelic|\blogger\b|logging\.", code, limit=8)
    hits(texts, "E3 database shape", r"CREATE TABLE|createTable|pgTable\(|sqliteTable\(|mysqlTable\(|^\s*model\s+\w+\s*\{|class\s+\w+\(.*Model\)", limit=10)
    hits(texts, "F1 plain-HTTP addresses", r"http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|www\.w3\.org|schemas\.)", not_docs, limit=8)
    hits(texts, "F2 cross-origin settings", r"Access-Control-Allow-Origin|Access-Control-Allow-Credentials|\bcors\(|CORS_ORIGIN|origin:\s*[\"']\*|allow_origins", limit=8)
    hits(texts, "F4 logging in server code", r"console\.(log|debug|info)|\bprint\(|var_dump|\bdd\(|System\.out\.print", is_server, limit=12)
    tools = sorted(rel for rel in texts if is_server(rel) and re.search(r"(^|/)(debug|seed|reset|test|dev|playground|tmp|mock)(/|\.)", rel, re.I))
    print(f"\n**F4 server files that look like building tools** ({len(tools)} found)")
    for t in tools[:10]:
        print(f"- `{t}`")
    hits(texts, "F5 promises to compare with the code", r"encrypt|secure|100\s?%|protected|guarantee|trusted by|\b\d[\d,.]*\+?\s*(users|customers|templates|reviews)", lambda r: code(r) and not is_server(r), limit=10)
    hits(texts, "F5 placeholder text", r"lorem ipsum|\bTODO\b|\bFIXME\b|coming soon|your-?domain|yourcompany", lambda r: code(r) and not is_server(r), limit=12)


# ---------------------------------------------------------------- main

def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    if not os.path.isdir(root):
        sys.exit(f"Not a folder: {root}")
    files = list(walk(root))
    texts = {}
    for rel, size in files:
        if is_data(rel, size) or not is_text_candidate(rel) or size > MAX_FILE_BYTES:
            continue
        text = read(root, rel)
        if text is not None:
            texts[rel] = text

    print("# Ship Check scan")
    print(f"\nProject: `{root}`")
    print(f"Files outside skipped folders: {len(files)}; read: {len(texts)}; lines read: "
          f"{sum(t.count(chr(10)) + 1 for t in texts.values())}")
    print("Skipped folders: dependency, build and version-control folders. Database and data files are listed, never opened.")

    report_stack(root, files)
    report_layout(root, files, texts)
    report_env_and_git(root, files, texts)
    report_endpoints(texts)
    report_services(texts)
    report_hits(texts)
    print("\nEnd of scan. Nothing was changed and nothing was sent anywhere.")


if __name__ == "__main__":
    main()
