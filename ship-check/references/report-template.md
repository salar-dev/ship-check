# Ship Check — report template

Use this structure for every report. Replace the text in `<angle brackets>`. Leave out a
section's findings when it has none, but keep the heading and write "None."

Write the report in English unless the user asked for another language (see SKILL.md). In
any language, keep the marks, check IDs, file paths and code as they are.

---

```markdown
# Ship Check report — <project name>

**Checked:** <date> · **Built with:** <stack in a few words> · **Scanned:** <folders or scope>

> Keep this file private. It lists this project's weak points, so do not commit or publish it.

## Result

🔴 <n> to fix before launch · 🟡 <n> to fix soon · 🟢 <n> passed · ⚪ <n> not checked

**<Verdict line>**

## Start here

<Only when there are red findings. Two to six numbered lines naming the underlying causes
behind them, in the order to fix them. Each line says what to do in a few words and which
red findings it clears. Every red finding belongs to exactly one line.>

## 🔴 Fix before launch

### 1. <What can happen, in plain words>

- **Found in:** `<file>:<line>` <short snippet if it helps; secrets masked>
- **Why it matters:** <one or two sentences, everyday words>
- **How to fix:** <concrete steps: which file, what to change>
- **Check:** <ID>

### 2. <…>

## 🟡 Fix soon

### 1. <What can happen, in plain words>

- **Found in:** `<file>:<line>`, or what was looked for and not found
- **Why it matters:** <one or two sentences>
- **How to fix:** <concrete steps>
- **Check:** <ID>

## 🟢 Passed

- <ID> <check name> — <a few words on what was confirmed>

## ⚪ Not checked

- <ID> <check name> — <why: does not apply, or cannot be seen from the code>.
  <The question for the owner, if there is one.>

## About this check

Ship Check reads your code and looks for common mistakes that hurt websites at launch.
It is not a full security audit, and it cannot guarantee a site is secure: it does not test
the live site, your hosting settings, or anything outside this folder. Fix the red items,
run it again, and for a site that handles payments or sensitive data, have a professional
review it too.
```

---

## The verdict line

Pick the one that matches, and add the main reason in the same sentence.

- Any red: **Not ready to launch.** <the worst consequence, e.g. "Right now a stranger can
  read your customers' details.">
- No red, some yellow: **No launch blockers found by these checks.** <n> things to fix soon.
- All green: **No problems found by these checks.**

Do not write "secure", "safe" or "ready" as a promise in any verdict.

## Counting

The four numbers in the Result line count checks, not places in the code. Every check gets
exactly one mark, so the numbers add up to the number of checks in the check list, and each
check appears once in the report under its mark.

## Writing the findings

- The title of a finding is the consequence ("Anyone can open the admin page"), not the
  category ("Broken access control").
- Order the red findings to follow "Start here": all findings of the first cause, then the
  second, and so on. Inside a cause, the most damaging first. The report then reads as a
  work plan from top to bottom.
- If one mistake appears in many places, write one finding and list the places.
- If one check catches several different mistakes, keep it one finding, title it by the
  worst, and list the others as bullets under "Found in".
- Mask every secret as SKILL.md describes, in snippets too.
- Keep "Passed" and "Not checked" to one line each: the owner should spend their attention
  on red and yellow.
