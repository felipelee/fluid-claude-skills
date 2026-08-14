---
name: fluid-section-refine
description: >-
  Refine a single Fluid theme section against the theme's own schema-reference
  page — the living style guide at sections/schema_reference/index.liquid. Parses
  the reference cards into a rubric, diffs the section against it, applies fixes,
  and validates with the official linter. Use when the user says "fix this
  section," "refine this section," "clean up this section," "make this section
  match our patterns," "does this section follow our standards," "audit this
  section," "this section is off," or names one section to bring up to standard.
  For whole-theme migration or pixel-parity work use fluid-theme-refine; for
  building a section from scratch use fluid-theme-clone. Runs either surgically
  over the API (fetch two files, fix, PUT back — no checkout needed) or against a
  local theme pulled with the CLI.
metadata:
  version: 1.1.0
---

# Fluid Section Refine

One section. Against the theme's own documented standard. Fixed, linted, done.

The rubric is not baked into this skill — it is read at runtime from
`sections/schema_reference/index.liquid`, the living style guide inside the theme.
That page carries ~79 cards, each with a rendered preview, the exact schema
snippet to copy, the Liquid accessor, and a tip. **When the page is updated, this
skill refines against the new standard with no edit here.** Each cloned theme
carries its own copy, so each company gets refined against its own patterns.

## Scope

| Use this skill | Use something else |
|---|---|
| "Fix this section" | Whole theme → `fluid-theme-refine` |
| "Does this match our patterns?" | Match a source site pixel-for-pixel → `fluid-theme-refine` |
| One section, one file, one loop | Build a new section → `fluid-theme-clone` |

## ⚠️ Never publish

Refining touches sections in themes people are already using.

- **Uploading is safe; publishing is not.** `PUT /api/application_themes/{id}/resources` saves. `POST /api/application_themes/{id}/publish` swaps the live storefront. Never call the second one on your own. In the CLI: `fluid theme push` saves, `fluid theme push --publish` goes live.
- **Check whether the target theme is live before the first write.** If it is, say so and offer `POST /api/application_themes/{id}/clone_for_development` first.
- **"Looks good" is not approval to publish.** Only "publish it" / "make it live" / "go live" is.
- End by handing over a preview URL. See [theme-upload-api.md](../fluid-theme-clone/references/theme-upload-api.md#publishing--explicit-approval-only).

---

## Two ways to run this

The rubric only needs **one file** — the schema-reference page. The audit needs **one more** — the section you're fixing. That means this skill does not require a full theme checkout.

| | **Surgical** (API) | **Local** (checkout) |
|---|---|---|
| Setup | `GET` two resources | `fluid theme pull` |
| Rubric | ✅ full — `rubric.py` runs on the fetched page | ✅ full |
| Schema validation | manual (see below) | ✅ `fluid theme lint --json` |
| Live preview | preview URL after `PUT` | ✅ `fluid theme dev` hot reload |
| Best for | a known fix in one section | exploring, several sections, anything visual |

**Default to surgical when you can name the section and the change.** Pull the theme when you need the real validator, a hot-reload preview, or you'd be iterating.

### Surgical flow

**1. Fetch the two files you need.** List resources, then pull the reference page and your target section:

```bash
curl -s "${FLUID_URL}/api/application_themes/${THEME_ID}/resources" \
  -H "Authorization: Bearer ${FLUID_TOKEN}"
```

Save `sections/schema_reference/index.liquid` and `sections/<target>/index.liquid` to a scratch directory. Note which theme is serving the storefront while you're here — see [Never publish](#-never-publish).

**2. Run Steps 0–3 below against the saved files.** Both scripts take explicit paths, so they work unchanged:

```bash
python3 scripts/lint_reference_page.py <scratch>/schema_reference.liquid
python3 scripts/rubric.py --page <scratch>/schema_reference.liquid --for-section <scratch>/target_section.liquid
```

**3. Validate by hand** — you don't have `fluid theme lint --json`, which needs a whole theme on disk:

- Extract the `{% schema %}` block and confirm it is **valid JSON**
- Check every `type:` against [schema-settings-reference.md](../fluid-theme-clone/references/schema-settings-reference.md) — `paragraph` is the classic reject
- Confirm every `{{ section.settings.X }}` / `{{ block.settings.X }}` read has a matching `id` in that file's schema — Liquid renders unknown refs as empty, so typos ship silently
- Count tag pairs: `if`/`endif`, `for`/`endfor`, `case`/`endcase` must balance

**4. Write the one file back.** `PUT` replaces the whole resource — there is no patch, so send the complete file:

```bash
curl -s -X PUT "${FLUID_URL}/api/application_themes/${THEME_ID}/resources" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ "key": "sections/<target>/index.liquid", "content": "<full file>" }'
```

**5. Hand over a preview URL.** Uploaded is not published. See [theme-editing.md](../fluid-admin/references/theme-editing.md) for the URL patterns and the full API loop.

### Escalate to local when

- The section needs more than a known, nameable fix
- Anything visual is in scope
- You're touching more than ~3 files
- You want the real validator rather than eyeball checks

---

## Step 0 — Validate the rubric before you trust it

**Do this first, every time.** The reference page is about to drive every change you
make. If it teaches something invalid, you will propagate that at speed.

```bash
python3 skills/fluid-section-refine/scripts/lint_reference_page.py
```

This lints the *snippets the page hands developers* — something `fluid theme lint`
never looks at, because they are string fields, not schema.

This is not hypothetical. The page taught `{ "type": "paragraph", … }` in its
Divider Block recipe; developers copied it into five sections; all six schemas
failed validation. One run of this check would have caught it at the source.

If it reports findings: **stop and fix the page first**, then continue. Refining
sections against a broken rubric multiplies the error.

> No `sections/schema_reference/index.liquid` in this theme? Then it has no
> rubric. Fall back to
> [schema-settings-reference.md](../fluid-theme-clone/references/schema-settings-reference.md),
> [css-js-patterns.md](../fluid-theme-clone/references/css-js-patterns.md), and
> [media-tag.md](../fluid-theme-clone/references/media-tag.md), and offer to copy the
> page in from the base theme — it is the single highest-value thing a theme can carry.

## Step 1 — Pull the rubric for this section

The page is ~175 KB. Never load it whole. Extract only what applies:

```bash
python3 skills/fluid-section-refine/scripts/rubric.py --for-section sections/hero_section/index.liquid
```

It reads the section's schema, finds every setting type and block type it declares,
and returns the matching cards plus the always-applicable patterns (Section Shell,
CSS placement, media rendering, canonical block primacy). Typically 10–15 of 79 cards.

Other modes when you need them:

```bash
rubric.py --list                     # compact index of all cards
rubric.py --card pattern-media-tag   # one card in full
rubric.py --category patterns        # every recipe
```

Add `--json` for structured output.

## Step 2 — Audit against the rubric

Read the section, then walk the extracted cards. For each one, ask: **does this
section do what the card says?**

The cards carry the specifics; these are the checks that apply to every section
regardless of what the rubric returns:

**Schema**
- [ ] Every setting `type:` is canonical — `fluid theme lint --json` rejects anything else. `paragraph` is the classic trap; use `header`.
- [ ] Every setting has a unique non-empty `id`, except `header` which carries `content:` and no id
- [ ] `range` has `min`/`max`/`step`; `select`/`radio` has `options`; `*_list` has `limit`; `checkbox` has `default`
- [ ] Section files use `"blocks": []` (array). Page templates use `{}` (object)
- [ ] No two singular resource pickers in the same role — collapse to a `*_list`
- [ ] No `X_1` / `X_2` / `X_3` parallel settings — those want to be blocks

**Content model**
- [ ] Content (headings, text, images, CTAs, cards) is modeled as **blocks**, not fixed section settings — even when there is only one today
- [ ] Section settings hold only whole-section config: width, background, padding, columns, alignment
- [ ] Canonical blocks ship their **full** setting list — never an abbreviated button or image block

**Editor**
- [ ] `{{ section.fluid_attributes }}` on the section's root element
- [ ] `{{ block.fluid_attributes }}` on each block's root inside `{% for block in section.blocks %}`
- [ ] No typos (`fluid_attribute`, `fluid_attr`, `fluidAttributes`) and no hand-rolled `data-fluid-section-*`
- [ ] Passing through a component? Forward as `attr: block.fluid_attributes`

**Assets and media**
- [ ] No co-located `styles.css` — CSS lives in `assets/`, referenced from the top of `index.liquid`
- [ ] Images and video render through `| media_tag`, not hand-rolled `<img>` / `<video>`
- [ ] Above-the-fold media passes `loading: 'eager'`
- [ ] `*_picker` images pass an explicit `alt:` (or `alt: ''` when decorative)
- [ ] Inline `<style>` is setting-driven only and under ~10 lines; `<script>` under ~5; `<script src>` has `defer`

**Liquid**
- [ ] Every `section.settings.*` / `block.settings.*` read has a matching `id` in this file's schema
- [ ] `block` only referenced inside its loop; loop vars not used after `{% endfor %}`
- [ ] Balanced `if`/`for`/`case`/`capture` tags; whitespace control (`{%-` `-%}`) in markup loops
- [ ] Unguarded resource chains (`settings.product.first_variant.price`) are nil-safe
- [ ] User strings escaped, except `richtext` / `html` / `html_textarea` which render raw

## Step 3 — Fix, one change at a time

Severity order, highest first:

| Tag | Meaning |
|---|---|
| `blocker` | The validator rejects it, or it renders wrong / breaks the editor / exposes user data |
| `should` | Works today, hurts later — perf, DRY, missing default, drifts from the documented pattern |
| `nit` | Cosmetic. Mention once, don't block |

Rules:

- **Quote the card you are refining against.** Every fix cites a rubric anchor: "per `[pattern-media-tag]`…". If no card covers it, say the check came from this skill's baseline list instead. Never present a personal preference as the theme's standard.
- **One focused change at a time.** Don't bundle a behavioral fix with formatting.
- **Don't restyle.** Pure formatting churn is out of scope.
- **Don't rewrite a section the user didn't ask you to rewrite.** Propose first.

## Step 4 — Validate until clean

**Local mode:**

```bash
fluid theme lint --json
```

Parse the JSON — don't eyeball it. Fix what it flags, run again, repeat until that
file is clean. Then re-read the section to confirm the change landed as intended.

**Surgical mode:** the linter needs a whole theme on disk, so run the four manual
checks from [Surgical flow step 3](#surgical-flow) instead — schema parses as JSON,
every `type:` is canonical, every settings read has a declared `id`, tag pairs
balance. Do them before the `PUT`, not after.

Either way, a clean validation is necessary but **not sufficient**: it covers schema
JSON only. It says nothing about whether blocks are editable, media is responsive, or
the section follows the documented pattern. That is what Step 2 is for.

## Step 5 — Feed what you learned back into the page

**This is the step that keeps the rubric from rotting**, and the reason the page
drifted out of date in the first place.

While refining, watch for two things:

1. **The section does something better than the documented pattern.** A cleaner
   block contract, a fallback chain the card doesn't cover, a genuinely nicer
   approach. Propose promoting it into the reference page as a new card, or as an
   edit to an existing one.
2. **The rubric has a hole.** You needed a rule the page doesn't state, and you
   filled it from this skill's baseline list. That gap belongs on the page.

Don't edit the reference page silently — it is the shared standard, and changing
it changes how every future section gets refined. Surface the proposal, show the
card you'd add, and let the user decide.

When a card *is* updated, re-run Step 0 before continuing.

## Working loop

For a single section:

```
0. lint_reference_page.py          → rubric is trustworthy
1. rubric.py --for-section <path>  → 10–15 relevant cards
2. audit against those cards + the baseline checks
3. fix, highest severity first, one change at a time
4. validate → local: fluid theme lint --json | surgical: the 4 manual checks
5. note anything worth promoting back to the page
```

Surgical mode adds a fetch before step 0 and a `PUT` + preview URL after step 4;
steps 0–3 are identical, just pointed at the saved files.

For several sections, finish one completely before starting the next, and pause
between them to ask whether to continue, skip, or stop. Don't sweep a whole theme
silently — that is `fluid-theme-refine`'s job, and it asks different questions.

## Reference

- [schema-settings-reference.md](../fluid-theme-clone/references/schema-settings-reference.md) — canonical setting types, common mistakes, singular→list heuristic
- [css-js-patterns.md](../fluid-theme-clone/references/css-js-patterns.md) — the assets-only CSS contract
- [media-tag.md](../fluid-theme-clone/references/media-tag.md) — responsive media rendering
- [fluid-cli.md](../fluid-theme-clone/references/fluid-cli.md) — `lint`, `dev`, push/pull
- [theme-upload-api.md](../fluid-theme-clone/references/theme-upload-api.md) — resource upload, publishing rules, preview URLs

The platform team's bundled `themes-review` skill (`fluid theme skills install`)
covers the same ground from the reviewer's side and is authoritative where it
disagrees with anything here. If you hit a conflict, follow it and flag it.
