---
name: fluid-brand-setup
description: >-
  Interview a company to build their brand.md — a living brand-voice document
  that Mist, themes, portals, and widgets read to match the company's tone and
  style. Use when the user wants to set up their brand, create a brand guide,
  define their brand voice, describe their tone of voice, write brand
  guidelines, document their mission/values/audience, or asks things like
  "set up my brand," "help me write our brand guidelines," "define our brand
  voice," "brand setup," "what's our tone of voice," or "add to our brand
  guide." Also use when a brand decision is made mid-conversation (a new tone
  rule, a phrase to avoid, a competitor comparison) and it should be captured
  for later.
metadata:
  version: 1.0.0
---

# Fluid Brand Setup

Runs a focused interview to produce (or extend) a company's **brand.md** — a
prose document describing how the company sounds, who it's for, and what
"on-brand" looks like. Mist apps, themes, portals, and widgets all read this
file to generate copy, pick tone, and make style decisions that feel like the
company wrote them.

This is a **voice and style** document. Structured brand data — logo, color
swatches, fonts — lives in the company's brand guidelines fields (accessible
via the Fluid API / admin Brand Guidelines settings page), not in brand.md.
When colors or a logo are relevant to a question below (e.g. visual style),
pull them from those structured fields if available, and describe how they're
*used* in prose rather than re-listing hex codes.

## Two modes: first setup vs. addition

- **First setup** — `brand_md` is empty or the user wants to (re)build the
  whole doc. Run the full staged interview below, then write the complete
  document.
- **Addition** — brand.md already exists and the user just made a decision
  worth capturing ("never say 'cheap', always say 'affordable'", "we're going
  more playful now"). Skip the interview. Draft a short addition to the
  relevant section (or a new bullet under it) and append it — do not
  re-interview or rewrite unrelated sections.

Before starting, check whether brand.md already exists (see "Reading the
current state" below) and skip any question you can already answer from it.
Never make the user re-answer something already on the page.

## Reading the current state

- **Inside Mist**: the agent's context typically already includes the current
  brand.md content (injected as a `<brand_voice>` block). Use that — don't ask
  the user to repeat what's already there. If the block is empty or missing,
  treat this as first setup.
- **Elsewhere** (Claude Code, claude.ai, etc.): look for an existing
  `brand.md` in the project/working directory the user points you to. If
  found, read it and treat as an addition; if not, treat as first setup.

## The interview

Ask in small, focused batches — never dump all questions at once. 2-4
questions per batch, in plain language, with a short example so the user
knows the shape of a good answer. Skip any question you can already answer
confidently from context (an existing brand.md, a scraped website, prior
conversation). After each batch, briefly reflect back what you heard before
moving on, so the user can correct course early.

Suggested order (skip/reorder as context demands):

**Batch 1 — Overview & mission**
1. In a sentence or two, who are you and what do you sell?
2. What's the "why" behind the company — the mission or belief that drives
   decisions?
3. What are the 3-5 values that guide how you operate? (e.g. "sustainability
   over speed," "customer obsession")

**Batch 2 — Tone of voice**
4. If your brand were a person talking to a customer, how would they sound?
   Give 2-3 adjectives (e.g. "warm, direct, a little playful — never
   corporate").
5. Do you have an example of copy (an email, a product description, a social
   post) that feels exactly right? Paste it or link it.
6. Anything that feels *off-brand* when you see it? (too formal, too silly,
   too salesy, etc.)

**Batch 3 — Audience**
7. Who's your primary customer? Age range, lifestyle, what they care about.
8. Any secondary audience worth calling out (gift buyers, resellers,
   B2B buyers)?

**Batch 4 — Vocabulary & naming**
9. Words or phrases you always use (or want to start using) — product names,
   category terms, signature phrases?
10. Words or phrases to avoid — competitor terms, jargon, anything that reads
    wrong for your brand?
11. Any capitalization or naming conventions? (e.g. product names always
    Title Case, never call it an "order," always a "drop")

**Batch 5 — Visual style**
12. If the company has existing brand guidelines with colors/logo already on
    file, pull them and confirm: "I see your primary color is `#...` — how
    would you describe how it's used? Bold accents, or mostly neutral with a
    pop of color?" If nothing's on file, ask the user to describe their
    palette in words.
13. How would you describe your typography — modern/geometric, classic/serif,
    handwritten/friendly, technical/mono?
14. Imagery style — photography vs. illustration, bright vs. moody, people-
    forward vs. product-forward?
15. Roundedness/sharpness — soft rounded corners and shapes, or sharp/angular?

**Batch 6 — Inspiration & guardrails**
16. Are there brands or sites you admire — for their voice, their look, or
    both? What specifically do you like about each?
17. Any hard do's and don'ts? (e.g. "always mention our guarantee," "never
    use exclamation points," "never disparage competitors by name")

Adapt the batches to the conversation — if the user answers three questions
in one breath, don't re-ask them. If they're clearly in a hurry, offer to
draft with what you have and mark gaps with the template's built-in prompts
for them to fill in later.

## Assembling brand.md

Use this **exact** skeleton — headings must match verbatim (word for word,
same casing and order) so future automated edits target the right section.
This is the same template Mist ships when `brand_md` is empty, so a document
built here is indistinguishable from one started in Mist.

```markdown
# Brand Guide

_A living document. Sections are prompts — fill in what's true for your brand and
delete what isn't. Agents (Mist, themes, portals, widgets) read this to match
your voice and style._

## Brand Overview
<!-- One paragraph: who you are, what you sell, what you stand for. -->

## Mission & Values
<!-- Why you exist; the 3-5 values that guide decisions. -->

## Tone of Voice
<!-- How you sound. e.g. "Warm, direct, a little playful. Never corporate." -->

## Audience
<!-- Who you're speaking to. Primary + secondary personas. -->

## Vocabulary & Naming
<!-- Words you use / avoid. Product naming conventions. Capitalization rules. -->

## Visual Style
<!-- Color usage, typography feel, imagery style, spacing/roundedness. -->

## Do's and Don'ts
<!-- Concrete guardrails. "Do X." "Never Y." -->

## Brands & Sites We Admire
<!-- Links + one line on what you like about each. -->

## Examples
<!-- Snippets of on-brand copy, taglines, product descriptions. -->
```

Fill each section from the matching interview batch:

| Section | From batch |
|---|---|
| Brand Overview | 1 |
| Mission & Values | 1 |
| Tone of Voice | 2 |
| Audience | 3 |
| Vocabulary & Naming | 4 |
| Visual Style | 5 |
| Do's and Don'ts | 6 (guardrails) |
| Brands & Sites We Admire | 6 (inspiration) |
| Examples | pulled from batch 2's example copy, plus anything else volunteered |

Write in the user's own words where possible — this is their voice, not a
generic template filled in by an AI. If a section has nothing to say yet,
leave the HTML comment prompt in place rather than inventing content; the
comment doubles as a placeholder for later.

For an **addition** (brand.md already exists), don't regenerate the whole
document — draft a short paragraph or bullet for the one relevant section
and append it there, leaving everything else untouched.

## Attribution

Every block of content the agent adds — whether the initial full draft or a
later addition — ends with a trailing attribution line:

```
_(— {UserName})_
```

Resolve `{UserName}` from the authenticated Fluid user's display name.
Fall back to the company name if no user name is available, then to
`"Unknown"` as a last resort. Admin free-text edits made directly in the
fluid-admin Brand Guidelines settings page are not auto-attributed this way —
attribution is an agent-authored-content behavior, not something applied to
whole-document manual edits.

Example addition with attribution:

```markdown
## Vocabulary & Naming
<!-- Words you use / avoid. Product naming conventions. Capitalization rules. -->

Always "members," never "customers." Always "drops," never "releases."

Avoid "cheap" — use "accessible" or "everyday-priced" instead. _(— Priya)_
```

## Saving the document

**If the `update_brand_voice` tool is available** (running inside Mist
Desktop):

- **First setup**: call it with `mode: "replace"` and the full assembled
  document as `content`. The tool handles `(Name)` attribution and syncing
  the doc back to the Fluid API (`brand_md` on brand guidelines) for you —
  don't append the attribution line yourself in this case, since the whole
  document isn't "added content" from one person, it's the baseline. (If the
  tool signature in your build additionally accepts a `section`, you may pass
  it for targeted first-setup writes, but a full replace is the common case.)
- **Later additions**: call it with `mode: "append"` and just the new
  section/paragraph as `content`. The tool adds the `(Name)` attribution and
  pushes the update to the API.
- If the API sync fails (backend not yet available, network error), the tool
  degrades gracefully and keeps the local copy — mention this to the user
  rather than blocking on it.

**If running outside Mist** (Claude Code, claude.ai, or any environment
without that tool):

- Write the assembled markdown directly to a `brand.md` file. Ask the user
  where it should live if it's not obvious (repo root, a `docs/` folder, or
  wherever they keep company documents) — do not silently pick a path in a
  project you don't own.
- Add the `(Name)` attribution line yourself, the same format as above, for
  any addition you make (not for a from-scratch first draft you're handing
  off for review).
- Tell the user clearly where the file was written, and remind them: if this
  company also uses Mist, brand.md lives per-company in the Mist workspace
  and syncing this file there (or pasting its content into the fluid-admin
  Brand Guidelines page) is what makes Mist and themes pick it up.

## After saving

Briefly summarize what was captured, note any sections left as placeholders
for later, and mention that:

- Colors, logo, and fonts are managed separately as structured brand
  guidelines fields (not in this file) — point the user to the fluid-admin
  Brand Guidelines settings page if they want to set/change those.
- Future brand decisions can be captured incrementally — just describe the
  decision and this skill (or the `update_brand_voice` tool directly, inside
  Mist) will append it with attribution rather than rewriting the whole
  document.
