# Ship Check

A free skill for Claude that gets a website or web app ready to launch.

You built a site with AI tools. It works on your computer. Ship Check reads the project and
tells you, in plain words, what to fix before real visitors arrive, and then helps you fix it.

[العربية](README.ar.md)

## What it does

Type `/ship-check` in Claude Code and pick one of five modes:

| Mode | What you get |
|---|---|
| **Launch check** | A red / yellow / green report of the mistakes that hurt at launch: exposed keys, pages and data anyone can reach, unchecked input, missing safety nets. 28 checks. |
| **Bug hunt** | What is broken, or will break for real visitors, most painful first. |
| **Code cleanup** | A project that is easier to change without breaking it. The site keeps working the same way. |
| **UI review** | Layout, readability, phones, loading and error states. Your colors and design stay yours. |
| **Go live** | A step-by-step plan to move from your computer to the internet: hosting, database, login, AI, payments, domain. Each step says who does it: you or Claude. |

The Launch check report ends with a **Start here** section. It groups the findings by their
root cause and puts them in order, so a long list becomes a few things to fix.

## What it will not do

- **Change anything without your yes.** Checking never edits your project. Fixes happen one at a time, after you pick them.
- **Touch your live site.** It works on your local copy only.
- **Show your secrets.** It does not open your settings files, and any key it finds in the code is masked in the report.
- **Tell you the site is secure.** Ship Check is a check, not a guarantee. It catches common mistakes by reading code. It is not a security audit, and it cannot prove a site is safe. The best result it gives is "no problems found by these checks".

## Install

You need [Claude Code](https://claude.com/claude-code). Python 3 makes the first scan faster, but the skill works without it.

**By hand**

1. On this page, click **Code**, then **Download ZIP**, and unzip it.
2. Move the folder named `ship-check` into Claude's skills folder:
   - macOS and Linux: `~/.claude/skills/`
   - Windows: `%USERPROFILE%\.claude\skills\`

   Create the `skills` folder if it is not there. You should end up with `.claude/skills/ship-check/SKILL.md`.

**With the terminal (macOS and Linux)**

```bash
git clone https://github.com/salar-dev/ship-check.git /tmp/ship-check && mkdir -p ~/.claude/skills && cp -R /tmp/ship-check/ship-check ~/.claude/skills/
```

## Use

1. Open your project folder in Claude Code.
2. Type `/ship-check`. If it does not appear in the list, type `/reload-skills` or restart Claude Code.
3. Pick a mode, or just say what you want: "is this safe to launch?", "where should I host this?".

If you are about to launch, the useful order is: Launch check, fix what is red, then Go live.

## Good to know

- It is not tied to one stack. If a result looks wrong on your project, please open an issue.
- Files the skill writes (the report, the launch plan) are in English, so any developer can read them. The chat follows your language.
- Prices and limits of hosting and other services change. The skill tells you to confirm them on the provider's own page.

## Feedback

Found a false alarm, or a mistake it missed? Open an issue here, or message
[@salar_dev](https://instagram.com/salar_dev) on Instagram.

## License

MIT. Created by Salar Dev ([@salar_dev](https://instagram.com/salar_dev)).
