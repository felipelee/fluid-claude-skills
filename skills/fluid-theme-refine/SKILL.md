---
name: fluid-theme-refine
description: >-
  Upgrade any Fluid theme to the gold standard. Works for two scenarios:
  (1) pixel-perfect visual refinement after fluid-theme-clone, and
  (2) migrating an existing / older / legacy Fluid theme to our current
  canonical architecture (Section Shell + Container, theme tokens, canonical
  blocks, richtext hero blocks, modern JS patterns). Triggers on "refine
  theme," "improve theme," "fix the theme," "migrate the theme,"
  "modernize theme," "upgrade theme," "old theme refactor," "fix this
  legacy theme," "bring theme up to standard," "make theme gold
  standard," "QA the theme," "audit the theme," "theme doesn't match
  our pattern," "fix the old sections," "make it closer," "pixel
  perfect," "doesn't match," "fix the spacing," "colors are off,"
  "fonts don't match," "compare and fix," "tighten up," "visual diff,"
  "side by side comparison," "it doesn't look right," "make it exact,"
  or "closer to the original."
metadata:
  version: 3.0.0
---

# Fluid Theme Refine

You are an expert Fluid theme developer. This skill covers **two complementary workflows**:

**A) Pixel-perfect refinement** — after `/fluid-theme-clone` ships a 1:1 site clone, tighten visual fidelity to match the source.

**B) Legacy theme modernization** — take any existing Fluid theme (built before our canonical architecture solidified, or by a dev following older patterns) and bring it up to the current gold standard: Section Shell + Container settings, theme tokens for every color + font, canonical image / button / cart-button blocks, richtext hero blocks, preset expansion, modern CSS (scroll-snap, no Splide), proper Fluid JS hook preservation.

Both workflows share the same loops + rules — just different starting conditions.

**Which workflow is cheaper than a full clone?** If the existing theme's content + brand tokens are already in place and the goal is structural + visual polish, refining is faster than a full clone. If the existing theme's architecture is fundamentally broken (e.g. every section uses hardcoded hex, every image is an `image_picker` inline, Splide is everywhere), a clone might be cleaner — but Phase 0 below tells you exactly which.

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

## Phase 0: Theme Architecture Audit (RUN FIRST, ALWAYS)

**This phase is mandatory when modernizing a legacy theme, and recommended even during pure visual refinement.** It takes 10–15 minutes and surfaces every structural bug that no screenshot can catch. Fix these first; then the visual diff loop in Steps 1–10 only has to worry about px / color / font polish.

The audit walks the **entire theme** — not just sections. An old theme can have beautiful sections that silently break because `body { overflow-x: hidden }` kills sticky nav, or because `assets/config.css` hardcodes font variables that shadow merchant selections, or because `settings_data.json` is missing font-family keys so nothing resolves.

### 0a: Theme-wide files — check each one

Pull the theme with `GET /api/application_themes/{id}/resources?key=...` for each path below, OR work from a local `THEME_DIR` if provided.

| File | What to verify |
|------|---------------|
| `config/settings_schema.json` | Has **5 font slots** (`font_family_body`, `font_family_heading`, `font_family_accent`, `font_family_italic`, `font_family_handwriting`) and **12 color slots** (`color_primary`, `color_secondary`, `color_accent`, `color_white`, `color_light`, `color_gray`, `color_muted`, `color_dark`, `color_black`, `color_body`, `color_success`, `color_warning`). Every font slot has `option_group: { id: "font_families", label, value: "var(--ff-*)" }`. Every color slot has the same for `background_colors`. |
| `config/settings_data.json` | Every schema setting with a default has a seeded value here. Especially the 5 font slots — missing keys mean the `font_family` Liquid filter falls back to Roboto for all of them. |
| `assets/config.css` | Does NOT hardcode `--ff-body`, `--ff-heading`, `--ff-accent`, `--ff-italic`, `--ff-handwriting` in `:root`. Those must come dynamically from `layouts/theme.liquid`. Hardcoded values shadow merchant selections. |
| `assets/reset.css` | `body` uses `overflow-x: clip` (NOT `overflow-x: hidden`). Hidden creates a scroll container and breaks `position: sticky` for the navbar. |
| `assets/global.css` (or `global_styles.css`) | Pagination rules use modern pill styles (circular buttons, 6px gap, active=primary bg) — not the legacy square-bordered paginator. |
| `layouts/theme.liquid` | Inline `{% style %}` outputs `--ff-*` CSS variables from `settings.font_family_*` with proper `| font_family | default:` fallback chain. Same for `--clr-*` variables from `settings.color_*`. |
| `components/pagination/index.liquid` | Uses `paginate.current_offset \| plus: 1` for the "from" value (NOT raw `current_offset` which is 0-indexed). Caps "to" with `paginate.items`. Renders modern pill-button layout. |
| `components/navbar_primary_nav/index.liquid` | Outputs `<ul class="primary-menu" id="primary-nav-menu">` with canonical block wrapper. Iterates `menu.menu_items` (NOT `menu.links`). |
| `components/navbar_locale_dropdown/index.liquid` | Preserves Fluid's locale JS hooks: `#show-language-country-dropdown`, `#mobile-country-language`, `.saveLocaleBtn`, `.country-selector`, `.language-selector`, `.locale-selector`. Never rewrite these. |
| `components/navbar_mobile_menu/index.liquid` | Drawer structure with feature_buttons + primary nav baked in. |
| `blocks/image/` + `blocks/button/` + `blocks/cart_button/` + `blocks/fluid_media/` | These are **canonical REFERENCE files** — they document the schema you inline into sections. They are NOT render targets. `{% render 'cart_button' %}` WILL NOT resolve (Fluid renders only from `components/`). |
| Every `sections/*/index.liquid` | Checked by per-section audit in Step 4b (existing). |
| Every page-template file (`home_page/default/index.liquid`, `product/default/index.liquid`, etc.) | Composition only — no `blocks` in the template schema (blocks come from section presets). Uses `{% section 'name', id: 'unique_id' %}` pattern. |

### 0b: Theme-wide grep audits

Run each grep across the whole theme directory. Any match is a bug.

```bash
# 1. Splide anywhere (forbidden — breaks Fluid's DOM lifecycle)
grep -rn -i "splide" base-theme/ --include="*.liquid" --include="*.css" --include="*.js"

# 2. render targeting blocks/ (Fluid won't resolve — must inline instead)
grep -rn "{% render 'cart_button'\|{% render 'image'\|{% render 'button'\|{% render 'fluid_media'" base-theme/sections/ base-theme/layouts/ base-theme/components/

# 3. font_picker inside a section (only allowed in config/settings_schema.json)
grep -rn '"type": "font_picker"' base-theme/sections/

# 4. Raw hex default in a section schema (should be var(--clr-*))
grep -rn '"default":\s*"#[0-9A-Fa-f]' base-theme/sections/

# 5. Body overflow that kills sticky
grep -rn "overflow-x:\s*hidden\|overflow:\s*hidden\|overflow-y:\s*hidden" base-theme/assets/ base-theme/layouts/ | grep -i "body\|html"

# 6. image_picker used for a content image (allowed fields: background_image, container_background_image, image inside canonical image block, data-fallback wrappers)
grep -rn '"type":\s*"image_picker"' base-theme/sections/ | grep -v 'background_image\|container_background_image\|"id": "image"\|image_override\|logo'

# 7. Navbar JS hooks — must preserve these IDs/classes
grep -rn "show-cart\|fluid-cart-count\|show-language-country-dropdown\|saveLocaleBtn\|country-selector\|language-selector" base-theme/components/ base-theme/sections/main_navbar/
```

Any non-empty result is a finding. Table them up with file:line:issue and fix before moving on.

### 0c: Decide — refine or re-clone?

After Phase 0, you'll have a clear list of architectural findings. Use this rubric:

| Findings | Recommend |
|---------|-----------|
| < 10 total, mostly visual (hex defaults, a few `image_picker`s, some `font_picker` leftovers) | **Refine** — fix in place, proceed to Steps 1–10 |
| 10–25 findings across sections + some theme-wide (reset, config) | **Refine aggressively** — allocate extra time; many recipe patterns in the Recipe Book apply |
| Splide everywhere, every section has hex, no Section Shell pattern, no canonical blocks, no theme tokens, no block-based heroes | **Re-clone** — run `/fluid-theme-clone` against the existing site; faster than rebuilding section by section |

Whichever path you pick, Steps 1–10 below drive the visual polish.

### 0d: Legacy → gold standard — section-by-section migration table

When refining, use this table to map each legacy section to its modern equivalent from the **v4 base theme** library (40 gold-standard sections shipped in `skills/fluid-theme-clone/base-theme/sections/`). Steal the shipped section verbatim; don't recreate.

| Legacy (old Fluid boilerplate) | Gold standard (v4 base theme) |
|---|---|
| `main_product` (Splide PDP) | `product_hero` (full-featured) OR `product_hero_2` (Seed-style grid gallery) + `product_benefits` + `product_ingredients` + `product_how_to_use` + `product_compare` + `product_press` + `product_reviews_showcase` + `related_products` |
| `main_collection` / `main_collection_list` | `collection_showcase` (single) + `collection_index` (all collections) |
| `main_category` / `main_category_list` | `category_showcase` + `category_index` |
| `main_shop` | `shop_showcase` |
| `main_post` / `main_post_list` | `blog_showcase` (single post) + `blog_index` (listing) |
| `main_enrollment` | `enrollment_pack_hero` + `enrollment_whats_included` + `enrollment_compensation` + `enrollment_success_stories` + `enrollment_showcase` |
| Old homepage hero (hardcoded content) | `hero_centered`, `hero_split_stats`, or `hero_editorial` — block-based, theme-tokened |
| Old featured products | `featured_products` (auto-fills from collection picker + fallback chain) |
| Old reviews carousel | `testimonial_grid` (masonry or grid with divider block pattern) |
| Old FAQ accordion | `faq_accordion` (native `<details>` / `<summary>`, bordered or card style) |
| Old press logos | `logo_bar` (canonical image blocks) |
| Old CTA banner | `cta_banner_v2` |
| Old image + text split | `image_text_split` (canonical block pattern) |
| Old stats row | `stats_bar` (prefix/value/suffix/label per stat block) |
| Old process/timeline | `process_steps` (divider + number + image + heading + text blocks) |
| Old UGC carousel (Splide) | `ugc_carousel` (CSS scroll-snap — Splide-free) |
| Old before/after slider | `before_after` (drag slider with configurable labels) |
| Old navbar | `main_navbar` (3-col grid, hamburger overflow, scrolled-bg dropdown, Fluid JS hooks preserved) |
| Old footer | `main_footer` (multi-column with link_list pickers, newsletter, socials, bottom bar) |

**How to use this table:** open the v4 base-theme file, copy its full contents, paste into the legacy theme's section file (matching the file path), adjust only the theme-specific class prefix if collision risk, push. The section comes with Section Shell + Container + theme tokens + canonical blocks + preset + fluid_attributes already.

### 0e: Theme-wide asset migration — fast paths

For the theme-wide files flagged in 0a, use this cheat sheet:

**`assets/reset.css` body overflow fix**
```css
/* old */ body { overflow-x: hidden; }
/* new */ body { overflow-x: clip; }
```
`overflow: clip` is identical visually but does NOT create a scroll container — so `position: sticky` keeps working.

**`assets/config.css` — remove hardcoded font vars**
```css
/* REMOVE these lines: */
--ff-body: "Roboto", sans-serif;
--ff-heading: "Roboto", sans-serif;

/* Dynamic values live in layouts/theme.liquid and are injected from settings.
   Hardcoded :root rules shadow merchant selections. */
```

**`config/settings_data.json` — seed all 5 font slots**
```json
"current": {
  "font_family_body":        "Roboto",
  "font_family_heading":     "Roboto",
  "font_family_accent":      "Roboto",
  "font_family_italic":      "Playfair Display",
  "font_family_handwriting": "Caveat",
  // ...
}
```
Missing slots make `{{ settings.font_family_italic | font_family }}` silently fall back to Roboto for all 5.

**`layouts/theme.liquid` — dynamic font variables**
```liquid
{% style %}
  {{ settings.font_family_body | font_face: font_display: 'swap' }}
  {{ settings.font_family_heading | font_face: font_display: 'swap' }}
  {{ settings.font_family_accent | font_face: font_display: 'swap' }}
  {{ settings.font_family_italic | font_face: font_display: 'swap' }}
  {{ settings.font_family_handwriting | font_face: font_display: 'swap' }}

  :root {
    --ff-body:        {{ settings.font_family_body        | font_family | default: "system-ui, sans-serif" }};
    --ff-heading:     {{ settings.font_family_heading     | font_family | default: "system-ui, sans-serif" }};
    --ff-accent:      {{ settings.font_family_accent      | font_family | default: "system-ui, sans-serif" }};
    --ff-italic:      {{ settings.font_family_italic      | font_family | default: "'Playfair Display', serif" }};
    --ff-handwriting: {{ settings.font_family_handwriting | font_family | default: "'Caveat', cursive" }};

    --clr-primary:   {{ settings.color_primary }};
    --clr-secondary: {{ settings.color_secondary }};
    /* ... etc for all 12 */
  }
{% endstyle %}
```

**`components/pagination/index.liquid` — replace wholesale** with the v4 version. It's 30 lines, modern, and the styles are in `global_styles.css`. Copy from `skills/fluid-theme-clone/base-theme/components/pagination/index.liquid`.

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

## Step 4b: Gold-Standard Theme QA (structural — not visual)

Beyond visual parity, every section must also pass these structural rules. These are the things that fail SILENTLY — a section can look identical to the source but still be broken in the editor or on stores with different content. Walk through each section and check:

**Block editability**
- [ ] Every block (image, text, trust item, etc.) selectable in the Layers panel AND directly clickable in the visual preview — this requires `{{ block.fluid_attributes }}` on the rendered element
- [ ] Canonical image blocks are ALWAYS wrapped (not hidden by empty-image `{% else %}` branch) so the editor can select the slot before uploading
- [ ] Logo / canonical image blocks have `min-width` + `min-height` so empty slots remain clickable
- [ ] Placeholder rendered (dashed-border, striped bg, "Your image" label) when no image AND no data-fallback is set

**Theme tokens (must use, never hardcode)**
- [ ] Every color control is `select` pointed at `background_colors` option group — no raw hex defaults
- [ ] Every font-family control is `select` pointed at `font_families` — no `font_picker` in section settings
- [ ] Values like `var(--clr-primary)`, `var(--ff-heading)` ship as defaults (not literal hex or font names)

**Section Shell + Container pattern**
- [ ] Shell has `section_padding` (padding control), `section_border_radius` (corner_radius), `background_color`, `background_image`, `section_border_width` + `section_border_color`
- [ ] Container has `container_max_width` (select), `container_padding`, `container_border_radius`, `container_background_color`, `container_background_image`, `container_overlay_color` + `container_overlay_opacity`, `container_border_width` + `container_border_color`
- [ ] Vertical padding only on the shell (`padding: Npx 0`) so the background bleeds edge-to-edge
- [ ] Content lives inside the container (`max-width: 1080-1440px; margin: 0 auto; padding: 0 64px`)

**Hero text pattern**
- [ ] Eyebrow / heading / subhead are richtext BLOCKS (editable in editor), not hard-coded section settings
- [ ] Richtext defaults include inline `style="color: var(--clr-primary); font-size: …;"` so the first-paint looks intentional

**Forbidden patterns — grep to detect**
- [ ] `"type": "image_picker"` — only allowed on `background_image` / `container_background_image` / `blocks/image.image` / data-driven fallback wrappers. If it appears on a content image, refactor to a canonical `image` block.
- [ ] `"type": "font_picker"` — only allowed in `config/settings_schema.json`. Never in a section schema.
- [ ] `splide` — forbidden. CSS scroll-snap + vanilla JS instead.
- [ ] Raw hex colors in schema defaults — should be CSS vars (`var(--clr-*)`).
- [ ] `{% render 'cart_button' %}` / any render targeting `blocks/*` — Fluid only resolves from `components/*`. Inline the markup instead.

**Fluid-specific data access**
- [ ] `block.settings.menu.menu_items` (NOT `.links`) when iterating a `link_list` picker
- [ ] Collection-list image fallback: `c.image` → `c.image_url` → `c.image_path` → `c.products[0].image_url` (NOT `c.product_collections` — that field doesn't exist on the Liquid `collections` global)
- [ ] Pagination summary: `{{ paginate.current_offset | plus: 1 }}` (not raw `current_offset` — that's 0-indexed)
- [ ] For sticky navbars / headers: confirm no ancestor has `overflow: hidden` on either axis. If reset.css has `body { overflow-x: hidden }`, change it to `overflow-x: clip`.

**Preset expansion**
- [ ] Presets only fire on FRESH template creation. After editing a section's preset, `DELETE /api/application_theme_templates/{id}` then re-`PUT` the template file to trigger re-expansion.
- [ ] Template schema does NOT contain `blocks` — blocks come from section presets only. Including blocks in a template schema breaks `fluid_attributes` bindings.

**Navbar overflow**
- [ ] Long nav menus collapse cleanly. Default to hamburger collapse (`is-hamburger` class → hide primary-menu, show mobile-toggle even on desktop) vs a "More ▾" dropdown fallback.
- [ ] Never clip nav items mid-word (`overflow: hidden` on `.primary-menu` is forbidden; rely on JS `display: none` via `.is-hidden` class instead).

**Image uploads not rendering**
- [ ] Check block state: image upload often sits in editor draft state. Fetch the live page and grep for the image URL — if it's not there, tell the user to click **Save** in the editor. The draft doesn't persist on its own.

Anything that fails the above → not gold standard → must be fixed before marking the section complete.

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
- `blocks/cart_button` — icon-first cart trigger; preserves Fluid's `#show-cart` + `#fluid-cart-count` JS hooks
- `blocks/schema_entry` — reference card used by the schema-reference page

Reusable theme components (rendered via `{% render %}`, not added as block instances):
- `components/navbar_locale_dropdown` — single component for desktop popover + mobile sheet, preserves Fluid's existing `header.js` locale-switch hooks

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

## Quoting Liquid in setting values — escape brace delimiters

Setting fields with `type: "html"` or `type: "richtext"` **re-evaluate Liquid** in the stored value. If you ever store text that demonstrates Liquid syntax (a docs page, a code-snippet field), Fluid's parser tries to execute the inline `{% for %}` / `{% comment %}` / `{{ x }}` and crashes with confusing errors like "Liquid syntax error: 'comment' tag was never closed" or "Syntax Error in 'for loop'" — even though the surrounding template is fine.

**Symptoms:**
- Page renders the navbar + footer but the section content is replaced with a Liquid error message
- Error references a tag inside a value that's clearly meant to be inert documentation text

**Fix — escape the brace delimiters as HTML entities in the stored value:**
```
{%  →  &#123;%
%}  →  %&#125;
{{  →  &#123;&#123;
}}  →  &#125;&#125;
{#  →  &#123;#       (Jinja-style comments — also re-evaluated)
#}  →  #&#125;
```

Output the field directly, **without** `| escape` — the browser decodes the entities back for display:
```liquid
<pre><code>{{ block.settings.snippet }}</code></pre>
```

(Adding `| escape` would double-encode the `&` in `&#123;` → `&amp;#123;` and the user would see the literal entity reference.)

**Bulk-escape audit script** for an existing reference page:
```python
import json, re

def escape(v):
    return (v.replace('{%', '&#123;%').replace('%}', '%&#125;')
             .replace('{{', '&#123;&#123;').replace('}}', '&#125;&#125;')
             .replace('{#', '&#123;#').replace('#}', '#&#125;'))

# Walk preset blocks, escape any string field that contains {%/{{/{#
for b in schema['presets'][0]['blocks']:
    for k, v in list(b['settings'].items()):
        if isinstance(v, str) and ('{%' in v or '{{' in v or '{#' in v):
            b['settings'][k] = escape(v)
```

---

## Image stretch override — canonical image filling a column

When the canonical `blocks/image` is used inside a hero or split section, the image needs to FILL its column instead of using its own aspect ratio. The canonical image block ships with an `aspect_ratio` control (e.g., `4/5`, `16/9`); for hero columns, override it via section CSS:

```css
.hero__image-slot { align-self: stretch; position: relative; min-height: 360px; }

.hero__image-slot .media-wrap {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  aspect-ratio: unset !important;   /* override canonical block's aspect_ratio */
  margin: 0 !important;
}
.hero__image-slot .media-wrap img {
  width: 100%; height: 100%; object-fit: cover;
}
```

The image block keeps its full canonical settings (overlay, border, radius all still work) — section just stretches the wrapper.

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

---

## The Recipe Book — Legacy → Gold Standard Migrations

Drop-in fixes for every pattern that shows up in legacy themes. Each recipe: (1) what the legacy code looks like, (2) why it's wrong, (3) what to replace it with.

### Recipe 1: Legacy section-level `image_picker` → canonical `image` block

**Legacy:**
```json
"settings": [
  { "type": "image_picker", "id": "hero_image", "label": "Hero Image" }
]
```
```liquid
<img src="{{ section.settings.hero_image | img_url: '1600x' }}" alt="">
```

**Why wrong:** merchant loses all the controls the canonical image block ships (aspect_ratio, fit, object_position, border_radius, border, overlay). Can't duplicate independently. The slot isn't editor-selectable as an image block.

**Replace with:**
```json
"blocks": [
  { "type": "image", "name": "Image", "limit": 1,
    "settings": [
      { "type": "image_picker", "id": "image", "label": "Image" },
      { "type": "text", "id": "alt", "label": "Alt Text" },
      { "type": "select", "id": "aspect_ratio", "label": "Aspect ratio", "default": "1/1",
        "options": [ { "value": "1/1", "label": "Square" }, { "value": "4/5", "label": "Portrait (4:5)" }, { "value": "3/4", "label": "Portrait (3:4)" }, { "value": "4/3", "label": "Standard (4:3)" }, { "value": "16/9", "label": "Widescreen (16:9)" } ]
      },
      { "type": "radio", "id": "fit", "label": "Fit", "default": "cover",
        "options": [ { "value": "cover", "label": "Cover" }, { "value": "contain", "label": "Contain" } ] },
      { "type": "select", "id": "object_position", "label": "Focal point", "default": "center",
        "options": [ { "value": "center", "label": "Center" }, { "value": "top", "label": "Top" }, { "value": "bottom", "label": "Bottom" }, { "value": "left", "label": "Left" }, { "value": "right", "label": "Right" } ] },
      { "type": "corner_radius", "id": "border_radius", "label": "Border Radius" },
      { "type": "range", "id": "border_width", "label": "Border Width", "min": 0, "max": 10, "step": 1, "default": 0, "unit": "px" },
      { "type": "select", "id": "border_color", "label": "Border Color", "options": "background_colors", "default": "var(--clr-primary)" }
    ]
  }
]
```
```liquid
{%- assign image_block = section.blocks | where: 'type', 'image' | first -%}
{% if image_block %}
  {%- assign _alt = image_block.settings.alt | default: '' -%}
  {%- capture _wrap_style -%}
    aspect-ratio: {{ image_block.settings.aspect_ratio | default: '1/1' }};
    {%- assign br = image_block.settings.border_radius -%}{% if br %}border-radius: {{ br.tl }}px {{ br.tr }}px {{ br.br }}px {{ br.bl }}px;{% endif %}
    {% if image_block.settings.border_width > 0 %}border: {{ image_block.settings.border_width }}px solid {{ image_block.settings.border_color }};{% endif %}
  {%- endcapture -%}
  <div class="media-wrap" style="{{ _wrap_style | strip_newlines }}" {{ image_block.fluid_attributes }}>
    {% if image_block.settings.image %}
      <img src="{{ image_block.settings.image | img_url: '1600x' }}" alt="{{ _alt | escape }}"
           style="object-fit: {{ image_block.settings.fit | default: 'cover' }}; object-position: {{ image_block.settings.object_position | default: 'center' }};">
    {% else %}
      <div class="media-placeholder">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" width="48" height="48"><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="8.5" cy="10" r="1.5"/><path d="M3 16l5-4 4 3 4-5 5 6"/></svg>
      </div>
    {% endif %}
  </div>
{% endif %}
```

**Key points:** outer `<div class="media-wrap">` always renders (with `fluid_attributes`) so the editor can select it even when no image is uploaded. Image ↔ placeholder swap is inside, not at the wrapper level.

---

### Recipe 2: Hardcoded `"type": "color"` → theme-token dropdown

**Legacy:**
```json
{ "type": "color", "id": "heading_color", "label": "Heading color", "default": "#111827" }
```

**Why wrong:** merchant picks a one-off hex, disconnected from the theme's brand palette. Changing brand colors requires editing every section's picker.

**Replace with:**
```json
{ "type": "select", "id": "heading_color", "label": "Heading color",
  "options": "background_colors", "default": "var(--clr-primary)" }
```

The `background_colors` option group is defined in `config/settings_schema.json` with all 12 theme colors. Every color setting in every section references it, so one edit to the palette flows everywhere.

---

### Recipe 3: `font_picker` in section → theme-token dropdown

**Legacy:**
```json
{ "type": "font_picker", "id": "heading_font", "label": "Heading font", "default": "Inter" }
```

**Replace with:**
```json
{ "type": "select", "id": "heading_font", "label": "Heading font",
  "options": "font_families", "default": "var(--ff-heading)" }
```

`font_picker` belongs in `config/settings_schema.json` only. Section-level font choices must reference the `font_families` option group (which ships 5 slots: body, heading, accent, italic, handwriting).

---

### Recipe 4: Section-level heading/eyebrow text → richtext BLOCKS

**Legacy:**
```json
"settings": [
  { "type": "text",     "id": "eyebrow",  "label": "Eyebrow",  "default": "Featured" },
  { "type": "text",     "id": "heading",  "label": "Heading",  "default": "Shop now" },
  { "type": "textarea", "id": "subhead",  "label": "Subhead",  "default": "..." }
]
```

**Why wrong:** merchant can't style inline (color, weight, italic emphasis), can't reorder, can't omit one without awkward "leave blank to hide" UX.

**Replace with** canonical eyebrow/heading/subhead blocks:
```json
"blocks": [
  { "type": "eyebrow", "name": "Eyebrow",
    "settings": [
      { "type": "richtext", "id": "text", "label": "Text",
        "default": "<h5 style=\"color: var(--clr-primary); text-transform: uppercase; letter-spacing: 0.14em; font-size: 12px; font-weight: 600;\">Featured</h5>" }
    ]
  },
  { "type": "heading", "name": "Heading",
    "settings": [
      { "type": "richtext", "id": "text", "label": "Text",
        "default": "<h2 style=\"color: var(--clr-primary); font-size: clamp(32px, 4.5vw, 56px); font-weight: 700; letter-spacing: -0.02em; line-height: 1.05;\">Shop now</h2>" }
    ]
  },
  { "type": "subhead", "name": "Subhead",
    "settings": [
      { "type": "richtext", "id": "text", "label": "Text",
        "default": "<p style=\"color: var(--clr-body); font-size: clamp(15px, 1.3vw, 17px); line-height: 1.55;\">Short supporting line.</p>" }
    ]
  }
],
"presets": [
  { "name": "...", "blocks": [ { "type": "eyebrow" }, { "type": "heading" }, { "type": "subhead" } ] }
]
```
```liquid
{%- assign eyebrow_blocks = section.blocks | where: 'type', 'eyebrow' -%}
{%- assign heading_blocks = section.blocks | where: 'type', 'heading' -%}
{%- assign subhead_blocks = section.blocks | where: 'type', 'subhead' -%}

{% for b in eyebrow_blocks %}<div class="rte" {{ b.fluid_attributes }}>{{ b.settings.text }}</div>{% endfor %}
{% for b in heading_blocks %}<div class="rte" {{ b.fluid_attributes }}>{{ b.settings.text }}</div>{% endfor %}
{% for b in subhead_blocks %}<div class="rte" {{ b.fluid_attributes }}>{{ b.settings.text }}</div>{% endfor %}
```

Inline `style=""` on the richtext default gives a proper-looking first paint. Merchant can fully edit typography later via the richtext WYSIWYG.

---

### Recipe 5: Section with no Section Shell / Container → canonical shell

**Legacy:**
```liquid
<section class="legacy-section">
  <div style="max-width: 1280px; margin: 0 auto; padding: 60px 20px;">
    ...
  </div>
</section>
```
Hardcoded dimensions, no merchant control over padding / background / border / container.

**Replace with** the canonical 6 + 9 pattern. Add to the section schema:
```json
"settings": [
  // ... other section settings ...

  { "type": "header", "content": "Container" },
  { "type": "select", "id": "container_max_width", "label": "Max Width", "default": "1280px",
    "options": [
      { "value": "1080px", "label": "Comfy (1080px)" },
      { "value": "1280px", "label": "Default (1280px)" },
      { "value": "1440px", "label": "Wide (1440px)" },
      { "value": "100%",   "label": "Full" }
    ]
  },
  { "type": "padding",       "id": "container_padding",        "label": "Container Padding" },
  { "type": "corner_radius", "id": "container_border_radius",  "label": "Container Border Radius" },
  { "type": "select",        "id": "container_background_color", "label": "Container Background Color", "options": "background_colors", "default": "transparent" },
  { "type": "image_picker",  "id": "container_background_image", "label": "Container Background Image" },
  { "type": "select",        "id": "container_overlay_color",  "label": "Container Overlay Color", "options": "background_colors", "default": "transparent" },
  { "type": "range",         "id": "container_overlay_opacity", "label": "Container Overlay Opacity", "min": 0, "max": 100, "step": 5, "default": 0, "unit": "%" },
  { "type": "range",         "id": "container_border_width",   "label": "Container Border Width", "min": 0, "max": 10, "step": 1, "default": 0, "unit": "px" },
  { "type": "select",        "id": "container_border_color",   "label": "Container Border Color", "options": "background_colors", "default": "var(--clr-primary)" },

  { "type": "header", "content": "Section Shell" },
  { "type": "padding",       "id": "section_padding",        "label": "Section Padding" },
  { "type": "corner_radius", "id": "section_border_radius",  "label": "Section Border Radius" },
  { "type": "select",        "id": "background_color",       "label": "Background Color", "options": "background_colors", "default": "transparent" },
  { "type": "image_picker",  "id": "background_image",       "label": "Background Image" },
  { "type": "range",         "id": "section_border_width",   "label": "Section Border Width", "min": 0, "max": 10, "step": 1, "default": 0, "unit": "px" },
  { "type": "select",        "id": "section_border_color",   "label": "Section Border Color", "options": "background_colors", "default": "var(--clr-primary)" }
]
```
```liquid
{%- style -%}
  .sec.section-{{ section.id }} {
    {%- assign p = section.settings.section_padding -%}
    {%- if p -%}padding: {{ p.top | default: 80 }}px {{ p.right | default: 0 }}px {{ p.bottom | default: 80 }}px {{ p.left | default: 0 }}px;{%- else -%}padding: 80px 0;{%- endif -%}
    {%- assign r = section.settings.section_border_radius -%}
    {%- if r -%}border-radius: {{ r.tl }}px {{ r.tr }}px {{ r.br }}px {{ r.bl }}px;{%- endif -%}
    {% if section.settings.section_border_width > 0 %}border: {{ section.settings.section_border_width }}px solid {{ section.settings.section_border_color }};{% endif %}
    background-color: {{ section.settings.background_color | default: 'transparent' }};
    {%- if section.settings.background_image != blank -%}background-image: url({{ section.settings.background_image | img_url: '2400x' }});background-size:cover;background-position:center;{%- endif -%}
  }
  .sec.section-{{ section.id }} .sec__container {
    position: relative;
    max-width: {{ section.settings.container_max_width | default: '1280px' }};
    margin: 0 auto;
    {%- assign cp = section.settings.container_padding -%}
    {%- if cp -%}padding: {{ cp.top | default: 0 }}px {{ cp.right | default: 64 }}px {{ cp.bottom | default: 0 }}px {{ cp.left | default: 64 }}px;{%- else -%}padding: 0 64px;{%- endif -%}
    background-color: {{ section.settings.container_background_color | default: 'transparent' }};
    {%- if section.settings.container_background_image != blank -%}background-image: url({{ section.settings.container_background_image | img_url: '2400x' }});background-size:cover;background-position:center;{%- endif -%}
    {%- assign ccr = section.settings.container_border_radius -%}
    {%- if ccr -%}border-radius: {{ ccr.tl }}px {{ ccr.tr }}px {{ ccr.br }}px {{ ccr.bl }}px;{%- endif -%}
    {% if section.settings.container_border_width > 0 %}border: {{ section.settings.container_border_width }}px solid {{ section.settings.container_border_color }};{% endif %}
  }
  {%- if section.settings.container_overlay_color != blank and section.settings.container_overlay_opacity > 0 -%}
    {%- assign _cov = section.settings.container_overlay_opacity | divided_by: 100.0 -%}
    .sec.section-{{ section.id }} .sec__container::before { content: ""; position: absolute; inset: 0; background: {{ section.settings.container_overlay_color }}; opacity: {{ _cov }}; pointer-events: none; }
  {%- endif -%}
  .sec.section-{{ section.id }} .sec__container > * { position: relative; }
  @media (max-width: 991px) { .sec.section-{{ section.id }} .sec__container { padding-left: 24px; padding-right: 24px; } }
  @media (max-width: 767px) { .sec.section-{{ section.id }} .sec__container { padding-left: 16px; padding-right: 16px; } }
{%- endstyle -%}
```

---

### Recipe 6: Splide carousel → CSS scroll-snap

**Legacy:**
```html
<div class="splide">
  <div class="splide__track">
    <ul class="splide__list">
      <li class="splide__slide">...</li>
    </ul>
  </div>
</div>
<script>new Splide('.splide').mount();</script>
```

**Why wrong:** Fluid's editor mutates the DOM on every save; Splide re-mounts on each mutation, double-binds events, loses scroll position. Documented incompatibility.

**Replace with** CSS scroll-snap:
```html
<div class="rail" data-carousel-rail>
  <article class="rail__slide">...</article>
  <article class="rail__slide">...</article>
</div>
<button data-carousel-prev>‹</button>
<button data-carousel-next>›</button>
```
```css
.rail {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: calc((100% - 20px * 3) / 4);
  gap: 20px;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-behavior: smooth;
  scrollbar-width: none;
}
.rail::-webkit-scrollbar { display: none; }
.rail__slide { scroll-snap-align: start; }
```
```js
const rail = document.querySelector('[data-carousel-rail]');
const slideWidth = rail.querySelector('.rail__slide').getBoundingClientRect().width + 20;
document.querySelector('[data-carousel-prev]').addEventListener('click', () => rail.scrollBy({ left: -slideWidth, behavior: 'smooth' }));
document.querySelector('[data-carousel-next]').addEventListener('click', () => rail.scrollBy({ left:  slideWidth, behavior: 'smooth' }));
```

Zero dependencies, Fluid-DOM-safe, works natively with trackpad / touch / keyboard / arrow-button controls.

---

### Recipe 7: `{% render 'cart_button' %}` → inline markup

**Legacy navbar:**
```liquid
{%- for block in section.blocks -%}
  {%- when 'cart_button' -%}
    {%- render 'cart_button', block: block -%}
{%- endfor -%}
```

**Why wrong:** Fluid resolves `{% render %}` from `components/` only. `blocks/cart_button/` is a canonical reference file — it documents the schema but isn't a render target. The output is empty.

**Replace with** inline markup (copy from `skills/fluid-theme-clone/base-theme/sections/main_navbar/index.liquid` — the `{%- when 'cart_button' -%}` branch inside the `feature_buttons` capture). Carries the full 14-setting cart button including `id="show-cart"` + `id="fluid-cart-count"` hooks Fluid's cart JS depends on.

---

### Recipe 8: Legacy pagination → modern pill pagination

**Legacy component:**
```liquid
Showing <span>{{ paginate.current_offset }}</span> to <span>{{ paginate.end_offset }}</span> of <span>{{ pagination.total_count }}</span> results
```

**Why wrong:** `current_offset` is 0-indexed (page 1 shows "Showing 0 to 10"). `pagination.total_count` is a typo (should be `paginate.items`).

**Replace with** the v4 component (~30 lines). Copy `skills/fluid-theme-clone/base-theme/components/pagination/index.liquid` wholesale, plus the matching styles in `global_styles.css` (pill buttons, circular shape, modern gap-based layout).

---

### Recipe 9: `body { overflow-x: hidden }` → `clip`

**Legacy reset.css:**
```css
body {
  overflow-x: hidden;
}
```

**Why wrong:** `overflow: hidden` on either axis creates a new scroll container, which breaks `position: sticky` relative to the viewport. Every sticky navbar / tab bar / side rail silently fails.

**Replace with:**
```css
body {
  /* overflow-x: clip keeps the visual effect but doesn't create a
     scroll container, so sticky positioning still works. */
  overflow-x: clip;
}
```

Browser support: Chrome 90+, Safari 16+, Firefox 102+ (95%+ of users).

---

### Recipe 10: Old nav without overflow handling → hamburger-collapse + overflow JS

**Legacy:** navbar with a fixed horizontal menu. 10+ links either clip off-screen or push the logo / actions off.

**Replace with** the v4 main_navbar overflow pattern:
1. 3-column grid: `auto minmax(0, 1fr) auto` (logo / nav / actions — middle column has `minmax(0, 1fr)` so it shrinks rather than pushing)
2. JS measures on paint + resize; if any link would overflow the nav column, adds `.is-hamburger` to the header → CSS hides primary-menu + surfaces the mobile toggle on desktop too
3. Mobile drawer (existing `navbar_mobile_menu` component) contains the full menu

Copy the full Liquid + CSS + JS from `skills/fluid-theme-clone/base-theme/sections/main_navbar/index.liquid`. Key settings exposed: `overflow_mode` (`hamburger` vs `more_dropdown`), `nav_alignment` (flex-start / center / flex-end), `logo_min_width` (reserve clickable area when empty).

---

### Recipe 11: Old footer with hardcoded links → block-based with Fluid link_list pickers

**Legacy:**
```liquid
<footer>
  <div class="footer-col">
    <h4>Shop</h4>
    <ul><li><a href="/">Bestsellers</a></li><li><a href="/">New</a></li></ul>
  </div>
</footer>
```

**Replace with** the v4 main_footer pattern. Each column is a block with a `link_list` picker pointing at a Fluid menu:

```json
{ "type": "column", "name": "Link column",
  "settings": [
    { "type": "text",      "id": "heading", "label": "Heading", "default": "Shop" },
    { "type": "link_list", "id": "menu",    "label": "Menu (Fluid link list)",
      "info": "Pick a Fluid menu. Or leave blank and use Manual links below." },
    { "type": "textarea",  "id": "manual_links", "label": "Manual links (Label | /url per line)" }
  ]
}
```
```liquid
{%- assign menu_items = block.settings.menu.menu_items -%}
{% if menu_items and menu_items.size > 0 %}
  {% for item in menu_items %}
    <li><a href="{{ item.url }}">{{ item.title | escape }}</a></li>
  {% endfor %}
{% elsif block.settings.manual_links != blank %}
  {%- assign lines = block.settings.manual_links | split: "\n" -%}
  {% for line in lines %}
    {%- assign parts = line | strip | split: '|' -%}
    {% if parts.size > 1 %}<li><a href="{{ parts[1] | strip }}">{{ parts[0] | strip | escape }}</a></li>{% endif %}
  {% endfor %}
{% endif %}
```

**Key points:** `menu.menu_items` (NOT `.links`). Fallback to manual_links when menu is blank — both ship in the preset so an empty theme doesn't render an empty footer.

---

### Recipe 12: Editor draft not persisting → tell the user to SAVE

**Symptom:** merchant uploads a logo image (or any image) in the visual editor. The block settings panel shows the uploaded file. But the live render still shows the fallback (company logo, or placeholder).

**Why:** the visual editor maintains unsaved state in the iframe only. The theme-resource API doesn't receive the change until the merchant clicks **Save** / **Publish** at the top of the editor.

**Fix workflow:**
1. Confirm the block setting with a debug echo: `<!-- {{ block.settings.image | json }} -->`
2. If it shows `null`, tell the user to hit Save in the editor
3. After they save, hard-refresh the preview page (Cmd+Shift+R)
4. The live render should now pick up the uploaded image

This is a USER-FLOW issue, not a code bug. But it's the most common "my upload isn't showing" support case.

---

### Using the Recipe Book

When the Phase 0 audit or Step 4b structural QA surfaces a finding, search this book for the matching pattern and apply. Most legacy themes hit 3–5 of these recipes. After applying, re-run Phase 0 — findings should drop to zero before moving to Steps 1–10 visual diff.

**Shortcuts:**
- Migration table (Phase 0d) → which v4 base-theme section replaces which legacy `main_*` section
- Asset cheat sheet (Phase 0e) → theme-wide file fixes (reset.css, config.css, settings_data.json, theme.liquid, pagination component)
- Recipe Book (this section) → in-section transformations with before/after code

All three feed into the same end state: every custom section passes the Step 4b audit, every theme-wide file passes the Phase 0 audit, and the visual diff loop only handles true visual polish.
