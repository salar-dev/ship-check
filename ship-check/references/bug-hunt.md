# Bug hunt

Find what is broken, or will break, for real visitors, and fix it. This is about the site
working, not about attackers: for exposed keys and open doors, use the Launch check.

## 1. Learn what the site is supposed to do

From the scan and the pages, list the three to six things a visitor comes to do (sign up,
log in, the main action, pay, see their results). Say the list to the owner in one line each,
and in the same message ask whether the site is running on their computer. Wait for the
answer: bugs only matter relative to what the site is for. The owner's own admin screens are
not a visitor path unless the owner asks for them.

In this mode the useful parts of the scan are the pages, the endpoints table and "Settings
the code reads". Its lettered pattern hits belong to the Launch check.

## 2. Follow each of those paths through the code

For every path, read it end to end: the page, what it sends, the server code that receives
it, the database call, and what comes back to the page. Most bugs in AI-built projects sit at
the joins between these, so compare both sides of each join:

- The page sends one shape and the server expects another (a field named differently, a
  number sent as text, a missing field).
- The server answers with an error and the page treats it as success, or never stops loading.
- A step works only with data that exists on the builder's machine (sample accounts, a local
  file, a fixed address such as `localhost`).
- Something asynchronous is not waited for, so the next line runs too early.
- A condition is the wrong way round, or handles only the happy case (empty list, first-time
  user, logged-out visitor, very long text, a second click on the same button).
- A link or redirect points to a page that does not exist.
- A setting the code reads is not defined anywhere (the scan lists these).
- Dates, money and counts: time zones, rounding, off-by-one at the edges.

Where the project has its own checks, run them and read the output: a type check, a linter,
a test suite, a build (`npm run lint`, `npm run build`, `pytest`, and similar; the scan lists
the project's scripts). Ask before running anything that writes files or installs something:
a build always does, and a linter does when it is not yet set up in the project. If the
owner has the site running locally and you have a browser tool, walking a path in the
browser confirms a bug better than reading does. Never test against a live site.

When a path leads into a file the scan flagged for holding a key or password, you do not
need the value: work from the scan's masked line and the code around it.

## 3. Report the bugs, most painful first

Keep it short: the ten that matter most at the most, in the chat (no file unless the owner
asks). For each one:

- **What the visitor sees**, in a sentence.
- **Where**: `file:line`. When the same mistake sits in several places, it is one bug with
  several places.
- **How sure**: *confirmed* (you ran it or the code leaves no doubt) or *likely* (it depends on
  something you could not see; say what). A mistake that is certainly in the code but only
  shows when something else fails is confirmed; say when it shows.
- **Fix**: what to change.

Order by how many visitors hit it and how badly. A crash on sign-up outranks a wrong label on
a settings page. Leave style preferences out: this list is for things that are wrong.

Some things you find belong to another mode: an open door (Launch check), a choice of
database or host (Go live), a confusing screen (UI review). If one of them also breaks
something for an ordinary visitor, list that visible half as a bug. Then name the rest in a
short paragraph, a phrase each, without grading them, and recommend the mode that covers them.

## 4. Fix them

Offer to fix the list from the top. With the owner's yes:

- Fix one bug at a time and keep each change as small as the bug.
- After each, run whatever check proves it (the test, the build, the path in the browser) and
  say what you ran and what it showed. If nothing can prove it, say that plainly.
- If fixing one reveals another, add it to the list instead of widening the change.
