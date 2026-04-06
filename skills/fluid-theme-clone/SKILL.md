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
  version: 3.0.0
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
```
sections/exact-<SITE_PREFIX>-<section-name>/index.liquid
```

### Gold Standard Section Architecture

Every section MUST follow these rules. Violating any of them breaks the Fluid visual editor.

#### Content = Blocks, Layout = Settings

- **Section settings** are for layout ONLY: `padding` (native type), `corner_radius` (native type), `background_color` (select with `"options": "background_colors"`)
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

#### Images — Dual Picker Pattern

Use BOTH `image_picker` and `url` for backwards compatibility:
```json
{ "type": "image_picker", "id": "image", "label": "Image (Upload)" },
{ "type": "url", "id": "image_url", "label": "Image URL", "info": "Alternative: paste URL directly" }
```
Render: `<img src="{{ block.settings.image_url | default: block.settings.image }}">`

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

Read [references/section-template.md](references/section-template.md) for the full section boilerplate.
Read [references/schema-settings-reference.md](references/schema-settings-reference.md) for all setting types.
Read [references/css-js-patterns.md](references/css-js-patterns.md) for CSS/JS patterns.

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

Extract fonts and colors from the source site and set them as current values:

```json
{
  "current": {
    "color_primary": "#023026",
    "color_secondary": "#023026",
    "color_accent": "#fc6f39",
    "color_cream": "#FAF8F1",
    "font_family_body": "Inter",
    "font_family_heading": "Spartan",
    "font_size_h1": 60,
    "font_size_h2": 48,
    "font_size_h3": 32
  }
}
```

### settings_schema.json — Add option_groups for color dropdowns

Every color setting needs an `option_group` so sections can reference them in select dropdowns:

```json
{
  "type": "color_background",
  "id": "color_primary",
  "label": "Primary Color",
  "default": "#023026",
  "option_group": { "id": "background_colors", "label": "Primary", "value": "var(--clr-primary)" }
}
```

Without the `option_group`, any section setting with `"options": "background_colors"` will show an empty dropdown.

### theme.liquid — Wire CSS variables

Add all color and spacing variables to `:root` in the `{% style %}` block:

```liquid
--clr-primary: {{ settings.color_primary | default: '#023026' }};
--clr-accent: {{ settings.color_accent | default: '#fc6f39' }};
--clr-cream: {{ settings.color_cream | default: '#FAF8F1' }};
--clr-heading: {{ settings.color_primary | default: '#023026' }};
```

Sections reference these as `var(--clr-primary)` — the theme config is the single source of truth.

---

## Fluid Theme Architecture

### Directory structure
```
your-theme/
├── layouts/theme.liquid              # Global wrapper (nav + content + footer)
├── home_page/default/index.liquid    # Homepage template
├── page/<slug>/index.liquid          # Static page templates
├── product/<slug>/index.liquid       # Product page templates
├── collection/<slug>/index.liquid    # Collection page templates
├── sections/
│   ├── main_navbar/index.liquid      # Global navigation
│   ├── main_footer/index.liquid      # Global footer
│   ├── main_product/index.liquid     # DO NOT MODIFY — Fluid's built-in
│   └── exact-<prefix>-*/index.liquid # Your cloned sections
├── config/
│   ├── settings_schema.json          # Theme setting definitions
│   └── settings_data.json            # Current setting values
└── assets/product.js
```

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

## Lessons from Rain International Clone (Session 2)

These lessons were learned the hard way during a full-site clone. Follow them to avoid the same mistakes.

### Splide.js in the Fluid Editor — Don't Use MutationObserver

When the Fluid visual editor saves, it unmounts and re-renders sections via React. This destroys Splide's DOM elements mid-lifecycle, causing `Cannot read properties of null` errors.

**What doesn't work:**
- `MutationObserver` to reinitialize Splide after editor saves — fires too early, before DOM is ready
- `try/catch` around `Splide.mount()` — catches errors but creates race conditions
- Complex reinitialization logic — makes things worse, not better

**What works:** Simple `DOMContentLoaded` listener. Accept that Splide breaks during editor saves — it reinitializes on page refresh. The live site (not the editor) always works correctly.

```javascript
document.addEventListener('DOMContentLoaded', function() {
  if (typeof Splide === 'undefined') return;
  var el = document.getElementById('my-carousel-{{ section.id }}');
  if (!el) return;
  new Splide(el, { /* config */ }).mount();
});
```

### CSS Animation Marquee > Splide for Tickers

For auto-scrolling ticker/marquee sections, **use pure CSS `@keyframes` animation** instead of Splide. Splide's autoScroll extension may not be loaded, and the fallback `autoplay` with fast intervals creates jerky movement.

```css
.marquee__inner {
  display: flex;
  width: max-content;
  animation: marquee-scroll 30s linear infinite;
}
@keyframes marquee-scroll {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
```

Duplicate the block content in HTML for seamless looping:
```liquid
{% for block in section.blocks %}
  <!-- original items -->
{% endfor %}
{% for block in section.blocks %}
  <!-- duplicate for seamless loop (aria-hidden="true") -->
{% endfor %}
```

### CSS Default Padding — Always Add to Root Class

The native `padding` type setting only works when the editor has saved data. For sections that haven't been saved yet, padding is zero. **Always add a CSS fallback on the root class:**

```css
.section-name {
  padding-top: 80px;
  padding-bottom: 80px;
}
```

The `{%- style -%}` block's padding wiring overrides this when the user adjusts values in the editor.

### Background Color Default — Use Cream Not Transparent

On the Rain site, almost every section has a warm cream background (`#FAF8F1`). Setting `default: "transparent"` makes sections white, which looks wrong.

**Set cream as default** for content sections:
```json
{ "type": "select", "id": "background_color", "options": "background_colors", "default": "var(--clr-cream)" }
```

**Keep dark green** for CTAs, marquees, and community sections.

### option_group on Color Settings — Required for Dropdowns

If sections reference `"options": "background_colors"` in a select setting, the color settings in `settings_schema.json` MUST have `option_group` defined:

```json
{
  "type": "color_background",
  "id": "color_primary",
  "default": "#023026",
  "option_group": { "id": "background_colors", "label": "Primary", "value": "var(--clr-primary)" }
}
```

Without this, the dropdown in the section settings panel shows empty.

### Product Images — Triple Fallback Chain

Fluid product images can be objects with `.src`, objects with `.url`, or raw URL strings. Always use a triple fallback:

```liquid
<img src="{{ image.src | default: image.url | default: image }}">
```

And resolve the image array with variant fallback:
```liquid
{% assign variant_imgs = product.selected_or_first_available_variant.images %}
{% if variant_imgs and variant_imgs.size > 0 %}
  {% assign images_array = variant_imgs %}
{% elsif product.images and product.images.size > 0 %}
  {% assign images_array = product.images %}
{% endif %}
```

**Never use `| parse_json`** on variant images — if they're already an array, it silently fails and returns nothing.

### Stacking Card Animations — Use Sticky with Care

For scroll-animated stacking cards (like the Nature & Science section):

```css
.card {
  position: sticky;
  top: 80px; /* increment per card: 80, 100, 120 */
  z-index: 1; /* increment per card */
  margin-bottom: 24px; /* small gap, NOT -200px overlap */
  border-radius: 16px;
  overflow: hidden;
}
```

**Don't use large negative margins** — they hide content. Use positive `margin-bottom` with small gaps. The sticky positioning creates the stacking effect naturally.

### Layered Image Compositions — Two-Image Pattern

For the "floating seeds over lifestyle photo" pattern used on multiple pages:

```html
<div class="image-group" style="position: relative; min-height: 500px;">
  <div class="lifestyle-wrap" style="position: relative; z-index: 1;">
    <img src="lifestyle.jpg" style="width: 85%; margin-left: auto; border-radius: 12px;">
  </div>
  <div class="scatter-wrap" style="position: absolute; bottom: -40px; left: -20px; z-index: 2; width: 65%;">
    <img src="seeds-cutout.png" style="width: 100%;">
  </div>
</div>
```

The scatter image is a transparent cutout (PNG/WebP) positioned absolutely to overlap the lifestyle photo.

### Contained Hero vs Full-Bleed Hero

The Rain homepage hero is NOT full-bleed — it's a video card **inside a max-width container**:

```html
<div class="hero-wrapper" {{ section.fluid_attributes }}>
  <div class="hero-container" style="max-width: 1280px; margin: 0 auto; padding: 0 var(--space-9xl, 64px);">
    <div class="hero-card" style="position: relative; min-height: 640px; overflow: hidden; border-radius: 0 0 16px 16px;">
      <!-- video, overlay, content -->
    </div>
  </div>
</div>
```

### Product Description — Read More Clamp

Long product descriptions should be clamped with a "Read more" toggle:

```css
.product-desc-clamp {
  display: -webkit-box;
  -webkit-line-clamp: 7;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.product-desc-clamp.is-expanded {
  -webkit-line-clamp: unset;
  display: block;
}
```

JS checks `scrollHeight > clientHeight` to show/hide the toggle button.

### Footer — Video Background Pattern

The Rain footer uses a background video with dark overlay:

```html
<video autoplay loop muted playsinline style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;">
  <source src="video.mp4" type="video/mp4">
</video>
<div class="overlay" style="position: absolute; inset: 0; background: var(--clr-dark-green); opacity: 0.55;"></div>
<div class="content" style="position: relative; z-index: 2;">
  <!-- footer content -->
</div>
```

Use `company.logo_url` for the logo and editable link/social blocks for footer links.

### Accordion Items — Use Individual Blocks

Never hardcode accordion items (like product Details/Shipping/Return). Make each item an `accordion_item` block so users can add, remove, and reorder:

```json
{
  "type": "accordion_item",
  "name": "Accordion Item",
  "settings": [
    { "type": "text", "id": "title", "default": "Section Title" },
    { "type": "richtext", "id": "content", "default": "<p>Content</p>" }
  ]
}
```

### sed Is Dangerous for Liquid Files

Never use `sed` to modify Liquid template files — the `{%`, `}}`, and pipe characters cause regex escaping nightmares. **Always use Python** for file modifications:

```python
with open(filepath, 'r') as f:
    content = f.read()
content = content.replace('old_string', 'new_string')
with open(filepath, 'w') as f:
    f.write(content)
```

One bad sed command corrupted 15 CSS selectors by merging padding values into class names — took hours to debug.

---

## Related Skills

- [fluid-product-admin-import](../fluid-product-admin-import/SKILL.md) — For importing products, categories, and admin settings (run before theme clone)
- [fluid-onboarding-prefill](../fluid-onboarding-prefill/SKILL.md) — For pre-filling KYC/onboarding forms
