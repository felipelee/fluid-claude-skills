# Surgical theme edits via the API

`fluid-admin` can read and write individual theme files. That makes it the right tool for a
targeted change — fix one setting type, swap one image reference, correct one block — without
pulling the whole theme, starting a dev server, and running a screenshot diff.

The tradeoff is that you lose the local toolchain: no `fluid theme lint --json`, no rubric
extraction, no hot-reload preview. This page covers how to do surgical edits **correctly**
anyway, and when to stop and escalate.

## Contents

- Is a surgical edit the right call?
- ⚠️ Never publish
- The read → edit → write loop
- Conventions that actually break things
- Validating without a local checkout
- When to escalate

---

## Is a surgical edit the right call?

| Surgical (this skill) | Pull the theme (`fluid-section-refine` / `fluid-theme-refine`) |
|---|---|
| One or two files, change is known | You need to find what's wrong |
| Fix an invalid setting type | Refine a section against the full standard |
| Swap a hardcoded URL for a setting | Anything visual — spacing, color, layout parity |
| Add a missing `alt` / `fluid_attributes` | Restructure content into blocks |
| Correct a typo'd `id` | More than ~3 files, or you'd be iterating |

**The test:** can you name the file and the exact edit before you start? If yes, surgical. If
you'd be exploring, pull the theme — you'll want the linter and the preview.

## ⚠️ Never publish

Writing theme resources is safe and reversible. Publishing is neither.

- `PUT /api/application_themes/{id}/resources` — **saves a file.** Does not publish.
- `POST /api/application_themes/{id}/publish` — **swaps the live storefront.** Never call this
  on your own.

Rules:

1. **Check whether the theme you're editing is the live one before the first write.** If it is,
   say so and let the user decide. Offer `POST /api/application_themes/{id}/clone_for_development`
   — an isolated unpublished copy that preserves content and DAM references.
2. **Create new themes as `status: "draft"`**, never `"active"`. `"active"` puts it on the storefront.
3. **Publishing needs an unambiguous instruction** — "publish it", "make it live", "go live".
   "Looks good" / "ship it" / "that's the one" are approval of the *work*, not of going live.
4. **If you do publish, say plainly that the live storefront changed.**

Full detail: [theme-upload-api.md](../../fluid-theme-clone/references/theme-upload-api.md#publishing--explicit-approval-only).

## The read → edit → write loop

### 1. Find the theme

```bash
curl -s "${FLUID_URL}/api/application_themes" \
  -H "Authorization: Bearer ${FLUID_TOKEN}"
```

Note which one is serving the storefront before you touch anything.

### 2. List its resources

```bash
curl -s "${FLUID_URL}/api/application_themes/${THEME_ID}/resources" \
  -H "Authorization: Bearer ${FLUID_TOKEN}"
```

Resources are keyed by their path in the theme — `sections/hero/index.liquid`,
`assets/global.css`, `config/settings_schema.json`. Inspect the payload shape before assuming
where content lives; text resources carry their content, binaries carry a DAM/ImageKit URL.

### 3. Read the one file you're changing

**Always read before you write.** `PUT` replaces the whole resource — there is no patch. Editing
blind overwrites whatever else is in that file.

### 4. Write it back

```bash
curl -s -X PUT "${FLUID_URL}/api/application_themes/${THEME_ID}/resources" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "sections/hero/index.liquid",
    "content": "<full file contents>"
  }'
```

`PUT` is idempotent — same key twice overwrites. The `key` is the full path from the theme root.

### 5. Preview

Uploaded is not published. Give the user a preview so they can see it:

```
https://admin.fluid.app/templates/{template_id}?editor=visual&themeable_type={type}&from=themes
https://{company}.fluid.app/{path}?preview=true&theme_template_id={template_id}&version={n}
```

`version={n}` is a real Fluid parameter pinning the saved template version — bump it as you
push. For the editor iframe, which caches hard and has no `version`, append a throwaway
`&cb={unique}` that changes every navigation.

## Conventions that actually break things

You're editing one file without the linter. These are the rules that cause a hard failure or a
silent breakage — check them by eye before you `PUT`.

**Setting types — the validator rejects anything off-list.** A bad `type:` fails
`fluid theme push` and the editor's own validation.

- `paragraph` is **not valid in Fluid** even though it works in Shopify. Use `header` — same
  `content:` field, no `id`.
- `text_area` is not a type. It's `textarea`, one word.
- `range` needs `min`/`max`/`step`. `select`/`radio` need `options`. `*_list` needs `limit`.
  `checkbox` needs `default`.
- Every setting needs a unique non-empty `id` — except `header`, which has `content:` and no id.
- Block `settings` must be an array `[]`, never an object `{}`.
- Section files use `"blocks": []`. Page templates use `"blocks": {}`.

Full list: [schema-settings-reference.md](../../fluid-theme-clone/references/schema-settings-reference.md).

**CSS lives in `assets/` — nowhere else.** A co-located `sections/{name}/styles.css` is the
deprecated shape and returns **422** once the company has `STYLESHEET_STRICT_INPUT` enabled.
Theme-level `styles.css` / `global_styles.css` belong in `assets/` under those *exact*
filenames, referenced from `layouts/theme.liquid` via `| inline_asset_content` — renaming them
breaks the FileResource lookup.
See [css-js-patterns.md](../../fluid-theme-clone/references/css-js-patterns.md).

**Images and video go through `| media_tag`.** A hand-rolled `<img>` ships one fixed-size
original with no `srcset` and no format negotiation. Pass `alt:` explicitly for `*_picker`
settings (they carry no stored alt), and `loading: 'eager'` above the fold.
See [media-tag.md](../../fluid-theme-clone/references/media-tag.md).

**`fluid_attributes` or the editor goes dead.** `{{ section.fluid_attributes }}` on the
section's root element, `{{ block.fluid_attributes }}` on each block's root inside the loop.
These render empty in production, so a missing one is invisible on the storefront and only
breaks click-to-edit in the editor — which means nobody notices until a merchant complains.

**Content belongs in blocks, not section settings.** Anything a merchant might add, remove, or
reorder — headings, images, CTAs, cards — should be a block. Section settings are for
whole-section config: width, background, padding, columns.

**Don't hand-edit `config/settings_data.json`.** It's compiled preset state.

## Validating without a local checkout

You don't have `fluid theme lint --json`, so validate what you can before writing:

1. **Parse the schema.** Extract the `{% schema %}` block and confirm it is valid JSON. A syntax
   error there breaks the section outright.
2. **Check every `type:`** against the canonical list in
   [schema-settings-reference.md](../../fluid-theme-clone/references/schema-settings-reference.md).
3. **Check every `{{ section.settings.X }}` / `{{ block.settings.X }}`** read has a matching `id`
   declared in that same file's schema. Liquid renders unknown references as empty — a typo
   ships silently.
4. **Count your tags.** `{% if %}`/`{% endif %}`, `for`/`endfor`, `case`/`endcase` must balance;
   Liquid's parser is permissive and an unclosed tag swallows the rest of the template.

If the theme's `sections/schema_reference/index.liquid` exists, you can fetch just that one
resource and run the rubric extractor on it locally — it only needs the file, not a full
checkout:

```bash
python3 skills/fluid-section-refine/scripts/rubric.py --page <saved_file> --list
```

## When to escalate

Stop doing surgery and pull the theme when:

- The change touches more than about three files
- You need to *find* the problem rather than fix a known one
- Anything visual is in scope — you need the `fluid theme dev` preview and screenshot diff
- You want the real validator, not eyeball checks
- You're restructuring content into blocks

Then hand off:

- [`fluid-section-refine`](../../fluid-section-refine/SKILL.md) — one section against the theme's
  own style guide
- [`fluid-theme-refine`](../../fluid-theme-refine/SKILL.md) — whole-theme structural and visual work
