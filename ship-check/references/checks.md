# Ship Check — the check list

Go through every check. Each has an ID to cite in the report, what to look for, how to grade
it, and the plain-language point to get across.

Tool and framework names are examples only. Apply the same idea to whatever the project uses.

Some checks are general (B2: endpoints with no login check) and others are specific (B4, B5,
C5, F4). When one line of code fits both, write the detail under the specific check and let
the general one list the place in a single line. Each check still gets its own mark.

The three login checks divide like this: B1 is about pages, B2 is about endpoints, and B3 is
for places where a check exists but only in the browser. A page with no check at all is B1,
not B3.

## Contents

- Search starters
- A. Secrets and config (A1–A5)
- B. Who can get in (B1–B6)
- C. What users can send (C1–C5)
- D. When things go wrong (D1–D4)
- E. Keeping it alive (E1–E3)
- F. Launch basics (F1–F5)

## Search starters

`scripts/scan.py` runs all of these and masks what it prints, so use this list only when the
script cannot run. Skip dependency and build folders. For the first row, print file names or
counts only (`grep -l` or `-c`), so that keys do not end up in the terminal. A hit is a place
to look, and no hit is not yet a pass.

```text
A1 A2   sk-|sk_live|sk_test|whsec_|AKIA|ghp_|eyJ|BEGIN .*PRIVATE KEY|api[_-]?key|secret|password *[:=]
A1 A3   process\.env|import\.meta\.env|os\.environ|getenv|NEXT_PUBLIC_|VITE_|REACT_APP_|EXPO_PUBLIC_
A4 F1   localhost|127\.0\.0\.1|http://|DEBUG|changeme|password123|123456
B1-B4   middleware|session|cookie|jwt|auth|currentUser|isAdmin|role|localStorage
B5      bcrypt|argon|scrypt|md5|sha1|hash
C2      SQL keywords on the same line as ${ or + or %s or .format( or f"
C3      innerHTML|dangerouslySetInnerHTML|v-html|\| *safe|html_safe
C4      upload|multipart|formData|multer
D1 D2   try|catch|except|rescue|\.stack
D3 D4   rate.?limit|throttle|sentry|logger|winston|pino
F2      Access-Control-Allow-Origin|cors
F4 F5   console\.log|print\(|TODO|FIXME|lorem|/debug|/seed|/test
```

For git: `git ls-files` lists what is tracked, and `git log --all --oneline -- <file>` shows
whether a file was ever committed.

---

## A. Secrets and config

### A1. Secret keys written in the code

**Look for:** API keys, database passwords, private keys, admin or "service" keys, signing
secrets and tokens typed directly into source files, config files, or anything shipped to the
browser. Check environment variables with a public prefix (`NEXT_PUBLIC_`, `VITE_`,
`REACT_APP_`, `PUBLIC_`, `EXPO_PUBLIC_` and similar): everything behind such a prefix is sent
to every visitor.

**Careful:** some keys are designed to be public: "publishable" or "anon" keys, web config for
hosted backends, map keys. Do not mark these red. They are only safe when the service behind
them has its own rules locked down, so note that and check B4.

**Grade:** 🔴 a real secret in source, in the browser bundle, or behind a public prefix.
🟡 a secret that looks like a placeholder or test value but sits where a real one will go.
🟢 secrets are read from the environment on the server only.

**Explain:** a secret key is the password to a service. In the code, anyone who sees the code
has it; in browser code, every visitor has it.

**Fix:** move it to a server-side environment variable, and replace the key in the service's
dashboard. Deleting it from the file is not enough once it has been exposed.

### A2. Secrets file saved into version control

**Look for:** `.env` and similar files (`.env.local`, `.env.production`, credential JSON files,
key files) that are tracked by git or missing from `.gitignore`. If git is available, check
whether such a file was ever committed, not only whether it is tracked now. Apply the same
test to files that hold real data: database files, dumps, exports and backups (`*.db`,
`*.sqlite`, `*.sql`, `backup*`).

**Grade:** 🔴 a file with real secrets or real user data is tracked or appears in history.
🟡 not tracked, but nothing in `.gitignore` prevents it. 🟢 ignored and never committed.

**Explain:** version control remembers everything. Once a secrets file is saved into it, it
stays in the history, and it goes wherever the code goes, including a public repository.

**Fix:** add it to `.gitignore`, stop tracking it, and replace every key that was in it.

### A3. No list of required settings

**Look for:** environment variables the code reads, compared with what is documented. Is there
a `.env.example` or a setup section listing every variable, without real values?

**Grade:** 🟡 variables are used but listed nowhere. 🟢 an example file or setup notes cover them.

**Explain:** without the list, the live site starts with a setting missing and fails in ways
that are hard to trace, and nobody else can ever set the project up.

**Fix:** add `.env.example` with every variable name and a one-line note, no real values.

### A4. Development settings left on

**Look for:** debug mode on (`DEBUG=True`, development mode in production config), detailed
error pages, test or sandbox payment keys where live ones belong, default logins
(`admin`/`admin`, `test`/`1234`), seeded test accounts, addresses pointing at `localhost` in
config that will be used live, sample accounts or data loaded automatically on first run.

**Grade:** 🔴 a default or test login that works, or a `localhost` address in live config
(the site will not work). 🟡 debug mode, verbose errors, sample data. 🟢 none found.

**Explain:** settings that make building easier also show strangers how the site works inside,
and test logins are the first thing anyone tries.

**Fix:** turn debug off for production, remove test accounts, set live addresses from
environment variables.

### A5. Stand-ins where a real service belongs

**Look for:** a mock or stub standing in for a real service: a fake AI or email endpoint,
payment code that reports success without calling the payment provider, code that switches a
plan or an order to "paid" without looking at the provider's answer, a plan that is switched
on when the visitor lands on the "payment successful" or return page instead of when the
provider confirms the payment to the server, a feature that silently does nothing when a
setting is missing.

**Grade:** 🔴 a stand-in that skips a payment or a permission step. 🟡 any other stand-in the
visitor would meet. 🟢 none found.

**Explain:** the site looks finished, but a part of it is a prop. On launch day the feature
either does not work or gives away what should be paid for.

**Fix:** connect the real service, and make the code fail loudly when the setting is missing
instead of pretending it worked.

---

## B. Who can get in

### B1. Private pages with no login check

**Look for:** admin panels, dashboards, account and settings pages. For each, find where the
server decides whether this visitor may see it. A page nobody links to is not protected.

**Grade:** 🔴 a page showing private or admin content loads without a server-side check.
🟢 every private page is checked on the server before anything is sent.

**Explain:** the page is open to anyone who types or guesses its address.

**Fix:** check the login on the server (middleware, route guard, or at the top of the handler)
before returning the page or its data.

### B2. Server endpoints with no login check

**Look for:** every API route, server function, server action and webhook. Which ones read or
change private data, and does each check who is calling before doing it? Webhooks should
verify the sender's signature.

**Grade:** 🔴 an endpoint returns or changes private data with no check.
🟡 an unchecked endpoint that only exposes harmless data. 🟢 all sensitive endpoints check.

**Explain:** the page is only the front. The endpoints behind it can be called directly,
skipping the page and its login screen entirely.

**Fix:** verify the session or token at the start of each endpoint, and reject the request if
it is missing.

### B3. Login enforced only in the browser

**Look for:** hiding buttons or redirecting in browser code as the only protection; roles or
"is admin" flags kept in browser storage and trusted; the plan, the remaining free tries or a
credit balance kept in browser storage and trusted; a password compared in browser code; an
admin password written in the page's script.

**Grade:** 🔴 any of these with no matching check on the server. 🟢 the server decides.

**Explain:** code in the browser is in the visitor's hands. They can read it, change it, or
skip it, so a lock that lives there is not a lock.

**Fix:** keep the browser checks for convenience, and enforce every one of them on the server.

### B4. One person can reach another person's data

**Look for:** endpoints that take an ID (order, user, file) and load the record without
checking it belongs to the caller. For hosted databases and storage, read the access rules:
row-level rules switched off, rules that allow everything (`allow read, write: if true`),
public buckets holding private files, a database reachable from the browser with a powerful key.
Look too at public or "share" links built from a counting number (`/invoice/1042`): the next
number is someone else's. And look at what a person may change in their own record: a rule or
endpoint that lets them update their whole row is open when that row also holds their plan,
role or balance.

**Grade:** 🔴 another person's records can be read or changed, or rules are open.
⚪ the rules live in a dashboard and are not in the project: ask the owner to show them.
🟢 every lookup is tied to the caller, and rules restrict access.

**Explain:** being logged in is not the same as being allowed. Without an ownership check, any
customer can see every customer's data by changing a number.

**Fix:** filter every query by the current user, and write access rules that grant each person
only their own records.

### B5. Passwords stored or handled unsafely

**Look for:** passwords saved as plain text, or scrambled with a weak method (`md5`, `sha1`,
unsalted hashes); hand-written login systems where a maintained library or service exists;
passwords written to logs.

**Grade:** 🔴 plain text or weak scrambling. 🟡 hand-written login that looks correct but is
unreviewed. 🟢 a maintained library or service handles it.

**Explain:** people reuse passwords. If the database leaks and passwords are readable, the
damage reaches their email and bank, not only this site.

**Fix:** use the framework's or provider's login system, or a proper password-hashing library.

### B6. Sessions that are easy to steal or never end

**Look for:** login tokens kept where page scripts can read them; cookies missing `HttpOnly`,
`Secure` or `SameSite`; tokens with no expiry; a short or guessable signing secret.

**Grade:** 🟡 any of these. 🔴 a signing secret in use that is a default or example value.
🟢 protected cookies and tokens that expire. If the project has no server-side session at all
and "login" lives only in browser storage, that is B3; grade B6 🟡 and point to B3.

**Explain:** a session token is a temporary key to an account. If it is easy to copy or lasts
forever, one leak gives permanent access.

**Fix:** use protected cookies, set an expiry, and generate a long random signing secret.

---

## C. What users can send

### C1. Input accepted without checking

**Look for:** forms and endpoints that use what the user sent as-is. Is there a check on the
server for type, length, format and allowed values? Checks in the browser alone do not count.

**Grade:** 🟡 no server-side checking. 🟢 input is validated on the server.

**Explain:** people, and bots, will send things the form never expected. Unchecked input is
how broken records and most attacks get in.

**Fix:** validate every field on the server, ideally with a schema or validation library.

### C2. User input placed directly into database queries

**Look for:** queries built by joining text with user input (string concatenation or
templates), raw query calls fed request data, filters passed straight from the request.

**Grade:** 🔴 user input reaches a query unescaped. 🟢 parameterised queries or a query builder
are used throughout.

**Explain:** a visitor can type database commands into a form field and the database will run
them: read everything, change it, or delete it.

**Fix:** use parameterised queries or the query builder's own methods, never joined text.

### C3. User content shown as raw HTML

**Look for:** user-supplied text inserted as HTML (`innerHTML`, `dangerouslySetInnerHTML`,
`v-html`, `| safe`, unescaped template output), including names, comments and profile fields.

**Grade:** 🔴 content from one user is shown unescaped to other users or to an admin.
🟡 unescaped but only shown back to the same user. 🟢 output is escaped.

**Explain:** someone can post a "comment" that is really a script. It then runs in the browser
of everyone who views it and can act as them.

**Fix:** show user content as text; if formatting is needed, clean it with a sanitising library.

### C4. File uploads with no limits

**Look for:** upload handling with no limit on file type or size, files saved under their
original name, uploads stored where the server might run them, private uploads in public storage.

**Grade:** 🔴 uploaded files could be run by the server, or private files are public.
🟡 no type or size limit. 🟢 type, size and location are controlled. ⚪ no uploads.

**Explain:** an open upload lets people fill the storage, share harmful files from the site's
address, or upload a program instead of a picture.

**Fix:** allow only the needed file types, cap the size, rename files, store them away from code.

### C5. Trusting the browser for prices, amounts or roles

**Look for:** the price, total, discount, quantity limit, plan, user ID or role being taken
from the request instead of looked up on the server. Check checkout, signup and profile-update
code, and any update endpoint that saves whatever fields the browser sends.

**Grade:** 🔴 any of these values is taken from the request and used. 🟢 the server looks them up.

**Explain:** the visitor controls everything their browser sends. If the browser states the
price, the customer chooses what to pay; if it states the role, anyone can sign up as admin.

**Fix:** send only what was chosen (the product ID); calculate prices and set roles on the server.

---

## D. When things go wrong

### D1. No handling for failures

**Look for:** calls to databases, other services and the network with nothing catching a
failure; pages with no error or empty state; a failed request that leaves the screen loading
forever.

**Grade:** 🟡 important flows (signup, payment, saving data) have no failure handling.
🟢 failures are caught and the user is told something useful.

**Explain:** on a real connection, requests fail. Without handling, the visitor sees a frozen or
blank page, and may pay or submit twice.

**Fix:** catch failures around every outside call and show a clear message with a way to retry.

### D2. Error messages that reveal the insides

**Look for:** raw error objects, stack traces, database messages or file paths returned to the
visitor or shown on the page.

**Grade:** 🟡 internal details reach the visitor. 🟢 nothing in the code sends internal
details to the visitor, whether the code writes a general message itself or the framework
hides the detail in production.

**Explain:** a detailed error tells an attacker which database and which file to aim at.

**Fix:** return a short general message; record the full error on the server only.

### D3. Nothing stops repeated requests

**Look for:** rate limiting on login, signup, password reset, contact forms and search. Above
all, check endpoints that cost money per call: AI, SMS, email and payment providers. Where a
plan promises a usage limit ("3 free tries", credits), find where the server counts the uses.

**Grade:** 🔴 a paid service can be used without login and without a limit, whether through
one of the site's endpoints or straight from the browser; or a promised usage limit on a paid
service is not counted on the server (counted only in the browser, or not at all). Count a
service as paid if it will be at launch, even when a stub stands in for it now.
🟡 no limit on login or public forms. 🟢 limits are in place.

**Explain:** a simple script can try thousands of passwords, flood the inbox, or run up a bill
with a paid service overnight.

**Fix:** add rate limiting (by account and by address), require login for paid features, and
set a spending cap in the provider's dashboard.

### D4. Nobody would know it broke

**Look for:** any error tracking, logging or uptime monitoring that works in production.
`console.log` alone does not count.

**Grade:** 🟡 none. 🟢 errors are recorded somewhere the owner will see them.

**Explain:** without it, the owner learns the site is down from an angry customer, or never.

**Fix:** add an error-tracking service or the host's logging, and an uptime alert.

---

## E. Keeping it alive

### E1. Outdated or vulnerable packages

**Look for:** run the package manager's audit if it is available (`npm audit`, `pnpm audit`,
`pip-audit`, `composer audit`, `bundle audit`, and so on) and read the result. Check that a
lockfile exists. Note frameworks that are several major versions behind or no longer supported.

**Grade:** 🔴 a known critical problem in a package the live site uses (not a dev-only tool).
🟡 high or moderate problems, no lockfile, or an unsupported framework version.
🟢 audit is clean. If the audit cannot be run, grade from what is visible: 🟡 when pinned
versions are clearly old or unsupported, otherwise ⚪. Either way say the audit was not run
and give the command, and do not list specific flaws from memory.

**Explain:** most of the site is other people's code. When a flaw in a package is published,
sites still using the old version become easy targets.

**Fix:** update each package to the version the audit names, test, and commit the lockfile.
Say when that update is a jump to a new major version, because it can need code changes, and
say so when the audit offers no fixed version yet.

### E2. No backups

**Look for:** this is rarely visible in code. Look for backup scripts or config, then ask the
owner: is the database backed up automatically, and has a restore ever been tried? If the
database is a file stored next to the code, ask where the site will be hosted: many hosts
wipe local files on every deploy, which erases the data.

**Grade:** 🟡 the database is a file kept next to the code and nothing shows where it will
live or how it is copied; or the owner says there are no backups. 🟢 automatic backups
confirmed. ⚪ a hosted database whose backup settings are not visible: put the question in
the report.

**Explain:** one bad update, one mistake or one attack can erase the data. Without a backup
there is nothing to bring back.

**Fix:** turn on the database provider's automatic backups, and restore one once to prove it works.

### E3. Database changes are not recorded

**Look for:** migration files or a schema file in the project. Was the database shaped by hand
in a dashboard with nothing written down?

**Grade:** 🟡 no migrations or schema file. 🟢 schema is in the project, as migrations, a
schema file, or table definitions in the code. ⚪ no database.

**Explain:** if the database had to be rebuilt tomorrow, nobody could say what it looked like.

**Fix:** export the current schema into the project and make future changes through migrations.

---

## F. Launch basics

### F1. Not fully on HTTPS

**Look for:** `http://` addresses for the site's own API, scripts or assets; cookies without
`Secure`; no redirect from HTTP to HTTPS where the project configures its own server.

**Grade:** 🟡 a plain-HTTP address in use (ignore `http://localhost`: that is a development
leftover and belongs to A4). 🟢 the project itself forces HTTPS, with a redirect or a
strict-transport header in its own config. ⚪ nothing in the project decides it, which is
the usual case on platform hosting: tell the owner to turn on "force HTTPS" at the host.

**Explain:** over plain HTTP, anyone on the same network can read or change what passes
between the visitor and the site, including passwords.

**Fix:** use `https://` everywhere and force the redirect at the host.

### F2. The server answers any website

**Look for:** cross-origin settings (CORS) that allow every origin (`*`), or that echo back
whatever origin asks, especially together with cookies or credentials.

**Grade:** 🔴 any origin allowed together with credentials. 🟡 any origin allowed on an API
that serves private data. 🟢 limited to the site's own addresses.

**Explain:** this setting decides which other websites may talk to the server on a visitor's
behalf. Left open, a malicious page can use a logged-in visitor's session.

**Fix:** list the site's own domains instead of allowing all.

### F3. No page for "not found" or "something broke"

**Look for:** custom not-found and error pages; loading and empty states on the main screens.

**Grade:** 🟡 either page is missing. 🟢 both are present.

**Explain:** a visitor who hits a dead link or an error sees a raw technical page and leaves.

**Fix:** add simple not-found and error pages with a way back to the home page.

### F4. Leftovers from building

**Look for:** `console.log` or print statements that output user data, tokens or full
responses; test, debug or seed routes (`/test`, `/debug`, `/seed`, `/api/reset`); large
commented-out blocks holding old keys.

**Grade:** 🔴 a debug or seed route that exposes or resets data and is reachable.
🟡 logging of personal data, other leftovers. 🟢 clean.

**Explain:** tools left behind from building are open to the public once the site is live.

**Fix:** remove debug routes and stop logging personal data.

### F5. Placeholder content still in place

**Look for:** sample text ("lorem ipsum"), `TODO` and `FIXME` in user-facing code, fake
contact details, example product data, default page titles and icons from the starter template.
Look also for promises on the site that the code does not keep: security claims, feature
counts, numbers of users.

**Grade:** 🟡 placeholders or unkept promises visible to visitors. 🟢 none.

**Explain:** nothing breaks, but it tells every visitor the site is unfinished. A promise
about security or privacy that the code does not keep is worse than filler: name the finding
that contradicts it.

**Fix:** replace or remove each one.
