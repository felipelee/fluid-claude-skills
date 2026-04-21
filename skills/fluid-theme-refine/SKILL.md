---
name: fluid-theme-refine
description: >-
  Refine and improve a Fluid theme to achieve pixel-perfect 1:1 match with
  the source site. Use after fluid-theme-clone to tighten up visual fidelity.
  Triggers on "refine theme," "improve theme," "make it closer," "pixel perfect,"
  "doesn't match," "fix the spacing," "colors are off," "fonts don't match,"
  "compare and fix," "tighten up," "QA the theme," "visual diff," "side by side
  comparison," "it doesn't look right," "make it exact," or "closer to the original."
metadata:
  version: 1.4.0
---

# Fluid Theme Refine

You are an expert Fluid theme developer doing a pixel-perfect QA pass. Your job is to take an already-cloned Fluid theme, compare it against the original source site screenshot-by-screenshot, identify every visual discrepancy, fix them, and repeat until the two are indistinguishable.

This skill is the polish step after `/fluid-theme-clone`. The clone gets you 80-90% there. This gets you to 99%.

## How This Works

```
┌─────────────────────────────────────────────────────────┐
│                  REFINEMENT LOOP                         │
│                                                          │
│  ┌──────────┐    ┌──────────┐                           │
│  │ SOURCE   │    │ BUILT    │                           │
│  │ (live    │    │ (Fluid   │                           │
│  │  site)   │    │  theme)  │                           │
│  └────┬─────┘    └────┬─────┘                           │
│       │               │                                  │
│       ▼               ▼                                  │
│  ┌─────────────────────────┐                            │
│  │  SCREENSHOT BOTH PAGES  │                            │
│  │  at same viewport width │                            │
│  │  scroll to same section │                            │
│  └───────────┬─────────────┘                            │
│              ▼                                           │
│  ┌─────────────────────────┐                            │
│  │  COMPARE SIDE BY SIDE   │                            │
│  │  List EVERY difference: │                            │
│  │  - colors               │                            │
│  │  - spacing/padding      │                            │
│  │  - font size/weight     │                            │
│  │  - border radius        │                            │
│  │  - layout/alignment     │                            │
│  │  - missing content      │                            │
│  │  - animations           │                            │
│  └───────────┬─────────────┘                            │
│              ▼                                           │
│  ┌─────────────────────────┐     ┌──────────┐          │
│  │  ANY DIFFERENCES?       │────▶│   DONE   │          │
│  │  NO                     │     │  Report  │          │
│  └───────────┬─────────────┘     └──────────┘          │
│         YES  │                                          │
│              ▼                                           │
│  ┌─────────────────────────┐                            │
│  │  EXTRACT EXACT VALUES   │                            │
│  │  from source via JS     │                            │
│  │  getComputedStyle(el)   │                            │
│  └───────────┬─────────────┘                            │
│              ▼                                           │
│  ┌─────────────────────────┐                            │
│  │  FIX THE CSS/HTML       │                            │
│  │  Update section file    │                            │
│  └───────────┬─────────────┘                            │
│              ▼                                           │
│  ┌─────────────────────────┐                            │
│  │  UPLOAD FIXED FILE      │                            │
│  │  to Fluid theme API     │                            │
│  └───────────┬─────────────┘                            │
│              ▼                                           │
│       (loop back to screenshot)                          │
└─────────────────────────────────────────────────────────┘
```

Every round: screenshot → compare → list diffs → extract values → fix → upload → screenshot again. Repeat until no differences remain.

---

## Step 1: Collect Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `SOURCE_URL` | Yes | The original page to match (e.g. `https://yellowbirdfoods.com`) |
| `FLUID_URL` | Yes | The Fluid store URL (e.g. `https://companyname.fluid.app`) |
| `FLUID_TOKEN` | Yes | Fluid API token |
| `THEME_ID` | Yes* | The application theme ID to update. If not provided, fetch via `GET /api/application_themes` and ask the user to confirm which one. |
| `THEME_DIR` | No | Local working directory with theme files. If not provided, work directly against the Fluid API. |

Also ask:
- **Which page?** Homepage, a specific page, or "all pages"?
- **Which breakpoints?** Desktop only, or also tablet/mobile?
- **Specific sections?** Or full page sweep?

---

## Step 2: Validate and Set Up

```python
# 1. Source site reachable
requests.get(source_url, timeout=10)

# 2. Fluid API works
resp = requests.get(f"{fluid_url}/api/application_themes",
                    headers={"Authorization": f"Bearer {fluid_token}"})
# Find the theme, confirm theme_id

# 3. Fluid store page is reachable
requests.get(f"{fluid_url}", timeout=10)
```

Print:
```
[Refine] Source: OK yellowbirdfoods.com
[Refine] Fluid:  OK companyname.fluid.app (Theme ID: 55697)
```

**CRITICAL: Confirm company identity before proceeding.** Also call `GET /api/settings/company` and display the company name to the user. This prevents accidentally overwriting theme files on the wrong Fluid account.

```
⚠️  This token resolves to: "Yellowbird Foods" (Company ID: 980243068)
    Store URL: https://companyname.fluid.app
    Theme: "Yellowbird Theme" (ID: 55697)

Is this the correct store and theme? (yes/no)
```

**Do NOT proceed until the user confirms.**

```
[Refine] Starting refinement pass.
```

---

## Step 3: Screenshot Both Pages

Open two browser tabs — one for the source, one for the Fluid store.

### 3a: Set up both tabs

```
Tab 1: SOURCE_URL (the original site)
Tab 2: FLUID_URL (the Fluid store with the cloned theme)
```

### 3b: Remove overlays on both

```javascript
// Run on both tabs
document.querySelectorAll('[data-acsb-custom-trigger],.acsb-trigger,.acsb-widget,.acsb-overlay,.popup,.modal,[class*="cookie"],[class*="banner"]').forEach(e => e.remove());
```

### 3c: Set same viewport width

Both pages must be at the same width for comparison. Start with desktop (1280px).

### 3d: Screenshot each section pair

Scroll both pages to the same section. Take a screenshot of each.

**Label every screenshot pair:**
```
Section 1: Hero
  - source_hero_desktop.png
  - built_hero_desktop.png

Section 2: Features Grid
  - source_features_desktop.png
  - built_features_desktop.png
```

---

## Step 4: Detailed Comparison

For each section pair, create a **diff report**. Be exhaustive — catch everything:

```
SECTION: Hero
STATUS: 3 differences found

1. BACKGROUND COLOR
   Source: #1B3A4B
   Built:  #1C3B4C
   Fix:    Update .eh-hero background-color

2. HEADING FONT SIZE (mobile)
   Source: 32px
   Built:  28px
   Fix:    Update @media (max-width: 767px) .eh-hero__heading font-size

3. BUTTON BORDER RADIUS
   Source: 24px (fully rounded)
   Built:  8px
   Fix:    Update .eh-hero__cta border-radius

---

SECTION: Features Grid
STATUS: Match ✓

---

SECTION: Testimonials
STATUS: 2 differences found

1. CARD SHADOW
   Source: 0 4px 12px rgba(0,0,0,0.08)
   Built:  none
   Fix:    Add box-shadow to .eh-testimonials__card

2. GAP BETWEEN CARDS
   Source: 32px
   Built:  24px
   Fix:    Update .eh-testimonials__grid gap
```

### What to Compare (Checklist)

For EVERY section, check all of these:

**Layout**
- [ ] Same column count and arrangement
- [ ] Same max-width / container width
- [ ] Same alignment (left, center, right)
- [ ] Same content order

**Colors**
- [ ] Background color (section level)
- [ ] Background color (card/element level)
- [ ] Heading text color
- [ ] Body text color
- [ ] Button background and text color
- [ ] Border colors
- [ ] Hover state colors

**Typography**
- [ ] Font family
- [ ] Font size (heading, subheading, body, caption)
- [ ] Font weight
- [ ] Line height
- [ ] Letter spacing
- [ ] Text transform (uppercase, capitalize)

**Spacing**
- [ ] Section padding (top and bottom)
- [ ] Element margins
- [ ] Grid/flex gap
- [ ] Content padding inside cards

**Borders & Shapes**
- [ ] Border radius on cards, buttons, images
- [ ] Border width and style
- [ ] Box shadow

**Images**
- [ ] Correct image displayed
- [ ] Same aspect ratio / object-fit
- [ ] Same size
- [ ] Same border radius

**Interactive**
- [ ] Hover effects match
- [ ] Scroll animations match (timing, easing, direction)
- [ ] Carousel behavior matches
- [ ] Accordion behavior matches

---

## Step 5: Extract Exact Values from Source

For every difference found, go to the source site and extract the exact computed value:

```javascript
// Target the specific element
var el = document.querySelector('.hero-section h1');
var s = getComputedStyle(el);

// Extract everything relevant
JSON.stringify({
  color: s.color,
  fontSize: s.fontSize,
  fontWeight: s.fontWeight,
  fontFamily: s.fontFamily,
  lineHeight: s.lineHeight,
  letterSpacing: s.letterSpacing,
  textTransform: s.textTransform,
  margin: s.margin,
  padding: s.padding
}, null, 2);
```

For backgrounds and containers:
```javascript
var el = document.querySelector('.hero-section');
var s = getComputedStyle(el);

JSON.stringify({
  backgroundColor: s.backgroundColor,
  padding: s.padding,
  maxWidth: s.maxWidth,
  borderRadius: s.borderRadius,
  boxShadow: s.boxShadow,
  gap: s.gap
}, null, 2);
```

**Convert `rgb()` values to hex** for cleaner CSS:
```javascript
function rgbToHex(rgb) {
  var m = rgb.match(/\d+/g);
  return '#' + m.slice(0,3).map(x => parseInt(x).toString(16).padStart(2,'0')).join('');
}
```

---

## Step 6: Fix the Section Files

Update the section's `index.liquid` file with the corrected values. Be surgical — only change what's wrong.

**Common fixes:**
- Color off by a shade → update hex value in `<style>` block
- Spacing wrong → update padding/margin/gap values
- Font size wrong at a breakpoint → update the `@media` query
- Missing box-shadow → add the property
- Border radius wrong → update the value
- Missing hover effect → add `:hover` rule
- Animation timing off → adjust `transition-duration` or `transition-delay`

### After fixing, read the file back to verify the change is correct.

---

## Step 7: Upload Fixed Files to Fluid

Push the updated section to the Fluid theme:

```python
with open(filepath, 'r') as f:
    content = f.read()

requests.put(
    f"{fluid_url}/api/application_themes/{theme_id}/resources",
    headers={
        "Authorization": f"Bearer {fluid_token}",
        "Content-Type": "application/json"
    },
    json={"key": key, "content": content}
)
```

The `key` is the path relative to the theme root (e.g. `sections/exact-yb-hero/index.liquid`).

---

## Step 8: Re-Screenshot and Verify

After uploading fixes:

1. **Hard refresh** the Fluid store page (Cmd+Shift+R) to clear cache
2. **Screenshot the fixed section** at the same viewport width
3. **Compare against source again**
4. If still different → go back to Step 5
5. If matching → move to next section

---

## Step 9: Responsive Pass

After desktop matches, repeat the full comparison at:

| Viewport | Width |
|----------|-------|
| Tablet | 768px |
| Mobile | 375px |

At each breakpoint:
1. Resize both source and built pages to the same width
2. Screenshot each section pair
3. Compare, fix, upload, verify

Common responsive issues:
- Grid columns don't collapse at the right breakpoint
- Font sizes don't scale down enough
- Padding is too large on mobile
- Images don't resize properly
- Hamburger menu behavior differs

---

## Step 10: Final Report

After all sections match at all breakpoints, print a summary:

```
=== REFINEMENT COMPLETE ===

Page: https://yellowbirdfoods.com (Homepage)
Theme: companyname.fluid.app (Theme ID: 55697)

ROUNDS: 3
SECTIONS REFINED: 7 of 9 (2 already matched)
TOTAL FIXES: 14

Fixes by type:
  Colors:     4 (background, text, button)
  Spacing:    3 (padding, gap)
  Typography: 3 (font-size, weight, line-height)
  Borders:    2 (border-radius, box-shadow)
  Layout:     1 (grid columns at tablet)
  Animation:  1 (scroll fade-in timing)

Breakpoints verified:
  Desktop (1280px): ✓ Match
  Tablet (768px):   ✓ Match
  Mobile (375px):   ✓ Match

All sections now match the source site.
```

---

## When to Stop

- **All sections match at all 3 breakpoints** → done
- **After 5 rounds on the same section** with no progress → note the remaining deviations (likely custom fonts, dynamic content, or third-party widgets) and move on
- **Differences are in dynamic content** (live prices, counters, user-generated content) → not fixable, note and skip
- **Custom fonts not available** → use the closest match, document the substitution

---

## Running on Specific Sections

If the user says "fix the hero section" or "the testimonials don't match," skip the full-page sweep and jump directly to that section:

1. Screenshot just that section on both source and built
2. Run the comparison checklist
3. Extract values, fix, upload, verify
4. Done

---

## Running on All Pages

If refining a full site clone, work through pages in this order:
1. Homepage (establishes the design language)
2. Product pages
3. Collection/shop pages
4. Static pages (about, FAQ, etc.)

Between pages, check if fixes to shared sections (nav, footer, CTA banners) propagate correctly.

---

## Fluid Engine Quirks — Discovered Field Knowledge

These are non-obvious behaviors discovered while refining themes. If you hit any of these symptoms, the fix is probably here.

### Headings render at body-text size (no visual hierarchy)

**Symptom:** Heading blocks look the same size as body text. All typography feels flat.

**Root causes (check in order):**

1. **CSS file with h1-h6 rules isn't being loaded.** Fluid does NOT auto-load CSS files at the theme root — only files in `assets/` are served via `| asset_url`. If there's a `global_styles.css` at the theme root, it's dead code.
   - **Fix:** Move it to `assets/global.css` and add `<link rel="stylesheet" href="{{ 'global.css' | asset_url }}">` in `layouts/theme.liquid` after `reset.css` / `config.css` / `utilities.css`.
   - Verify: the CSS variables `--fs-h1` … `--fs-h6` are defined in theme.liquid's `:root`, and h1-h6 selectors point at them.

2. **Richtext block defaults use `<p>` instead of `<h1>`–`<h6>`.** A richtext default of `<p>Medium length hero headline</p>` renders as body text because there's no heading tag for h1-h6 CSS to apply to.
   - **Fix:** Update the default in the block's schema:
     ```json
     "default": "<h1 style=\"color: var(--clr-primary);\">Medium length hero headline</h1>"
     ```
   - Include inline `color: var(--clr-primary);` so the heading picks up the theme color by default.
   - Map heading levels to block semantic purpose: hero heading → `h1`, section heading → `h2`, subsection → `h3`, card title → `h4`, eyebrow → `h5`.
   - **Caveat:** Schema `default` values only apply to **newly-added blocks**. Sections already on a page keep their previously-saved HTML. To update saved blocks, edit them manually in the editor OR patch the template's saved state via the API.

### "Primary Color" and "Text Presets" dropdowns in the editor are empty

The formatting toolbar on every `text` / `textarea` / `richtext` field has two dropdowns at the top: **Text Presets** and **Primary Color**. These draw from theme-level `option_group`s in `config/settings_schema.json`.

**Fix — colors:** every color setting needs an `option_group` with a distinct `label` and a `value` that's a CSS value:
```json
{
  "type": "color_background",
  "id": "color_primary",
  "label": "Primary Color",
  "default": "#023026",
  "option_group": { "id": "background_colors", "label": "Primary", "value": "var(--clr-primary)" }
},
{
  "type": "color_background",
  "id": "color_secondary",
  "label": "Secondary Color",
  "default": "#666",
  "option_group": { "id": "background_colors", "label": "Secondary", "value": "var(--clr-secondary)" }
}
```

**Fix — text presets:** every heading font-size range needs an `option_group` pointing at `text_presets`:
```json
{
  "type": "range", "id": "font_size_h1", "label": "H1 Font Size",
  "min": 32, "max": 72, "step": 1, "default": 42,
  "option_group": { "id": "text_presets", "label": "H1 · Heading", "value": "text-h1" }
}
```

Without these option_groups, the dropdowns render empty and editors have nothing to pick.

### Section `select` with `"options": "background_colors"` is empty

Same root cause as above. The `select + option_group` pattern is how Fluid gets a theme-aware color dropdown inside a section. If the dropdown is empty, the theme has no colors with `option_group: { id: "background_colors", ... }`.

**Critical bug to avoid:** never write `background-color: var(--clr-{{ section.settings.background_color }});`. When the setting is empty this renders `var(--clr-)` — invalid CSS that silently breaks the entire rule block. The option_group's `value` is already a CSS value, so:
```liquid
background-color: {{ section.settings.background_color | default: 'transparent' }};
```

### Section preset blocks don't populate on an existing template

**Symptom:** You define a section with 40 preset blocks. You push the theme. The section renders in the editor but has ZERO blocks — the preset didn't apply.

**Root cause:** Fluid only applies section presets when a section is **first added** to a template. An existing template that already has the section (even with zero blocks) never retroactively gets the preset. API `PUT` on resources doesn't trigger preset expansion.

**Fix:** delete the template via API, then re-push the page template. That forces Fluid to create a fresh template record, and fresh-creation runs preset expansion.
```python
# 1. Delete the resource (this deletes the template record)
requests.delete(f"{FLUID_URL}/api/application_themes/{THEME_ID}/resources",
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    json={"key": "page/<slug>/index.liquid"})

# 2. Re-push the page template content
with open(local_path) as f: content = f.read()
requests.put(f"{FLUID_URL}/api/application_themes/{THEME_ID}/resources",
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    json={"key": "page/<slug>/index.liquid", "content": content})
# A new template ID is created. Find it via GET /api/application_themes/{THEME_ID}.
```

**Additional requirement for preset expansion to fire:** the section's `"blocks"` array in its schema must declare blocks with **inline settings**, not as a standalone reference:
```json
/* WRONG — Fluid won't run preset expansion on this shape */
"blocks": [
  { "type": "schema_entry" }
]

/* RIGHT — inline settings, matches main_navbar convention */
"blocks": [
  {
    "type": "schema_entry",
    "name": "Schema Entry",
    "settings": [
      { "type": "text", "id": "control_name", "label": "Control Name" },
      { "type": "richtext", "id": "description", "label": "Description" }
    ]
  }
]
```

Note: even if you have a standalone `blocks/schema_entry/index.liquid` file with its own schema, the section still needs the inline copy for preset expansion to work. Keep the block file for markup reuse OR delete it if you're rendering blocks inline in the section.

### Blocks render in HTML but aren't clickable in the editor

**Symptom:** Blocks appear on the canvas, but clicking them doesn't open settings. The Layers panel doesn't list them.

**Diagnosis:** inspect any block element. If its HTML is missing `data-fluid-section-block-id`, `data-fluid-section-block-type`, and `data-fluid-block-attribute`, the block isn't registered with the editor.

```javascript
// In the preview iframe
document.querySelector('.your-block-class').outerHTML.substring(0, 300)
```

A **registered** block has attributes like:
```
data-fluid-section-block-id="02b31fac"
data-fluid-section-block-type="schema_entry"
data-fluid-parent-section-type="your_section"
data-fluid-section-id="5332901"
data-fluid-block-attribute="{...}"
```

**Root cause:** the blocks were injected via inline template schema rather than via the section's preset. `{{ block.fluid_attributes }}` returns empty for pseudo-blocks.

**Fix:** see "Section preset blocks don't populate" above — delete + recreate the template with the inline-blocks pattern in the section's schema.

### `{% render block %}` and `{% include 'block_name' %}` don't emit markup

**Symptom:** You have `blocks/my_block/index.liquid` with markup, and you call `{% render block %}` from a section's for-loop. Nothing renders.

**Root cause:** Fluid doesn't auto-render standalone block templates via `render` or `include`. The convention in Fluid themes is to render block markup **inline in the section** via `case/when`:

```liquid
{% for block in section.blocks %}
  {% case block.type %}
    {% when 'heading' %}
      <div class="heading" {{ block.fluid_attributes }}>{{ block.settings.text }}</div>
    {% when 'button' %}
      <a class="btn" {{ block.fluid_attributes }} href="{{ block.settings.url }}">{{ block.settings.label }}</a>
  {% endcase %}
{% endfor %}
```

The `blocks/<name>/index.liquid` file's `{% schema %}` defines the block's settings (editor UI). Its markup body is ignored in the Fluid section-block rendering path — everything renders inline in the section.

### Block loop whitespace dashes break the editor

Per Fluid's editor requirements — no `{%- -%}` dashes on block-loop tags. Inside the for-loop use plain `{% %}`:

```liquid
{% for block in section.blocks %}
  {% case block.type %}
    {% when 'heading' %}
```

Dashes ARE safe inside `{%- style -%}` blocks (CSS generation), just not inside the block iteration / case-when.

### Section root missing `{{ section.fluid_attributes }}` breaks section selection

**Symptom:** You can't click the section itself in the editor to open its settings.

**Fix:** the outermost element in the section's markup needs `{{ section.fluid_attributes }}`:
```liquid
<section class="my-section section-{{ section.id }}" {{ section.fluid_attributes }}>
  …
</section>
```

Without this, Fluid doesn't know where the section starts/ends in the DOM, so it can't bind selection handles.

### Binary theme assets (images) fail to upload via API

The old `dam_asset: "<https-url-string>"` shape on `PUT /api/application_themes/{id}/resources` now returns 422 ("must be a hash"). Tested shapes that still error:
- `dam_asset: { id }` → 500 RecordInvalid
- `dam_asset: { url }` → 500 RecordInvalid
- `dam_asset: { id, url }` → 500 RecordInvalid
- `dam_asset: { id, default_variant_id, default_variant_url }` → 500 UnknownAttributeError
- Full asset hash → 500 UnknownAttributeError

**Current workaround:** skip binary theme assets in API pushes. Images for sections belong in the DAM and should be referenced from Liquid with their DAM URLs in `settings_data.json` or block defaults, not pushed as theme resources. The 8-10 placeholder images in a base theme (logo, footer-logo, brand-*, placeholder-*) are rarely used — most themes override them via settings.

### Saved block state does NOT update when you change section defaults

Updating a block's `"default"` in the section schema and pushing does not retroactively change blocks that already exist on pages. The saved template state keeps the old content.

To update live content after changing defaults:
- **Quick:** edit each affected block manually in the editor.
- **Bulk:** patch the template's saved JSON directly via API — GET the template content, find the `blocks` object under the section, update the settings there, PUT it back.
- **Nuclear:** delete + recreate the template (see preset-expansion fix above). Loses any editor customizations.

### API push → editor Save workflow

After pushing section code via `PUT /api/application_themes/{id}/resources`:
1. Open the visual editor for a template that uses the section
2. Click **Save** (even with no visible changes)
3. This triggers Fluid's block registration system for any blocks already on the canvas
4. Blocks become clickable in both the Layers panel and the preview

This is different from preset expansion — Save registers blocks that already exist. Preset expansion only happens on fresh template creation.

### Required templates (18)

Fluid expects 18 template folders. Missing any template type prevents that page type from rendering. The full list:

`navbar`, `footer`, `home_page`, `category_page`, `category`, `collection`, `collection_page`, `shop_page`, `product`, `post`, `post_page`, `cart_page`, `page`, `enrollment_pack`, `join_page`, `library`, `library_navbar`, `medium`.

Each lives at `{template}/default/index.liquid`. A commonly missed one is `library_navbar` — it pairs with `library` for media pages and wraps the navbar.

---

## Section Shell Pattern — enforce on every custom section

Every custom (non-Fluid-built-in) section MUST ship with these three groups in its `{% schema %}` settings:

**Section Shell** (outer box):
```json
{ "type": "padding",        "id": "section_padding",       "label": "Section Padding" },
{ "type": "corner_radius",  "id": "section_border_radius", "label": "Section Border Radius" },
{ "type": "select",         "id": "background_color",      "label": "Background Color",
  "options": "background_colors", "default": "transparent" },
{ "type": "image_picker",   "id": "background_image",      "label": "Background Image",
  "info": "Optional. Covers the section background." },
{ "type": "range",          "id": "section_border_width",  "label": "Section Border Width",
  "min": 0, "max": 10, "step": 1, "default": 0, "unit": "px" },
{ "type": "select",         "id": "section_border_color",  "label": "Section Border Color",
  "options": "background_colors", "default": "var(--clr-primary)" }
```

**Container** (inner content frame — 9 settings):
```json
{ "type": "select", "id": "container_max_width", "label": "Max Width", "default": "1280px",
  "options": [
    { "value": "720px",  "label": "Extra narrow (720px)" },
    { "value": "960px",  "label": "Narrow (960px)" },
    { "value": "1080px", "label": "Comfy (1080px)" },
    { "value": "1280px", "label": "Default (1280px)" },
    { "value": "1440px", "label": "Wide (1440px)" },
    { "value": "100%",   "label": "Full (100%)" }
  ]
},
{ "type": "padding",       "id": "container_padding",       "label": "Container Padding" },
{ "type": "corner_radius", "id": "container_border_radius", "label": "Container Border Radius" },
{ "type": "select",        "id": "container_background_color", "label": "Container Background Color",
  "options": "background_colors", "default": "transparent" },
{ "type": "image_picker",  "id": "container_background_image", "label": "Container Background Image" },
{ "type": "select",        "id": "container_overlay_color",    "label": "Container Overlay Color",
  "options": "background_colors", "default": "transparent" },
{ "type": "range",         "id": "container_overlay_opacity",  "label": "Container Overlay Opacity",
  "min": 0, "max": 100, "step": 5, "default": 0, "unit": "%" },
{ "type": "range",         "id": "container_border_width",     "label": "Container Border Width",
  "min": 0, "max": 10, "step": 1, "default": 0, "unit": "px" },
{ "type": "select",        "id": "container_border_color",     "label": "Container Border Color",
  "options": "background_colors", "default": "var(--clr-primary)" }
```

Container is a full design surface, not just a width/padding wrapper. It supports its own background color + image, overlay (color + opacity), border, and corner radius — nested inside the Section Shell. Editors can create a hero with a dark section shell and a rounded container card inside without nesting sections.

CSS wire-up in `{%- style -%}`:

```liquid
{%- style -%}
  /* --- Section Shell --- */
  .my-section.section-{{ section.id }} {
    {%- assign p = section.settings.section_padding -%}
    {%- if p -%}padding: {{ p.top | default: 80 }}px {{ p.right | default: 0 }}px {{ p.bottom | default: 80 }}px {{ p.left | default: 0 }}px;{%- else -%}padding: 80px 0;{%- endif -%}
    {%- assign r = section.settings.section_border_radius -%}
    {%- if r -%}border-radius: {{ r.tl }}px {{ r.tr }}px {{ r.br }}px {{ r.bl }}px;{%- endif -%}
    {% if section.settings.section_border_width > 0 %}border: {{ section.settings.section_border_width }}px solid {{ section.settings.section_border_color }};{% endif %}
    background-color: {{ section.settings.background_color | default: 'transparent' }};
    {%- if section.settings.background_image != blank -%}
      background-image: url({{ section.settings.background_image | img_url: '2400x' }});
      background-size: cover; background-position: center; background-repeat: no-repeat;
    {%- endif -%}
  }

  /* --- Container --- */
  .my-section.section-{{ section.id }} .my-section__container {
    position: relative;
    max-width: {{ section.settings.container_max_width | default: '1280px' }};
    margin: 0 auto;
    {%- assign cp = section.settings.container_padding -%}
    {%- if cp -%}padding: {{ cp.top | default: 0 }}px {{ cp.right | default: 64 }}px {{ cp.bottom | default: 0 }}px {{ cp.left | default: 64 }}px;{%- else -%}padding: 0 64px;{%- endif -%}
    background-color: {{ section.settings.container_background_color | default: 'transparent' }};
    {%- if section.settings.container_background_image != blank -%}
      background-image: url({{ section.settings.container_background_image | img_url: '2400x' }});
      background-size: cover; background-position: center; background-repeat: no-repeat;
    {%- endif -%}
    {%- assign ccr = section.settings.container_border_radius -%}
    {%- if ccr -%}border-radius: {{ ccr.tl }}px {{ ccr.tr }}px {{ ccr.br }}px {{ ccr.bl }}px;{%- endif -%}
    {% if section.settings.container_border_width > 0 %}border: {{ section.settings.container_border_width }}px solid {{ section.settings.container_border_color }};{% endif %}
  }
  {%- if section.settings.container_overlay_color != blank and section.settings.container_overlay_opacity > 0 -%}
    {%- assign _cov = section.settings.container_overlay_opacity | divided_by: 100.0 -%}
    .my-section.section-{{ section.id }} .my-section__container::before { content: ""; position: absolute; inset: 0; background: {{ section.settings.container_overlay_color }}; opacity: {{ _cov }}; pointer-events: none; }
  {%- endif -%}
  .my-section.section-{{ section.id }} .my-section__container > * { position: relative; }
  @media (max-width: 991px) { .my-section.section-{{ section.id }} .my-section__container { padding-left: 24px; padding-right: 24px; } }
  @media (max-width: 767px) { .my-section.section-{{ section.id }} .my-section__container { padding-left: 16px; padding-right: 16px; } }
{%- endstyle -%}

<section class="my-section section-{{ section.id }}" {{ section.fluid_attributes }}>
  <div class="my-section__container">
    …
  </div>
</section>
```

Standardized responsive breakpoints: `991px` (tablet), `767px` (mobile). Never use 749, 768, 1023, or any Shopify-era value.

**Why the split?** `section_padding` controls the outer colored area (vertical spacing between sections, colored background padding). `container_padding` controls inner content spacing (how far from the container edge the text/images sit). Editors often want generous section padding (80px top/bottom) but tighter container padding (24px sides). Two controls, two concerns.

**Why two `border_*` settings instead of `"type": "border"`?** Fluid's native `border` control uses a hex color picker internally, breaking theme-driven color rules. Splitting into `border_width` (range) + `border_color` (select → background_colors) keeps every color theme-aware.

Audit script (run before refinement to flag sections missing the pattern):
```python
import re, json, os
BASE = "base-theme/sections"
SKIP = {"main_product","main_cart","main_bundle_product","main_collection","main_category",
        "main_shop","main_post","main_page","main_enrollment","main_post_list",
        "main_collection_list","main_category_list","main_navbar","main_footer"}

for name in sorted(os.listdir(BASE)):
    if name in SKIP: continue
    with open(f"{BASE}/{name}/index.liquid") as f: c = f.read()
    s = re.sub(r"{%\s*raw\s*%}.*?{%\s*endraw\s*%}", "", c, flags=re.DOTALL)
    m = re.search(r"{%\s*schema\s*%}(.*?){%\s*endschema\s*%}", s, re.DOTALL)
    if not m: continue
    settings = json.loads(m.group(1)).get("settings", [])
    required = {"section_padding", "section_border_radius", "background_color",
                "section_border_width", "section_border_color",
                "container_max_width", "container_padding", "container_border_radius",
                "container_background_color", "container_border_width", "container_border_color"}
    ids = {x.get("id") for x in settings}
    missing = required - ids
    if missing:
        print(f"{name}: missing {missing}")
```

---

## Prefer theme color dropdowns over raw hex pickers

**User principle:** *never* use raw hex color pickers in section/block settings. Always pull from the theme's named colors via a `select` + `options: "background_colors"` dropdown.

**Bad:**
```json
{ "type": "color", "id": "text_color", "label": "Text Color", "default": "#000000" }
{ "type": "color_background", "id": "bg", "label": "Background", "default": "#ffffff" }
```

**Good:**
```json
{ "type": "select", "id": "text_color", "label": "Text Color",
  "options": "background_colors", "default": "var(--clr-primary)" }
```

Why: raw `color` / `color_background` let editors pick any random hex, disconnected from the theme palette. The `select + background_colors` pattern restricts choices to theme colors, so palette changes propagate site-wide.

**Where raw `color_background` is still OK:**
- `config/settings_schema.json` — theme-level color token DEFINITIONS (with `option_group: { id: "background_colors", ... }`)
- **Nowhere else.** Section and block settings should always use the dropdown.

Default value mapping when migrating:
- `#000000` / `#000` → `var(--clr-primary)` (or `var(--clr-black)`)
- `#ffffff` / `#fff` → `var(--clr-white)`
- `#f8f8f8` / `#f2f2f2` / `#f5f5f5` → `var(--clr-gray)`
- Any other hex → `transparent` (safe default, editor picks from dropdown)

Audit script to find raw color pickers in section/block settings:
```python
import re, os
BASE = "base-theme/sections"
for name in sorted(os.listdir(BASE)):
    with open(f"{BASE}/{name}/index.liquid") as f: c = f.read()
    s = re.sub(r"{%\s*raw\s*%}.*?{%\s*endraw\s*%}", "", c, flags=re.DOTALL)
    m = re.search(r"{%\s*schema\s*%}(.*?){%\s*endschema\s*%}", s, re.DOTALL)
    if not m: continue
    schema = m.group(1)
    for match in re.finditer(r'"type":\s*"(color|color_background)"', schema):
        print(f'{name}: line has "type": "{match.group(1)}" — consider converting to select')
```

---

## Phantom block defaults — remove hardcoded fallbacks in section markup

**The anti-pattern:**
```liquid
<p class="rte">{{ description_block.settings.text | default: "<p>Lorem ipsum dolor sit amet...</p>" }}</p>
<h2>{{ heading_block.settings.text | default: "<h2>Medium length heading</h2>" }}</h2>
<h6>{{ tagline_block.settings.text | default: "<p>Tagline</p>" }}</h6>
```

**Why it's bad:** when no block of that type is present, the Liquid still renders the hardcoded fallback text. The user sees "Lorem ipsum" on the page but can't click or edit it because there's no block bound. To remove the text they'd have to add the block and manually clear it — terrible UX.

**The right pattern:** conditionally render the wrapping element only when the block exists. Never use a non-empty string `| default:` on a block's content field.
```liquid
{% if description_block %}
  <p class="rte" {{ description_block.fluid_attributes }}>
    {{ description_block.settings.text }}
  </p>
{% endif %}
{% if heading_block %}
  <div class="rte" {{ heading_block.fluid_attributes }}>
    {{ heading_block.settings.text }}
  </div>
{% endif %}
```

The block's `"default"` in the schema is the right place for initial content — that only renders when the block is actually added.

Audit:
```python
import re, os
BASE = "base-theme/sections"
for name in sorted(os.listdir(BASE)):
    with open(f"{BASE}/{name}/index.liquid") as f: c = f.read()
    # Only look outside the {% schema %} block
    body = c.split("{% schema %}")[0]
    for line_no, line in enumerate(body.split("\n"), 1):
        m = re.search(r'\{\{\s*\w+_block\.settings\.\w+\s*\|\s*default:\s*"[^"]{2,}"', line)
        if m:
            print(f'{name}:{line_no}: {m.group(0)[:120]}')
```

---

## Theme config: 12 colors + 5 fonts

Every base theme's `config/settings_schema.json` exposes a standard palette of **12 named colors** and **5 named fonts**, each with an `option_group` so sections can reference them in select dropdowns. If any are missing, add them before refinement.

**12 colors** — grouped Brand / Neutrals / Text / Status:

| ID | Default | Group label |
|---|---|---|
| `color_primary`   | `#000000` | Primary   |
| `color_secondary` | `#1F2937` | Secondary |
| `color_accent`    | `#FF5722` | Accent    |
| `color_white`     | `#FFFFFF` | White     |
| `color_light`     | `#FAFAFA` | Light     |
| `color_gray`      | `#F2F2F2` | Gray      |
| `color_muted`     | `#9CA3AF` | Muted     |
| `color_dark`      | `#111827` | Dark      |
| `color_black`     | `#000000` | Black     |
| `color_body`      | `#1F2937` | Body      |
| `color_success`   | `#10B981` | Success   |
| `color_warning`   | `#F59E0B` | Warning   |

Each uses:
```json
{
  "type": "color_background",
  "id": "color_accent",
  "label": "Accent",
  "default": "#FF5722",
  "option_group": { "id": "background_colors", "label": "Accent", "value": "var(--clr-accent)" }
}
```

And is wired in `layouts/theme.liquid`:
```liquid
--clr-accent: {{ settings.color_accent | default: '#FF5722' }};
```

**5 fonts** — Body / Heading / Accent / Italic / Handwriting:

| ID | Default | Group label |
|---|---|---|
| `font_family_body`        | `Roboto`          | Body        |
| `font_family_heading`     | `Roboto`          | Heading     |
| `font_family_accent`      | `Roboto`          | Accent      |
| `font_family_italic`      | `Playfair Display`| Italic      |
| `font_family_handwriting` | `Caveat`          | Handwriting |

Each uses:
```json
{
  "type": "font_picker",
  "id": "font_family_italic",
  "default": "Playfair Display",
  "label": "Italic / Serif Font",
  "option_group": { "id": "font_families", "label": "Italic", "value": "var(--ff-italic)" }
}
```

Wired in `layouts/theme.liquid`:
```liquid
--ff-italic: {{ settings.font_family_italic | font_family | default: "'Playfair Display', Georgia, serif" }};
```

**Never use `font_picker` in section or block settings.** Always pull from the theme via select + `font_families` option group:
```json
{ "type": "select", "id": "font_family", "label": "Font Family",
  "options": "font_families", "default": "var(--ff-body)" }
```

Liquid output:
```liquid
{% if block.settings.font_family != blank %}font-family: {{ block.settings.font_family }};{% endif %}
```
(No `| font_family` filter — the value is already a `var(--ff-…)` reference.)

---

## Canonical block primacy — break composites into reusable blocks

There are a small number of **canonical blocks** in `base-theme/blocks/`:
- `blocks/image` — any time a user-uploaded image appears anywhere in the theme
- `blocks/button` — any time a button appears (10 settings: text, link, font, open_new_tab, style, font_size, padding, background_color, text_color, border, border_radius)
- `blocks/fluid_media` — any time a Fluid Media widget (video / UGC) appears
- `blocks/schema_entry` — reference card used by the schema-reference page

**Rule:** anywhere a section needs one of these things, it must accept the canonical block, not define its own local variant.

### Bad pattern (composite block with embedded image_picker)

```json
{
  "type": "author",
  "name": "Author",
  "settings": [
    { "type": "image_picker", "id": "author_image", "label": "Photo" },
    { "type": "range", "id": "author_image_margin_bottom", "label": "Image Margin" },
    { "type": "text", "id": "author_name", "label": "Name" },
    { "type": "text", "id": "author_position", "label": "Position" }
  ]
}
```

Why bad: the author block defines its own image handling — no aspect ratio, no overlay, no border, no canonical settings. Every composite re-invents images inconsistently.

### Good pattern (flatten; canonical image block + text-only author block)

```json
{
  "type": "author",
  "name": "Author",
  "settings": [
    { "type": "text", "id": "author_name", "label": "Name" },
    { "type": "text", "id": "author_position", "label": "Position" },
    { "type": "text", "id": "company_name", "label": "Company" }
  ]
},
{ "type": "image", "name": "Image", "settings": [ … canonical 11 image settings … ] }
```

Editor composes a testimonial card by adding blocks in order:
1. `testimonial_item` (empty divider block — marks start of a card)
2. `image` (company logo)
3. `testimonial_text` (quote)
4. `image` (author photo)
5. `author` (name + position, no image)

### The divider pattern for grouping

When a section needs grouped cards (testimonials, features, case studies), use an **empty divider block**:

```json
{ "type": "testimonial_item", "name": "New Testimonial Card", "settings": [] }
```

The section Liquid walks blocks statelessly. At each divider it opens a new card `<div>`; at end-of-loop it closes the last one:

```liquid
{% assign in_card = false %}
{% for block in section.blocks %}
  {% case block.type %}
    {% when 'testimonial_item' %}
      {% if in_card %}</div>{% endif %}
      <div class="testimonial-card" {{ block.fluid_attributes }}>
      {% assign in_card = true %}
    {% when 'image' %}
      {% if in_card %}[canonical image markup]{% endif %}
    {% when 'testimonial_text' %}
      {% if in_card %}<div class="quote">{{ block.settings.text }}</div>{% endif %}
    {% when 'author' %}
      {% if in_card %}
        <div class="author">
          <div class="name">{{ block.settings.author_name }}</div>
          <div class="position">{{ block.settings.author_position }}</div>
        </div>
      {% endif %}
  {% endcase %}
{% endfor %}
{% if in_card %}</div>{% endif %}
```

Pros:
- Every image renders through canonical image settings — aspect ratio, fit, object position, overlay, border, radius all consistent
- Composition is explicit (editors see cards build up block-by-block)
- Reorder/delete individual parts without complex wrapper state
- Sections don't duplicate image handling logic

Cons:
- More blocks in the editor list per card
- Editors must maintain correct order (divider → parts → divider → parts)

Migration checklist when refactoring a composite block:
1. Identify composite blocks that embed an `image_picker` — candidates for flatten
2. If the image is a user upload (not data-driven like `post.image`), extract it
3. Strip the image settings from the composite; keep only text/metadata
4. Add `{ "type": "image" }` (full canonical settings inline) to the section's `"blocks"` array
5. Update preset to include `image` block instances in the right positions
6. Rewrite section Liquid to render blocks statelessly (use divider pattern if grouping)

**When NOT to flatten:**
- The image is DATA-DRIVEN (e.g., `post.image`, `product.featured_image`). Keep a legacy wrapper that styles the data-driven image — not an editor-uploaded image.
- The composite's image is truly inseparable (no case-by-case variation needed). Rare.

---

## `media_picker` returns two shapes — fall back to `| image_url`

`{ "type": "media_picker" }` returns a Fluid Media object with `fluid_media_id` when the editor picks a Fluid video / UGC asset — but it returns a plain image object (no `fluid_media_id`) when the editor uploads a JPG/PNG. Rendering only the `<fluid-media-widget>` branch loses every plain-image pick.

Right pattern:
```liquid
{%- assign _m = block.settings.media -%}
{%- assign _fmid = _m.fluid_media_id -%}
{%- assign _img_url = '' -%}
{%- if _fmid == blank and _m -%}
  {%- assign _img_url = _m | image_url -%}
  {%- if _img_url == blank -%}{%- assign _img_url = _m.src | default: _m.url -%}{%- endif -%}
{%- endif -%}

{% if _fmid != blank %}
  <fluid-media-widget media-id="{{ _fmid }}" embed-type="{{ _embed }}" responsive="true" data-fluid-widget="true"></fluid-media-widget>
{% elsif _img_url != blank %}
  <img src="{{ _img_url }}" alt="" loading="lazy">
{% else %}
  <div class="media-wrap__placeholder">…</div>
{% endif %}
```

---

## Delete legacy sections properly (template vs resource)

`DELETE /api/application_themes/{THEME_ID}/resources` with `{ "application_theme_resource": { "key": "sections/foo/index.liquid" } }` returns 200 but **does not** delete the template — it nulls the content, leaving an empty `ApplicationThemeTemplate` record that still appears in the editor as a zero-block section.

To fully purge a legacy section, destroy its template record:

```bash
# Find the resource_id
curl -H "Authorization: Bearer $TOKEN" \
  "https://$COMPANY.fluid.app/api/application_themes/$THEME_ID/resources" \
  | jq '.application_theme_resources[] | select(.key | startswith("sections/foo/"))'
# resource_id will be the template ID (integer)

# Destroy it
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  "https://$COMPANY.fluid.app/api/application_theme_templates/$TEMPLATE_ID"
# → { "message": "Template was successfully destroyed." }
```

Same pattern works for the `home_page/default` template when you need to force preset re-expansion after changing a section's block structure: destroy the template, then re-push `home_page/default/index.liquid`. Fluid creates a fresh template record and runs preset expansion, picking up the new blocks.

---

## Quick Diagnostic Checklist

When a theme looks broken in the editor, check:

- [ ] `layouts/theme.liquid` has `{{ content_for_header }}` and `{{ content_for_layout }}` / `{% content_for_layout %}`
- [ ] All CSS files are in `assets/` (not at theme root) and linked in `theme.liquid`
- [ ] `config/settings_schema.json` has all **12 colors** with `option_group: { id: "background_colors", … }` and all **5 fonts** with `option_group: { id: "font_families", … }`, and `option_group: { id: "text_presets", … }` on every heading font-size
- [ ] `config/settings_data.json` has current values for every setting referenced in `theme.liquid`'s `:root`
- [ ] Every section's outermost element has `{{ section.fluid_attributes }}`
- [ ] Every block's outermost element has `{{ block.fluid_attributes }}`
- [ ] Block loops use `{% %}` not `{%- -%}`
- [ ] Heading blocks default to `<h1>`-`<h6>` (not `<p>`), with inline `color: var(--clr-primary);`
- [ ] All 18 required templates exist at `{template}/default/index.liquid`
- [ ] No section schema uses unsupported types (`number`, `article`, `video`, `video_url`, `inline_richtext`)
- [ ] **Every custom section has the Section Shell (6) + Container (9) pattern** — section_padding, section_border_radius, background_color, background_image, section_border_width, section_border_color + container_max_width, container_padding, container_border_radius, container_background_color, container_background_image, container_overlay_color, container_overlay_opacity, container_border_width, container_border_color
- [ ] **No raw `"type": "color"` or `"type": "color_background"` in section/block settings** — must be `select + options: "background_colors"`
- [ ] **No `"type": "font_picker"` in section/block settings** — must be `select + options: "font_families"`
- [ ] **No phantom `{{ X_block.settings.text | default: "<p>..." }}` fallbacks** in section markup — use `{% if X_block %}...{% endif %}`
- [ ] **Images come from canonical `blocks/image`** — no section-specific `image_picker` fields except on the canonical block itself
- [ ] **Buttons come from canonical `blocks/button`** — 10-setting pattern (text, link, font_family via select:font_families, open_new_tab, style, font_size, padding, background_color, text_color, border, border_radius)
- [ ] **Fluid Media embeds come from canonical `blocks/fluid_media`** with the `media_picker` → `fluid_media_id` / `| image_url` fallback pattern
- [ ] **Grouped cards (testimonials, features, steps) use the divider-block pattern** — empty divider block opens a new card, subsequent canonical/sub-blocks render inside it until the next divider

For block/preset issues specifically:
- [ ] Section's `"blocks"` array in schema has blocks with **inline settings** (not standalone references)
- [ ] Section has a `"presets"` array with initial block instances if the page should ship pre-populated
- [ ] To apply presets to a template: delete + re-push the template resource
