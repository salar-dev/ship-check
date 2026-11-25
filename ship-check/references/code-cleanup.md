# Code cleanup

Make the project easier to change without breaking it. AI-built projects tend to work and
then become hard to extend: the same logic pasted in five places, one file that does
everything, folders that follow no pattern. The aim is a project the owner, their AI tool or
a hired developer can find their way around.

This mode is not a rewrite. The site must behave exactly the same after every step.

## 1. Read the shape of the project

From the scan and the folders, work out:

- **Which structure it is trying to follow.** Every framework has a recommended layout. Find
  the one for this project's framework and compare. If the owner names a structure they want
  (by feature, by layer, a specific pattern), that is the target instead.
- **Where things live now**: pages, shared components, data access, calls to outside
  services, settings, helpers.
- **The pain points**, with file names:
  - the same code repeated in several places
  - files that do several unrelated jobs, or are far longer than their neighbours
  - database or outside-service calls scattered through page code instead of sitting in one place
  - settings and addresses typed into many files instead of read from one
  - dead code: files nothing imports, commented-out blocks, unused packages
  - names that mislead, or three names for the same thing
  - no README that says how to run the project, no example settings file
  - nothing that would catch a mistake: no types, no tests on the paths that matter

The scan does not measure tidiness. Count lines per file, look for repeated blocks and for
files nothing imports yourself; a few searches are enough.

Before proposing anything, settle how each step will be proved. Find what the project has: a
build, a type check, tests, a linter. If it has none, say so, and the proof becomes a build
plus opening the affected pages before and after. Ask before running a build, since it
writes files.

## 2. Propose a short plan

Give the owner three to seven steps, in the chat. For each:

- what moves or changes, in a sentence a non-programmer follows
- why it helps ("one place to change the price instead of four")
- how risky it is, and how you will prove nothing broke

Order them so that each step stands on its own and the safest, most useful ones come first.
A good first step is usually the one that removes repetition around the thing the owner
changes most often; take that from what they complained about, or ask in the same message.
Leave out anything that is only taste.

Two cases need care. Copies that are almost but not quite the same (three feature lists with
different wording) cannot be merged without changing what visitors see: leave them, and ask
the owner which version they want. And when code that is unsafe has to move, move it exactly
as it is and say so; making it safe is a behaviour change that belongs to the Launch check.

Say what you are leaving alone and why. A working, ugly file that nobody needs to touch can
stay ugly.

## 3. Do it one step at a time

With the owner's yes for each step:

- Before the first change, make sure there is a restore point (ground rules).
- Change structure only. If you notice a bug or a security problem, note it for the Bug hunt
  or the Launch check; fixing it here would hide a behaviour change inside a tidy-up.
- After each step, run what proves the site still works (build, type check, tests, or the
  main pages in a browser) and say what you ran and what it showed.
- Update imports, the README and any example settings file in the same step, so the project
  is never left half-moved.
- Stop and ask before anything large: renaming many files, swapping a library, changing how
  data is stored.

## 4. Leave a map

When the plan is done, add or update a short "Project structure" section in the README: the
main folders, one line each on what belongs there. It is what lets the next person, or the
next AI session, put new code in the right place.
