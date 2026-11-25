# Launch check

A red / yellow / green report of the mistakes that hurt a site at launch. This mode only
looks: it changes nothing until the owner asks for fixes at the end.

Accuracy matters more than speed here. A wrong line number or a false alarm teaches the
owner to distrust the whole report, so every step below is built to keep you exact.

## 1. Read the two reference files, once

Read `references/checks.md` (every check, how to grade it, how to explain it) and
`references/report-template.md` (the fixed report layout) now, before opening the project
files. Knowing all the checks up front lets one pass over the code serve every check.

## 2. Read the code the scan points to

You already have the scan from Step 1. Use it as the map:

- Open every file in the scan's **Server endpoints** table and under **Pattern hits**, and
  the login, database and payment code they lead to.
- Do not open the settings files themselves (`.env` and the like). The scan already lists
  each setting's name, whether it has a value, whether it is public, and whether git tracks
  the file, which is everything the checks need. Their values are secrets you do not need to see.
- In a small project (under about 60 source files), read all the server-side code and every
  page that handles login, money or personal data.
- Read several files in each step rather than one at a time: it is faster and you compare
  them better side by side.
- Work out which code runs in the visitor's browser and which on the server. This matters
  more than anything else, because anything sent to the browser can be read by anyone.

The scan's columns are hints, not verdicts. "Login words in file: NONE" means look closely;
it does not replace reading the endpoint.

Then run the package manager's audit if there is one (`npm audit --omit=dev`, `pnpm audit`,
`pip-audit`, `composer audit`, `bundle audit`). It sends the list of package names and
versions to the package registry, and that is the only network call this mode makes. Useful
read-only git commands if you need more than the scan gave: `git ls-files`, `git log`,
`git check-ignore`, `git remote -v`. Do not install anything, do not start the app, and do
not run anything that writes.

## 3. Mark every check

Give each check in `checks.md` exactly one mark:

| Mark | Meaning |
|---|---|
| 🔴 Red | Someone could do damage today: read or change other people's data, spend the owner's money, take over the site, or lose data for good. Fix before launch. |
| 🟡 Yellow | Not an open door, but it will cause trouble: breaks under real use, hides problems, or gets riskier with time. Fix soon. |
| 🟢 Green | You looked for the problem and did not find it. |
| ⚪ Not checked | Does not apply to this project, or cannot be seen from the code. Say which, and ask the owner the question that would settle it. |

Tool and framework names in the check list are examples; apply the same idea to whatever this
project uses.

Decide all the marks before writing anything. Then find the few underlying causes behind the
red marks: in most projects a dozen red findings come from three or four causes (keys in the
wrong place, no login check on the server, input used as-is). Those causes become the
report's "Start here" list, and they are what makes the report a plan instead of a scare.

## 4. Write the report

Follow `references/report-template.md` exactly, so every report looks the same and one run
can be compared with the next. Write it in one go, in English unless the owner asked for
another language.

For each finding:

- Lead with the consequence, not the technical name.
- One or two sentences on why it matters, in everyday words.
- A fix the owner can do or hand to their AI tool: which file, what to change.

**Example**

Too technical:
> IDOR vulnerability in `/api/orders/[id]`: missing ownership validation.

Clear:
> **Any logged-in customer can open any other customer's order.**
> `api/orders/[id].js:12` loads the order by its number and never checks who is asking.
> Changing the number in the address bar shows someone else's name, address and purchase.

Save the report as `ship-check-report.md` in the project root.

## 5. Check the report before delivering it

```bash
python3 scripts/check_report.py <project folder> <project folder>/ship-check-report.md
```

It confirms that every `file:line` you cited exists, that no secret appears unmasked, that
the counts match the findings and every check has exactly one mark, and that no line reads
like a promise. Fix whatever it lists and run it again until it is clean. If Python is not
available, do the same four checks by eye.

## 6. Deliver it

In the chat, give a short summary: the counts, the verdict line, the "Start here" causes, and
the red findings by title. Tell the owner the report is in English and offer it in their
language if the conversation is in another one.

The report is a map of the project's weak points, so tell the owner to keep it private: it
should not be committed or deployed. If the project uses git, suggest adding the file name to
`.gitignore`, without editing it yourself.

Ask any question the ⚪ marks raised (backups, hosting), all in one message.

## 7. Offer the fixes

Offer to fix the red findings in the "Start here" order, one cause at a time. When the owner
says yes:

- Do one cause, then say what changed and in which files.
- Some steps are the owner's alone: replacing a leaked key in a provider's dashboard, turning
  on backups, choosing a host. Give them the exact place to click and wait.
- When a fix needs a service the project does not have (a real login, a hosted database, rate
  limiting), do not invent a home-made one. Read the matching part of `references/backend.md`
  or `references/services.md`, offer one recommendation and one alternative, and let the
  owner choose.
- After the red causes are done, run the scan and this check again, and show what moved from
  red to green.
