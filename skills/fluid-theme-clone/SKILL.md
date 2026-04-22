---
name: fluid-theme-clone
description: >-
  Clone any website into a pixel-perfect Fluid theme. Use when the user wants
  to clone, replicate, or copy a website page into a Fluid theme. Triggers on
  "clone this page," "replicate this site," "copy this page into Fluid,"
  "page clone," "1:1 clone," "pixel-perfect copy," "exact clone," "match this
  page," "build this page in Fluid," "recreate this page," "clone into Fluid,"
  "copy this site," "theme clone," "site clone," or "rebuild in Fluid."
metadata:
  version: 3.1.0
---

# Fluid Theme Clone

You are an expert Fluid theme developer. Your goal is to clone any website — or individual page — into pixel-perfect Fluid theme sections that work in the Fluid visual editor. You scrape content, audit visuals, upload images to the DAM, build sections, assemble page templates, and push everything to the Fluid theme API.

This skill supports two modes:
- **Single page clone** — clone one specific URL
- **Full site clone** — systematically clone all key pages of a website

## Every run is a fresh run

This skill is used across many different sites and Fluid accounts. **Never reuse data from a previous run.** Always ask for credentials, always start with a fresh working directory.

---

## Step 1: Collect Inputs

Ask the user for ALL of these before doing anything:

| Input | Required | Description |
|-------|----------|-------------|
| `SOURCE_SITE` | Yes | Base URL of the site to clone (e.g. `https://yellowbirdfoods.com`) |
| `SITE_PREFIX` | Yes | Short prefix for section naming (e.g. `yb`, `hiya`) |
| `FLUID_URL` | Yes | Fluid store URL (e.g. `https://companyname.fluid.app`) |
| `FLUID_TOKEN` | Yes | Fluid API token (`PT-xxx`) |
| `FIRECRAWL_API_KEY` | Yes | Firecrawl API key from [firecrawl.dev](https://firecrawl.dev) |

For **single page clone**, also collect:

| Input | Required | Description |
|-------|----------|-------------|
| `SOURCE_URL` | Yes | Full URL of the specific page to clone |
| `PAGE_TYPE` | Yes | `"home"` \| `"page"` \| `"product"` \| `"collection"` |
| `PAGE_SLUG` | Yes | Slug for the Fluid template (e.g. `about`, `our-story`) |

---

## Step 2: Validate Credentials

Run these in parallel. If ANY fail, stop immediately.

```python
# 1. Source site reachable
requests.get(source_site, timeout=10)  # expect 200

# 2. Fluid API token + get company info
resp = requests.get(f"{fluid_url}/api/settings/company_countries",
                    headers={"Authorization": f"Bearer {fluid_token}"}, timeout=10)
# expect 200, extract company info

# 3. Firecrawl key works
requests.post("https://api.firecrawl.dev/v1/scrape",
              headers={"Authorization": f"Bearer {fc_key}"},
              json={"url": "https://example.com", "formats": ["markdown"], "limit": 1},
              timeout=15)
# expect 200
```

Print results:
```
[Preflight] Source site: OK yellowbirdfoods.com
[Preflight] Fluid API:  OK companyname.fluid.app (Company ID: 980243068)
[Preflight] Firecrawl:  OK
```

**CRITICAL: Confirm company identity before proceeding.** Display the company name returned by the Fluid API and ask the user to confirm this is the correct store. This prevents accidentally writing theme data to the wrong Fluid account.

```
⚠️  This token resolves to: "Yellowbird Foods" (Company ID: 980243068)
    Store URL: https://companyname.fluid.app

Is this the correct store? (yes/no)
```

**Do NOT proceed until the user confirms.**

```
[Preflight] All checks passed — starting theme clone.
```

---

## Step 3: Initialize Working Directory

Create a fresh working directory and copy the base theme scaffolding:

```bash
WORK_DIR="/tmp/fluid-theme-$(echo $SOURCE_SITE | sed 's|https\?://||;s|/.*||')"
mkdir -p "$WORK_DIR"
cp -r "${CLAUDE_SKILL_DIR}/base-theme/"* "$WORK_DIR/"
```

If the `base-theme/` directory is empty or missing, create the minimum scaffolding manually:

```
$WORK_DIR/
├── layouts/theme.liquid
├── home_page/default/index.liquid
├── page/default/index.liquid
├── product/default/index.liquid
├── collection/default/index.liquid
├── sections/main_navbar/index.liquid
├── sections/main_footer/index.liquid
├── sections/main_product/index.liquid   (DO NOT MODIFY)
├── config/settings_schema.json
├── config/settings_data.json
└── assets/product.js
```

See the [Fluid Theme Architecture](#fluid-theme-architecture) section below for what goes in each file.

---

## Step 4: Page Discovery (Full Site Clone Only)

When cloning an entire site, discover all pages before building.

### 4a: Scrape the homepage with Firecrawl for navigation structure
### 4b: Open the site in the browser, inspect nav menus and footer links
### 4c: Build a page manifest

```
PAGE MANIFEST FOR https://yellowbirdfoods.com
=============================================

GLOBAL (clone once, used on all pages):
  - Navigation bar -> sections/main_navbar/index.liquid
  - Footer -> sections/main_footer/index.liquid

HOMEPAGE:
  - https://yellowbirdfoods.com -> home_page/default/index.liquid (type: home)

PRODUCT PAGES:
  - https://yellowbirdfoods.com/products/habanero -> product/habanero/index.liquid (type: product)

COLLECTION PAGES:
  - https://yellowbirdfoods.com/collections/all -> collection/default/index.liquid (type: collection)

STATIC PAGES:
  - https://yellowbirdfoods.com/pages/about -> page/about/index.liquid (type: page)
  - https://yellowbirdfoods.com/pages/faq -> page/faq/index.liquid (type: page)

TOTAL: X pages
```

### 4d: Identify shared sections (CTA banners, testimonials, newsletter signup) — build once, reuse
### 4e: Clone order — nav/footer first, homepage, products, collections, static pages

---

## Phase 1: Content Scraping

Use Firecrawl to extract text and image URLs from the source page.

```bash
curl -s -X POST https://api.firecrawl.dev/v1/scrape \
  -H "Authorization: Bearer <FIRECRAWL_API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"url": "<SOURCE_URL>", "formats": ["markdown"], "timeout": 30000}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('markdown',''))" \
  > /tmp/scraped-<PAGE_SLUG>.md
```

Extract: all text content, all image URLs, all video URLs, page structure (identify sections), navigation structure, footer structure. Create a **section inventory**.

---

## Phase 2: Visual Audit (Screenshot-Driven)

Screenshots are the **primary reference** for building sections.

### 2a: Navigate to SOURCE_URL, remove overlays/popups
```javascript
document.querySelectorAll('[data-acsb-custom-trigger],.acsb-trigger,.acsb-widget,.acsb-overlay,.popup,.modal,[class*="cookie"],[class*="banner"]').forEach(e => e.remove());
```

### 2b: Scroll through entire page, screenshot each section boundary

### 2c: Extract exact CSS values per section
```javascript
var el = document.querySelector('.hero-section');
var s = getComputedStyle(el);
[s.backgroundColor, s.color, s.fontFamily, s.fontSize, s.fontWeight, s.padding, s.margin].join(' | ');
```

### 2d: Note animations (scroll, hover, carousel, parallax)

### 2e: Check responsive at 375px, 768px, 1280px

### Output: Section Inventory
```
SECTION INVENTORY FOR <SOURCE_URL>:

1. Hero
   - Layout: Full-width, centered text over background image
   - BG: #1B3A4B, Text: #FFFFFF, Button: #FF6B35
   - Font: heading 48px/800, subtext 18px/400
   - Padding: 120px top/bottom
   - Animation: fade-in on load
   - Responsive: stacks vertically on mobile

2. Features Grid
   - Layout: 3-column card grid with icons
   - BG: #FFFFFF, Cards: #F9FAFB with 12px radius
   - Gap: 24px, max-width: 1200px
   - Animation: stagger fade-in (0.1s delay per card)
   - Responsive: 1col mobile, 2col tablet, 3col desktop

TOTAL SECTIONS: X
```

---

## Phase 3: Image Extraction & DAM Upload

### Extract all image URLs from the browser:
```javascript
var imgs = [];
document.querySelectorAll('img').forEach(function(i) {
  var s = (i.src || i.currentSrc || '').split('?')[0];
  if (s && s.indexOf('http') === 0 && imgs.indexOf(s) === -1) imgs.push(s);
});
document.title = imgs.length + ' images: ' + imgs.join(' | ');
```

Also check: background images in CSS, lazy-loaded (`data-src`), inline SVGs (copy markup directly).

### Upload to Fluid DAM

**All images must go to the DAM. Never hotlink to source CDNs.**

```bash
curl -s -X POST https://upload.fluid.app/upload \
  -H "Authorization: Bearer <FLUID_TOKEN>" \
  -F "external_asset_url=<SOURCE_IMAGE_URL>" \
  -F "name=<descriptive-name>"
```

Use `asset.default_variant_url` from the response. For batch uploads, see [references/batch-upload-script.md](references/batch-upload-script.md).

---

## Phase 4: Build Sections

### Naming convention

Prefer canonical names from the section library above (e.g. `sections/feature_grid/`, `sections/testimonial_grid/`). Use a canonical section whenever one fits — don't recreate a slightly different version of the same pattern.

If the source site truly has a section that doesn't match any canonical pattern, use snake_case with no prefix:

```
sections/<descriptive_name>/index.liquid
```

Do NOT use `exact-<site-prefix>-*` — the old convention created cruft (banner1, feature2-8, cta_banner3-5) that had to be purged later.

### Gold Standard Section Architecture

Every section MUST follow these rules. Violating any of them breaks the Fluid visual editor.

#### Section Shell + Container pattern (required)

Every custom section ships with **15 layout settings** in its schema — split into two groups:

- **Section Shell (6)** — outer colored box: `section_padding`, `section_border_radius`, `background_color`, `background_image`, `section_border_width`, `section_border_color`
- **Container (9)** — inner content frame: `container_max_width`, `container_padding`, `container_border_radius`, `container_background_color`, `container_background_image`, `container_overlay_color`, `container_overlay_opacity`, `container_border_width`, `container_border_color`

All color settings are `select + options: "background_colors"`. All border widths are `range 0-10 px`. Split border controls (width + color) because Fluid's native `border` type uses a hex color picker that breaks the theme-driven color rule.

See [fluid-theme-refine](../fluid-theme-refine/SKILL.md#section-shell-pattern--enforce-on-every-custom-section) for the full CSS wire-up template — every canonical section in the base theme implements it verbatim.

#### Content = Blocks, Layout = Settings

- **Section settings** are for layout ONLY: Section Shell + Container above
- **Blocks** are for ALL content: headings, paragraphs, images, buttons, cards, etc.
- Every piece of visible text is a block — never a section setting

#### Text Blocks Use `richtext`

ALL text content uses `richtext` type — the WYSIWYG handles font, size, weight, color, alignment. Defaults must be wrapped in HTML tags.

```json
{ "type": "richtext", "id": "text", "label": "Heading", "default": "<h2>Your heading here</h2>" }
```

**NEVER** use `text` or `textarea` for visible content — those create plain text that can't be styled in the editor.

#### Block Attributes on `<div>` Wrappers

`{{ block.fluid_attributes }}` goes on a `<div>` wrapper — NEVER directly on `<h1>`, `<h2>`, `<p>`, `<span>`, `<a>`, or other semantic elements.

```liquid
{% when 'heading' %}
  <div class="rte heading-wrap" {{ block.fluid_attributes }}>
    {{ block.settings.text }}
  </div>
```

#### No Whitespace-Trimming Dashes in Block Loops

`{%- -%}` dashes in block loops BREAK the Fluid editor parser. Always use `{% %}`:

```liquid
{% for block in section.blocks %}
  {% case block.type %}
    {% when 'heading' %}
```

Dashes ARE safe inside `{%- style -%}` blocks (CSS generation, not block rendering).

#### Native Padding Type with Wiring

```json
{ "type": "padding", "id": "section_padding", "label": "Section Padding" }
```

Wire in the `{%- style -%}` block:
```liquid
{%- assign p = section.settings.section_padding -%}
{%- if p -%}
  {%- capture pt -%}{{ p.top }}{%- endcapture -%}
  {%- capture pb -%}{{ p.bottom }}{%- endcapture -%}
  {%- capture pl -%}{{ p.left }}{%- endcapture -%}
  {%- capture pr -%}{{ p.right }}{%- endcapture -%}
  padding-top: {% if pt contains 'var(' %}{{ pt }}{% else %}{{ pt }}px{% endif %};
  padding-bottom: {% if pb contains 'var(' %}{{ pb }}{% else %}{{ pb }}px{% endif %};
  padding-left: {% if pl contains 'var(' %}{{ pl }}{% else %}{{ pl }}px{% endif %};
  padding-right: {% if pr contains 'var(' %}{{ pr }}{% else %}{{ pr }}px{% endif %};
{%- endif -%}
```

#### Background Color — Select with Option Group

Use `select` with `"options": "background_colors"` — NOT `color_background` (raw hex picker disconnected from theme):

```json
{ "type": "select", "id": "background_color", "label": "Background Color", "options": "background_colors", "default": "transparent" }
```

**CRITICAL BUG:** Never write `background-color: var(--clr-{{ section.settings.background_color }})`. When the setting is empty, this renders `var(--clr-)` — invalid CSS that **silently breaks the entire rule block** including padding and border-radius. The correct pattern:

```liquid
background-color: {{ section.settings.background_color | default: 'transparent' }};
```

The `background_colors` option group values ARE already CSS values like `var(--clr-primary)` or `transparent`.

#### CSS Uses Theme Variables — No Hardcoded Values

```css
/* WRONG */
font-family: 'Spartan', sans-serif;
color: #023026;
padding: 0 64px;

/* RIGHT */
font-family: var(--ff-heading), sans-serif;
color: var(--clr-heading, #023026);
padding: 0 var(--space-9xl, 64px);
```

Every section needs RTE heading rules:
```css
.section-class .rte h1,
.section-class .rte h2,
.section-class .rte h3 {
  font-family: var(--ff-heading), sans-serif;
  font-weight: 700;
  margin: 0;
  line-height: 1.1;
}
```

#### Root Element Pattern

```html
<section
  class="section-name section-{{ section.id }}"
  data-section-id="{{ section.id }}"
  {{ section.fluid_attributes }}
>
```

#### Consistent Container and Breakpoints

All sections use 1280px max-width with theme variable horizontal padding:
```css
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--space-9xl, 64px);
}
@media (max-width: 991px) { .container { padding: 0 var(--space-3xl, 24px); } }
@media (max-width: 767px) { .container { padding: 0 var(--space-lg, 16px); } }
```

Standardized breakpoints: `991px` (tablet), `767px` (mobile). Never use 749px, 768px, or 1023px.

#### Images — always through `blocks/image`

Never use a local `image_picker` inside a section schema. All user-uploaded images come through the canonical `blocks/image` block, which provides consistent aspect ratio, fit, object position, overlay, border, and border-radius controls across every section.

When a section needs an image, inline the canonical image block settings into the section's `blocks` array:
```json
{ "type": "image", "name": "Image", "settings": [ /* full canonical image settings */ ] }
```

Data-driven images (product.images, post.image) are the exception — those use `| image_url` directly in the section Liquid, since the user isn't picking them.

For Fluid Media (video / UGC), use `blocks/fluid_media` — and handle both shapes the `media_picker` returns (Fluid Media object with `fluid_media_id` vs plain image upload). See [fluid-theme-refine](../fluid-theme-refine/SKILL.md#media_picker-returns-two-shapes--fall-back-to--image_url) for the fallback pattern.

#### Dynamic Product Data — Never Static Blocks

For product grids, use Fluid's data system instead of static blocks:
- `product_list` setting type for curated product carousels
- `products` global variable for automatic product loops
- `collection.enrollment_packs | parse_json` for enrollment pack grids

Static product blocks disappear on editor save. Dynamic data never does.

### Schema rules
- Use `range` — NOT `number` (unsupported, breaks the editor)
- Use `post` — NOT `article` (unsupported)
- Use `video_picker` or `url` — NOT `video` or `video_url` (unsupported)
- Use `| default:` fallbacks on all Liquid variable access

### Documenting Liquid in setting values

If you ever quote Liquid syntax (`{% for %}`, `{{ x }}`, `{# #}`, `{% comment %}`) inside a setting value (e.g. for a docs page), Fluid will **re-evaluate** that text as Liquid when the value is read — typed `html` and `richtext` settings both trigger re-eval. Symptom: page errors with "Liquid syntax error" pointing to a tag inside what's supposed to be inert text.

**Fix:** escape the Liquid delimiters as HTML entities in the stored value, then output without `| escape` so the browser decodes them back for display.

```
{% → &#123;%
%} → %&#125;
{{ → &#123;&#123;
}} → &#125;&#125;
{# → &#123;#
#} → #&#125;
```

```liquid
<pre><code>{{ block.settings.snippet }}</code></pre>
```

The browser sees `&#123;%` and renders `{%` for the user. Liquid never sees the tag.

Read [references/section-template.md](references/section-template.md) for the full section boilerplate.
Read [references/schema-settings-reference.md](references/schema-settings-reference.md) for all setting types.
Read [references/css-js-patterns.md](references/css-js-patterns.md) for CSS/JS patterns.

### Canonical blocks

The base theme ships with a small number of **canonical block files** in `base-theme/blocks/`. Any section that needs one of these concepts MUST accept the canonical block (inline the settings into the section schema) instead of defining a local variant:

- `blocks/image` — user-uploaded image with aspect ratio, fit, object position, overlay, border, corner radius
- `blocks/button` — 10 settings: text, link, font_family (select → font_families), open_new_tab, style (filled/outline/text), font_size, padding, background_color, text_color, border_width/color, border_radius
- `blocks/fluid_media` — `<fluid-media-widget>` wrapper with embed_type (auto/inline/popover/modal), aspect ratio, placeholder fallback to `| image_url` for non-Fluid assets
- `blocks/cart_button` — icon-first cart trigger with 14 theme-driven settings (icon: bag/cart/basket/minimal · style: filled/outline/text · padding · radius · border · count badge with own colors). Preserves Fluid's existing cart JS hooks `#show-cart` + `#fluid-cart-count`.
- `blocks/schema_entry` — reference card used by the schema-reference page

**Rule:** `image_picker` only lives on `blocks/image` (and data-driven wrappers like `blocks/post_image`). `font_picker` only lives on `config/settings_schema.json`. Never in section settings.

### Canonical components

Some patterns live in `base-theme/components/` because they're rendered via `{% render '<name>' %}` from a section (not added as block instances). They're still theme-driven and reusable:

- `components/navbar_locale_dropdown` — single component renders both desktop popover AND mobile slide-in sheet for country/language selection. 23 theme-driven settings (display mode: flag+code/flag-only/code-only/flag+name · panel colors · save button colors). Preserves Fluid's existing locale JS hooks (`#show-language-country-dropdown`, `#mobile-country-language`, `.saveLocaleBtn`, `.country-selector`, `.language-selector`, `.locale-selector`) so the built-in locale-switch logic keeps working without touching `header.js`.

### Canonical section library

The base theme ships a standard library of award-winning ecommerce sections. Compose home pages from these — do not rebuild from scratch:

**Heroes (3)**

| Section | Purpose |
|---|---|
| `hero_centered`     | Full-bleed background with centered content, dual CTAs, status-pill badge, trust bar with stars, animated scroll cue. 80vh min-height. Style: Allbirds / Athletic Greens. |
| `hero_split_stats`  | 50/50 split (text + canonical image block, flippable) with bottom dark stats strip (4 stat blocks). Style: Tesla / Liquid Death. |
| `hero_editorial`    | 3-column magazine: vertical rotated meta column + main text (uses `var(--ff-italic)` Playfair) + portrait canonical image with caption pill, tag pills + byline. Style: Aesop / Aimé Leon Dore. |

**Content & conversion (14)**

| Section | Purpose |
|---|---|
| `image_text_split`   | Hero / story — 50/50 with flip, accepts canonical image + heading + text + button blocks |
| `logo_bar`           | Press / partner logos grid, canonical image blocks |
| `feature_grid`       | Benefits grid — divider + canonical image + heading + text + button (one card per divider) |
| `featured_products`  | Collection-driven product grid (collection picker + products_to_show range). Uses `product.images[0].src → image_url → image \| image_url` fallback chain. |
| `stats_bar`          | Numbers row (prefix/value/suffix/label per stat block) |
| `cta_banner_v2`      | Final full-width CTA |
| `faq_accordion`      | Native `<details>`/`<summary>` with bordered or card style |
| `rich_content`       | Flexible single-column composer (eyebrow/heading/text/image/fluid_media/button) |
| `ugc_carousel`       | CSS scroll-snap carousel of fluid_media blocks with UGC defaults (9:16, popover embed) — Splide-free |
| `comparison_table`   | Us-vs-Them table with check/X/text per row, "Recommended" badge |
| `testimonial_grid`   | Masonry or grid with divider-block testimonial cards (rating + image + quote + author sub-blocks) |
| `before_after`       | Drag slider with configurable initial position, labels, aspect ratio |
| `process_steps`      | Horizontal or vertical steps with divider + number (own block) + image + heading + text sub-blocks, connector line |
| `collection_tiles`   | Shop-by-category tiles with hover zoom, overlay gradient, CTA chip, auto-fills from Fluid collection. Uses `collection.canonical_url` for link, `image_url → image_path → first product image` fallback chain. |

All 17 use the Section Shell (6) + Container (9) pattern and reference `background_colors` / `font_families` option groups exclusively. Heroes additionally use the **canonical block primacy** pattern for hero images — the image is added as a `blocks/image` instance (not a section setting), with CSS `aspect-ratio: unset !important` override to fill the column.

### The Compare -> Code -> Preview -> Refine Loop

Each section goes through an iterative cycle until it matches the source. **Do NOT move to the next section until the current one passes visual comparison.**

1. **COMPARE** — Study the source screenshot from Phase 2
2. **CODE** — Build the section using exact extracted values (hex colors, px sizes, font weights)
3. **PREVIEW** — View your built section in the browser or MCP preview
4. **DIFF** — Side-by-side comparison: layout, background, typography, spacing, border-radius, images, buttons, responsive
5. **REFINE** — Fix discrepancies, re-extract CSS values if needed, loop back to step 3

Aim for 1-3 rounds per section. After 3 rounds, note remaining deviations in a comment and move on.

---

## Phase 5: Assemble Page Template

Read [references/page-templates.md](references/page-templates.md) for the correct template structure per page type.

| PAGE_TYPE | Template Location |
|-----------|------------------|
| `home` | `home_page/default/index.liquid` |
| `page` | `page/<PAGE_SLUG>/index.liquid` |
| `product` | `product/<PAGE_SLUG>/index.liquid` |
| `collection` | `collection/<PAGE_SLUG>/index.liquid` |

### Key rules
- `{% layout 'theme' %}` is always line 1
- Each `{% section 'name', id: 'unique_id' %}` needs a unique `id`
- The `{% schema %}` block maps each `id` to a section `type` with optional `settings` overrides
- The `order` array controls rendering order
- **Product pages**: always include `{% section 'main_product', id: 'product_main' %}` first — never replace it
- Read [references/fluid-rules.md](references/fluid-rules.md) for what NOT to touch
- Read [references/template-variables.md](references/template-variables.md) for available variables per page type

### CRITICAL: Template schemas must NOT contain blocks

**NEVER** put block data in template schemas. Blocks come from section presets ONLY.

```json
/* WRONG — breaks fluid_attributes bindings */
"sections": {
  "hero": {
    "type": "exact-rain-hero",
    "blocks": { "heading_1": { "type": "heading", ... } }
  }
}

/* RIGHT — section type + settings only */
"sections": {
  "hero": {
    "type": "exact-rain-hero",
    "settings": { "section_padding": { "top": 80, "bottom": 80, "left": 0, "right": 0 } }
  }
}
```

### Preset padding only applies on first add

Section preset values (including `section_padding`) only take effect when a section is **first added** to a template. They do NOT retroactively update existing templates. The editor's saved data always takes precedence.

### API push → editor Save workflow

After pushing section code via `PUT /api/application_themes/{id}/resources`:
1. Open the visual editor
2. Click **Save** (even with no changes)
3. This triggers Fluid's block registration system
4. Blocks become clickable in both Layers panel and preview

---

## Phase 6: Full-Page Visual QA

Phase 4 ensures each section matches. Phase 6 ensures the **assembled page** matches.

### 6a: Open source and built pages side by side, scroll both, screenshot-compare each section pair
### 6b: Responsive comparison at 375px, 768px, 1280px
### 6c: Functionality — carousels, accordions, buttons, hover effects, scroll animations, videos
### 6d: Structural checklist:
- [ ] Every section has `{{ section.fluid_attributes }}` on root
- [ ] Every block has `{{ block.fluid_attributes }}`
- [ ] All images use DAM URLs
- [ ] Schema has `presets` with default content
- [ ] Page template has correct `order` array
- [ ] No unsupported schema types
- [ ] All Liquid variable access uses `| default:` fallbacks
- [ ] All text content matches source exactly

---

## Phase 7: Upload Theme to Fluid

After all pages are built and QA'd, push the entire theme to Fluid.

### 7a: Create or find the application theme

```python
# Create new theme
resp = requests.post(f"{fluid_url}/api/application_themes",
    headers={"Authorization": f"Bearer {fluid_token}", "Content-Type": "application/json"},
    json={"application_theme": {"name": f"Clone - {source_site}", "status": "active"}})
theme_id = resp.json()["application_theme"]["id"]
```

### 7b: Upload every file

Walk the working directory and PUT each file as a theme resource:

```python
TEXT_EXTS = {'.liquid', '.css', '.js', '.json', '.html', '.txt', '.svg'}

for root, dirs, files in os.walk(WORK_DIR):
    for fname in files:
        if fname.startswith('.'): continue
        filepath = os.path.join(root, fname)
        key = os.path.relpath(filepath, WORK_DIR)
        ext = os.path.splitext(fname)[1].lower()

        if ext in TEXT_EXTS:
            with open(filepath, 'r') as f:
                content = f.read()
            requests.put(f"{fluid_url}/api/application_themes/{theme_id}/resources",
                headers=headers, json={"key": key, "content": content})
        else:
            # Binary: upload to DAM first, then register
            with open(filepath, 'rb') as f:
                dam_resp = requests.post("https://upload.fluid.app/upload",
                    headers={"Authorization": f"Bearer {fluid_token}"},
                    files={"file": (fname, f)}, data={"fileName": fname})
            dam_url = dam_resp.json().get("asset", {}).get("default_variant_url")
            if dam_url:
                requests.put(f"{fluid_url}/api/application_themes/{theme_id}/resources",
                    headers=headers, json={"key": key, "dam_asset": dam_url})

print(f"Theme uploaded. ID: {theme_id}")
```

See [references/theme-upload-api.md](references/theme-upload-api.md) for full API details.

---

## Phase 4b: Theme Config Setup

Before building sections, set up the theme's design tokens so sections can reference them.

### settings_data.json — Set the source site's design tokens

The base theme defines a **12-color palette** and a **5-font palette**. Extract the source site's tokens and map them in:

```json
{
  "current": {
    "color_primary":   "#023026",
    "color_secondary": "#1F2937",
    "color_accent":    "#fc6f39",
    "color_white":     "#FFFFFF",
    "color_light":     "#FAF8F1",
    "color_gray":      "#F2F2F2",
    "color_muted":     "#9CA3AF",
    "color_dark":      "#111827",
    "color_black":     "#000000",
    "color_body":      "#1F2937",
    "color_success":   "#10B981",
    "color_warning":   "#F59E0B",

    "font_family_body":        "Inter",
    "font_family_heading":     "Spartan",
    "font_family_accent":      "Inter",
    "font_family_italic":      "Playfair Display",
    "font_family_handwriting": "Caveat",

    "font_size_h1": 60,
    "font_size_h2": 48,
    "font_size_h3": 32
  }
}
```

### settings_schema.json — option_groups drive every section dropdown

Every color and font setting needs an `option_group` so sections can reference them in select dropdowns.

**Colors — 12 entries, all `option_group: { id: "background_colors", … }`:**

```json
{ "type": "color_background", "id": "color_primary",   "label": "Primary",
  "default": "#000000",
  "option_group": { "id": "background_colors", "label": "Primary",   "value": "var(--clr-primary)" } },
{ "type": "color_background", "id": "color_secondary", "label": "Secondary",
  "default": "#1F2937",
  "option_group": { "id": "background_colors", "label": "Secondary", "value": "var(--clr-secondary)" } },
{ "type": "color_background", "id": "color_accent",    "label": "Accent",
  "default": "#FF5722",
  "option_group": { "id": "background_colors", "label": "Accent",    "value": "var(--clr-accent)" } },
/* then: white, light, gray, muted, dark, black, body, success, warning — same pattern */
```

**Fonts — 5 entries, all `option_group: { id: "font_families", … }`:**

```json
{ "type": "font_picker", "id": "font_family_body",        "default": "Roboto",
  "label": "Body Font",
  "option_group": { "id": "font_families", "label": "Body",        "value": "var(--ff-body)" } },
{ "type": "font_picker", "id": "font_family_heading",     "default": "Roboto",
  "label": "Heading Font",
  "option_group": { "id": "font_families", "label": "Heading",     "value": "var(--ff-heading)" } },
{ "type": "font_picker", "id": "font_family_accent",      "default": "Roboto",
  "label": "Accent Font",
  "option_group": { "id": "font_families", "label": "Accent",      "value": "var(--ff-accent)" } },
{ "type": "font_picker", "id": "font_family_italic",      "default": "Playfair Display",
  "label": "Italic / Serif Font",
  "option_group": { "id": "font_families", "label": "Italic",      "value": "var(--ff-italic)" } },
{ "type": "font_picker", "id": "font_family_handwriting", "default": "Caveat",
  "label": "Handwriting Font",
  "option_group": { "id": "font_families", "label": "Handwriting", "value": "var(--ff-handwriting)" } }
```

Without the `option_group`, any section setting with `"options": "background_colors"` or `"options": "font_families"` shows an empty dropdown.

### theme.liquid — Wire CSS variables

Add all 12 colors and 5 fonts to `:root` in the `{% style %}` block:

```liquid
--clr-primary:   {{ settings.color_primary }};
--clr-secondary: {{ settings.color_secondary }};
--clr-accent:    {{ settings.color_accent   | default: '#FF5722' }};
--clr-white:     {{ settings.color_white    | default: '#FFFFFF' }};
--clr-light:     {{ settings.color_light    | default: '#FAFAFA' }};
--clr-gray:      {{ settings.color_gray     | default: '#F2F2F2' }};
--clr-muted:     {{ settings.color_muted    | default: '#9CA3AF' }};
--clr-dark:      {{ settings.color_dark     | default: '#111827' }};
--clr-black:     {{ settings.color_black    | default: '#000000' }};
--clr-body:      {{ settings.color_body     | default: '#1F2937' }};
--clr-success:   {{ settings.color_success  | default: '#10B981' }};
--clr-warning:   {{ settings.color_warning  | default: '#F59E0B' }};

--ff-body:        {{ settings.font_family_body        | font_family | default: "system-ui, sans-serif" }};
--ff-heading:     {{ settings.font_family_heading     | font_family | default: "system-ui, sans-serif" }};
--ff-accent:      {{ settings.font_family_accent      | font_family | default: "system-ui, sans-serif" }};
--ff-italic:      {{ settings.font_family_italic      | font_family | default: "'Playfair Display', Georgia, serif" }};
--ff-handwriting: {{ settings.font_family_handwriting | font_family | default: "'Caveat', cursive" }};
```

Sections reference these as `var(--clr-primary)` / `var(--ff-heading)` — theme config is the single source of truth.

---

## Fluid Theme Architecture

### Directory structure
```
your-theme/
├── layouts/theme.liquid              # Global wrapper (nav + content + footer)
├── home_page/default/index.liquid    # Homepage template
├── navbar/default/index.liquid       # Navbar template
├── footer/default/index.liquid       # Footer template
├── library_navbar/default/index.liquid # Library navbar template
├── page/<slug>/index.liquid          # Static page templates
├── page/schema-reference/index.liquid # Live reference for all schema controls
├── product/<slug>/index.liquid       # Product page templates
├── collection/<slug>/index.liquid    # Collection page templates
├── category/<slug>/index.liquid      # Category page templates
├── post/<slug>/index.liquid          # Blog post listing templates
├── post_page/<slug>/index.liquid     # Blog post detail templates
├── cart_page/default/index.liquid    # Cart page
├── shop_page/default/index.liquid    # Shop page
├── enrollment_pack/default/index.liquid # Enrollment pack page
├── join_page/default/index.liquid    # Join page
├── library/default/index.liquid      # Media library page
├── medium/default/index.liquid       # Single media page
├── sections/
│   ├── main_navbar/index.liquid      # Global navigation
│   ├── main_footer/index.liquid      # Global footer
│   ├── main_product/index.liquid     # DO NOT MODIFY — Fluid's built-in
│   ├── schema_reference/index.liquid # Live schema controls reference
│   └── exact-<prefix>-*/index.liquid # Your cloned sections
├── components/                       # Developer partials (no schema)
├── blocks/                           # Standalone reusable blocks (optional)
├── locales/                          # Translation files
├── config/
│   ├── settings_schema.json          # Theme setting definitions
│   └── settings_data.json            # Current setting values
└── assets/                           # CSS + JS served via | asset_url
```

18 required templates: `navbar`, `footer`, `home_page`, `category_page`, `category`, `collection`, `collection_page`, `shop_page`, `product`, `post`, `post_page`, `cart_page`, `page`, `enrollment_pack`, `join_page`, `library`, `library_navbar`, `medium`.

### Schema Controls Reference page — canonical control vocabulary

A live, browsable reference of every schema control lives at `page/schema-reference/index.liquid` + `sections/schema_reference/index.liquid`. After pushing the theme, visit `/pages/schema-reference` on your Fluid store.

**Agents: this page is the single source of truth for control types.** Before writing or modifying a section schema:

1. Decide what kind of value you need (text / number / color / media / resource / layout).
2. Open `base-theme/sections/schema_reference/index.liquid` and find the card for that control type. Each card has:
   - How it renders in the Fluid builder (so you can match editor expectations)
   - The exact schema snippet to copy
   - The exact Liquid accessor snippet to copy
3. If unsure — especially around `color` vs theme-color dropdowns, or resource pickers — stop and ask the user. Do **not** guess control names. Unsupported types (`number`, `article`, `video_url`, `inline_richtext`, etc.) break the editor silently.

**Key patterns this page encodes:**
- `richtext` for all visible copy (never `text`/`textarea`)
- `range` for numeric inputs (never `number`)
- `select + "options": "background_colors"` for theme-aware colors (never raw `color`)
- Singular resource pickers return an OBJECT in Fluid (not an ID) — access via `.title`/`.url`/etc.
- List resource pickers cap at 24 items

When you update [references/schema-settings-reference.md](references/schema-settings-reference.md), also update the corresponding card in the live reference page so the two stay in sync.

### layouts/theme.liquid
```liquid
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {{ content_for_header }}
</head>
<body>
  {% section 'main_navbar' %}
  <main>
    {% content_for_layout %}
  </main>
  {% section 'main_footer' %}
</body>
</html>
```

### DO NOT REPLACE
| Section | Why |
|---------|-----|
| `sections/main_product` | Wired to Fluid's product object (name, price, variants, add-to-cart) |
| Cart templates | Fluid-controlled |
| Checkout | Fluid-controlled |

### Fluid Liquid objects
```liquid
{{ product.name }}
{{ product.price | money }}
{{ product.description }}
{{ product.images }}
{{ company.name }}
{{ company.logo_url }}
{{ 'key' | t }}
{{ image.url | img_url: '600x400' }}
```

---

## Related Skills

- [fluid-theme-refine](../fluid-theme-refine/SKILL.md) — Pixel-perfect QA pass after clone. Canonical source of truth for Section Shell + Container patterns, divider-block pattern, canonical block primacy, media_picker fallback, and template-destroy preset refresh workflow.
- [fluid-product-admin-import](../fluid-product-admin-import/SKILL.md) — For importing products, categories, and admin settings (run before theme clone)
- [fluid-onboarding-prefill](../fluid-onboarding-prefill/SKILL.md) — For pre-filling KYC/onboarding forms
