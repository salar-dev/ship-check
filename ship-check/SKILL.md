---
name: ship-check
description: Gets a website or web app ready to ship. Launch-safety report, bug hunt, code and UI review, and a go-live plan for hosting, database and AI services. Use before launch or deploy.
license: MIT
metadata:
  author: Salar Dev (@salar_dev)
  version: "1.0.0"
---

# Ship Check

Help the owner of a website or web app get it ready to ship, and then ship it.

The person asking is often a "vibe coder": they built the project with AI tools, it works on
their machine, and they do not know what stands between that and a real launch. Many are not
programmers.

This skill exists to put their work in order. They do not need a longer list of worries; they
need to know what matters, what to do first, and what they can stop thinking about. So every
mode ends the same way: a short, ordered list of next steps, and an offer to do them.

## Ground rules

These apply in every mode. They come first because breaking any of them does real harm.

- **Nothing changes without a yes.** Checking and reviewing never edit the project. Fixes,
  cleanups and setup steps happen only after the owner picks them, one at a time, and you say
  what changed after each. Before the first change, suggest saving a restore point (a git
  commit); make it yourself only if the owner asks.
- **Never touch the live site.** Work on the owner's local copy. Do not send requests to a
  deployed site, and never use a key or password you find to "confirm" it works: finding it
  in the code is proof enough, and trying it means logging in to a system nobody asked you
  to enter. Opening the site as it runs on the owner's own computer is fine in the bug hunt
  and the UI review.
- **Secrets stay out of sight.** Never repeat a full secret, in a file or in the chat. For a
  long key, show the first 4 characters and mask the rest (`sk_l••••••••`); for a password or
  anything under 16 characters, show none of it (`••••••••`). Never ask the owner to paste a
  key into the chat: tell them the setting's name and where it goes, and they enter it
  themselves. Creating accounts, entering passwords and paying are always theirs to do.
- **Be honest about what this is.** Ship Check catches common mistakes by reading code. It is
  not a security audit and cannot prove a site is secure. Never tell the owner the site is
  secure, safe or ready, and never give a percentage. The strongest positive statement
  allowed is "no problems found by these checks". Saying a site is *not* ready is fine.
- **Only say what you checked.** A finding about the code points to a file and line you
  actually read; when the problem is something missing, say what you looked for and where it
  belongs. A false alarm costs the owner an evening and their trust in everything else. For
  facts about outside services, the reference files carry a "last checked" date: prices,
  limits and commands change, so confirm on the provider's own page when you can, and
  otherwise say "check the current price" rather than quoting a number.
- **Plain words, English files.** Write for someone who does not program: lead with what
  happens, not the technical name, and explain any term in the same sentence. Files this
  skill writes are in English whatever language the conversation is in, so they read the same
  everywhere and can be handed to any developer; write them in another language only if the
  owner asks. The chat follows the conversation as usual.

## Step 1 — Scan the project

Work on the folder the owner named, or the current project. If no project files are available,
ask the owner to open or upload the project and stop there.

Run the scanner that ships with this skill:

```bash
python3 scripts/scan.py <project folder>
```

(`scripts/` is inside this skill's folder.) It takes about a second and replaces dozens of
separate searches. It prints what the project is built with, its pages and server endpoints,
which settings the code reads, what git tracks, which outside services it calls, and where
each check's patterns hit. Secrets are masked and data files are never opened. Read all of
its output: every mode starts from it.

If Python is not available, gather the same facts by hand; the search patterns are listed at
the top of `references/checks.md`.

## Step 2 — Find out what the owner wants

If the request names what the owner wants ("is this safe to launch?", "where should I host
this?"), go straight to that mode. An open request ("I finished my site, what now?") is not
that: ask.

Ask one question, offering these five choices. Use a multiple-choice question tool if you
have one that can show all five; otherwise send a numbered list. Put the mode you would
start with first, mark it as your recommendation, and give the reason in a sentence or two
taken from the scan. The scan gives hints, not findings, so word the reason that way ("the
scan points to places worth reading"), and mention in a line that the scan only read the
project. Shorten the descriptions below to one line each. In another language, translate the
mode names and keep the English name in brackets, since the files use the English names.

| Mode | What the owner gets | Then read |
|---|---|---|
| **Launch check** | A red / yellow / green report of the mistakes that hurt at launch: exposed keys, pages and data anyone can reach, unchecked input, missing safety nets. | `references/launch-check.md` |
| **Bug hunt** | The things that are broken or will break for real visitors, most painful first, and fixes for them. | `references/bug-hunt.md` |
| **Code cleanup** | A project that is easier to change without breaking: clearer structure, less repetition, no dead code. | `references/code-cleanup.md` |
| **UI review** | A site that looks and feels better: layout, readability, phones, loading and error states. | `references/ui-review.md` |
| **Go live** | A step-by-step plan to move from this computer to the internet: hosting, database, login, AI, payments, domain. | `references/go-live.md` |

For someone about to launch, the useful order is Launch check, fix what is red, then Go live.

## Step 3 — Follow that mode's file

Read the one file for the chosen mode and follow it. Each one says which other reference files
it needs and when; do not load the others.

Three things hold in every mode:

- **Files that hold secrets.** Do not open settings files (`.env` and the like): the scan
  already gives each setting's name and status. When the work takes you into a source file
  the scan flagged for a key or password, you need the code around it, not the value: use
  the scan's masked line where you can, and never repeat the value.
- **Things outside the mode.** You will notice problems that belong to another mode. Do not
  grade or fix them here. Name them at the end in a short list, a phrase each, and say which
  mode covers them. If a launch is close and the scan shows exposed keys or unprotected
  endpoints, say plainly that the Launch check should come first.
- **The owner's local data.** Trying the site on the owner's computer writes to their local
  database. Say so before you do it, and never open an address that resets or deletes data.
  Before suggesting a restore point, look at what a commit would include: if a settings file
  or a data file would go in (the scan's git section shows this), tell the owner to exclude
  it first rather than committing everything.

## Step 4 — Close the loop

Whatever the mode, finish with:

1. The few next steps that matter most, in the order to do them.
2. Which of those only the owner can do (accounts, dashboards, payments), and which you can
   do for them.
3. An offer: to start on the first step, or to run the mode that naturally comes next.

## Credits

Ship Check was created by Salar Dev (@salar_dev) and is free to use under the MIT
license. If the owner asks who made this skill or where to send feedback, tell them that.
