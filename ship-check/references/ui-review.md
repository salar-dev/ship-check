# UI review

Make the site look and feel better to the people who use it. The goal is a site that is
clear, consistent and comfortable on a phone, in the owner's own style. It is not a redesign:
keep their colours, their brand and their layout unless they ask for something new.

## 1. Look at the site the way a visitor does

Reading the code tells you a lot; seeing the pages tells you more. Ask the owner, once,
whether the site is running on their computer or whether they can send screenshots, and
wait for the answer. If it is running and you have a browser or screenshot tool, open the
main pages at a phone width and at a desktop width. If neither is possible, work from the
code and say so: judge layout at a phone width of about 375 pixels, and label anything about
size or position ("the button falls below the first screen") as an estimate to confirm by eye.

In this mode the useful parts of the scan are the pages list and the layout section; find
the shared style files and components yourself. The lettered pattern hits belong to the
Launch check: if they show something alarming, say so in one line at the end and recommend
that mode, without grading it.

Pick the pages that matter: the first page a visitor lands on, sign-up or login, the page
where the main action happens, and any page that takes money. Tell the owner which pages you
reviewed and which you left out.

## 2. Check these, in this order

The order runs from what loses visitors to what merely looks rough.

1. **Can they tell what to do?** One clear main action per screen, a headline that says what
   the site is, the important thing visible without scrolling.
2. **Does it work on a phone?** Nothing cut off or scrolling sideways, text readable without
   zooming, buttons big enough for a thumb, forms usable with the on-screen keyboard.
3. **Does every state have a screen?** Loading, empty ("no orders yet"), error, success,
   disabled. AI-built sites usually design only the happy case.
4. **Forms.** A visible label on every field, an error message next to the field that says how
   to fix it, the right keyboard for emails and numbers, nothing lost when a submit fails.
5. **Can everyone read it?** Enough contrast between text and background (work out the ratio
   from the colours; small text needs at least 4.5 to 1), text not too small,
   links and buttons that look like links and buttons, a visible outline on the focused
   element, meaningful text on images and icon-only buttons.
6. **Is it consistent?** One set of spacings, corner radii, button styles and font sizes,
   used the same way on every page.
7. **Language and direction.** If the site is in a right-to-left language, check that layout,
   icons with a direction (arrows, back buttons) and mixed-direction text such as phone
   numbers and emails all read correctly.
8. **Does it feel fast?** Large images, layout that jumps as things load, a blank screen while
   waiting.
9. **Words.** Buttons that say what they do, no filler text, no claims the site cannot back.

## 3. Report the improvements

In the chat, give the five to eight changes that would help most. Group related problems
into one change when one piece of work fixes them, and list what the group covers. For each:

- **What a visitor experiences now**, in a sentence.
- **Where**: the page, and `file:line` when you have it.
- **The change**, concretely: what it becomes.
- **Size**: small (minutes), medium, or large.

Order the list by how much each change helps visitors, most first, and mark the small ones
as quick wins so the owner can start there. Say what already works well in a line or two:
it tells the owner what not to break.

A screen that gets stuck or lies (a spinner that never stops, "success" shown without
checking) is a missing state and belongs here. A deeper fault behind it (the payment never
happens) belongs to the Bug hunt or the Launch check: name it in a line and point there.

## 4. Apply them

Offer to make the changes from the top. With the owner's yes:

- One change at a time, kept inside the owner's existing style: reuse their colours, spacing
  and components rather than introducing new ones.
- Show the result when you can (a screenshot, or the page to open) and say which files changed.
- Fix a shared component once rather than patching each page that uses it.
- Check the phone width again after layout changes.

If the owner wants a larger change of look, ask what they want it to feel like and for one or
two sites they like, then propose a direction before touching the code.
