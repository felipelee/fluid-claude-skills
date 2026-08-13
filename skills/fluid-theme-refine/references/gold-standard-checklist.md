# Gold-Standard Section Refinement — Field Notes

Condensed checklist of every mistake we caught refining sections on cloned themes, with the fix. Run this in order on any ported section before marking it done. Each item below is a REAL bug we hit — not a theoretical concern.

---

## 1. Section Shell + Container contract (6 + 9 settings)

Every custom section MUST ship these **15 settings** — no abbreviating, no omissions.

### Section Shell (6) — the outer colored box
```json
{ "type": "padding",        "id": "section_padding",        "label": "Section Padding" },
{ "type": "corner_radius",  "id": "section_border_radius",  "label": "Section Border Radius" },
{ "type": "select",         "id": "background_color",       "label": "Background Color", "options": "background_colors", "default": "transparent" },
{ "type": "image_picker",   "id": "background_image",       "label": "Background Image" },
{ "type": "range",          "id": "section_border_width",   "label": "Section Border Width", "min": 0, "max": 10, "step": 1, "default": 0, "unit": "px" },
{ "type": "select",         "id": "section_border_color",   "label": "Section Border Color", "options": "background_colors", "default": "var(--clr-primary)" }
```

### Container (9) — inner content frame, NOT just a width wrapper
```json
{ "type": "select",        "id": "container_max_width", "default": "1280px", "options": [{"value":"1080px","label":"Comfy (1080px)"}, ...] },
{ "type": "padding",       "id": "container_padding",        "label": "Container Padding" },
{ "type": "corner_radius", "id": "container_border_radius",  "label": "Container Border Radius" },
{ "type": "select",        "id": "container_background_color", ..., "default": "transparent" },
{ "type": "image_picker",  "id": "container_background_image" },
{ "type": "select",        "id": "container_overlay_color",  ..., "default": "transparent" },
{ "type": "range",         "id": "container_overlay_opacity", "min": 0, "max": 100, "step": 5, "default": 0, "unit": "%" },
{ "type": "range",         "id": "container_border_width",   "min": 0, "max": 10, "step": 1, "default": 0, "unit": "px" },
{ "type": "select",        "id": "container_border_color",   "default": "var(--clr-primary)" }
```

**❌ Common mistakes:**
- Putting `background_color` but no `container_background_color` (merchant can't color the inner card separately from the outer bleed).
- Using `section_padding_y_mobile` + `section_padding_y_desktop` as select fields with Tailwind values like `py-xl` / `lg:py-3xl` — breaks completely when you swap to CSS vars. Use `type: "padding"` which gives a 4-sided struct.
- Skipping `container_overlay_color` / `container_overlay_opacity` — this is what lets merchants put a semi-dark overlay on a hero bg image.
- Omitting `section_border_width` / `section_border_color` because "we don't use borders." Merchants might. Ship the full contract.

---

## 2. CSS wire-up — use the exact pattern from SKILL.md line 1002

```liquid
{%- style -%}
  /* --- Section Shell --- */
  .my-section.section-{{ section.id }} {
    background-color: {{ section.settings.background_color | default: 'transparent' }};
    {%- assign p = section.settings.section_padding -%}
    {%- if p -%}padding: {{ p.top | default: 80 }}px {{ p.right | default: 0 }}px {{ p.bottom | default: 80 }}px {{ p.left | default: 0 }}px;{%- else -%}padding: 80px 0;{%- endif -%}
    {%- assign r = section.settings.section_border_radius -%}
    {%- if r -%}border-radius: {{ r.tl }}px {{ r.tr }}px {{ r.br }}px {{ r.bl }}px;{%- endif -%}
    {% if section.settings.section_border_width > 0 %}border: {{ section.settings.section_border_width }}px solid {{ section.settings.section_border_color | default: 'var(--clr-primary)' }};{% endif %}
    {%- if section.settings.background_image != blank -%}
      background-image: url({{ section.settings.background_image | image_url: width: 2400 }});
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
    /* container_background_image, overlay, border, radius — same pattern */
  }
  {%- if section.settings.container_overlay_opacity > 0 -%}
    {%- assign _cov = section.settings.container_overlay_opacity | divided_by: 100.0 -%}
    .my-section.section-{{ section.id }} .my-section__container::before {
      content: ""; position: absolute; inset: 0;
      background: {{ section.settings.container_overlay_color | default: 'var(--clr-primary)' }};
      opacity: {{ _cov }}; pointer-events: none; z-index: 1;
    }
  {%- endif -%}
  .my-section.section-{{ section.id }} .my-section__container > * { position: relative; z-index: 2; }
{%- endstyle -%}
```

**❌ Bug we hit:** `class="my-section section-"` — forgot the `{{ section.id }}` interpolation. All scoped CSS breaks because the class literal is `section-` (no id). Grep: `class="[^"]*section-"[^{]` → should always be `section-{{ section.id }}"`.

---

## 3. Scoped-CSS self-check

Before pushing, grep for:
```bash
grep -n 'class="[^"]*section-"' sections/*/index.liquid
```
If it returns anything, you forgot the `{{ section.id }}` interpolation — the scoped CSS rules won't apply.

---

## 4. URL-string guards on EVERY image setting

Fluid's `image_url` filter assumes the value is a Fluid media record. If the value is a raw URL (passed from a preset or template), it will double-encode and break the image.

Every section that has an `image_picker` AND might receive a URL string (via preset defaults, template overrides, or JSON imports) needs both field types:

```liquid
{%- assign _bg_url = '' -%}
{%- if section.settings.background_image_url != blank -%}
  {%- assign _bg_url = section.settings.background_image_url -%}
{%- elsif section.settings.background_image != blank -%}
  {%- assign _bg_raw = section.settings.background_image -%}
  {%- if _bg_raw contains '://' -%}
    {%- assign _bg_url = _bg_raw -%}
  {%- else -%}
    {%- assign _bg_url = section.settings.background_image | image_url: width: 2400 -%}
  {%- endif -%}
{%- endif -%}
```

Schema:
```json
{ "type": "image_picker", "id": "background_image",     "label": "Background Image" },
{ "type": "text",         "id": "background_image_url", "label": "Background Image URL (overrides above)" }
```

**❌ Bug we hit:** Features-glassmorphism wouldn't accept URL strings in presets because `image_picker` requires a Fluid media record. Solution: parallel `text` field that overrides.

---

## 5. CSS-var defense on EVERY color dropdown

Option_groups return CSS var strings (`var(--clr-primary)`). But merchants might save a Tailwind class name like `bg-white` by mistake, or the theme might have a stale option. **Every color setting** needs a guard:

```liquid
{%- assign _bg = section.settings.background_color | default: 'transparent' -%}
{%- unless _bg contains 'var(' or _bg contains '#' or _bg contains 'rgb' or _bg == 'transparent' -%}
  {%- assign _bg = 'transparent' -%}
{%- endunless -%}
background-color: {{ _bg }};
```

**❌ Bug we hit:** Bottom cards rendering with no background because `class="bottom-card {{ block.settings.background_color }}"` was concatenating the class literal `var(--clr-dark)` into the HTML. Fixed by rewriting to inline `style="background-color: {{ _bg }};"` with the guard.

---

## 6. DO NOT use `class=""` concatenation for dynamic colors

**❌ Wrong:**
```liquid
<div class="card {{ block.settings.bg_color }}">
```
Because `bg_color` is `var(--clr-primary)` (from option_group), you get `class="card var(--clr-primary)"` — a garbage class name.

**✅ Right:**
```liquid
<div class="card" style="background-color: {{ _bg_with_guard }};">
```

---

## 7. Text content → richtext BLOCKS, not section settings

**❌ Legacy pattern (breaks merchant editing):**
```json
"settings": [
  { "type": "text", "id": "heading", "label": "Heading", "default": "Shop now" }
]
```
Merchant can't bold/italic, can't change color, can't reorder.

**✅ Gold standard — canonical richtext block:**
```json
"blocks": [
  { "type": "heading", "name": "Heading",
    "settings": [
      { "type": "richtext", "id": "text",
        "default": "<h2 style=\"color: var(--clr-primary); font-size: clamp(32px, 4.5vw, 56px); font-weight: 400; line-height: 1.15; letter-spacing: -0.015em;\">Shop now</h2>" }
    ]
  }
]
```

Apply to: eyebrow / heading / subhead / description / paragraph / any display text. Inline `style=""` in the default gives proper first-paint; merchant can override via WYSIWYG.

---

## 8. CRITICAL — Template schema does NOT contain `blocks`

**❌ This breaks `fluid_attributes` bindings and Layers editing:**
```liquid
{% schema %}
{
  "sections": {
    "my_hero": {
      "type": "hero",
      "settings": { ... },
      "blocks": { "b1": { "type": "heading", "settings": { ... } } },
      "block_order": ["b1"]
    }
  }
}
{% endschema %}
```

**✅ Correct:** template just references sections, presets populate blocks:
```liquid
{% schema %}
{
  "name": "about-us",
  "sections": {
    "my_hero": { "type": "hero", "settings": { "container_background_image_url": "..." } }
  }
}
{% endschema %}
```

Blocks come from the section's `presets[0].blocks` array. **Section-level `settings` overrides ARE allowed** in the template schema — that's how you pass DAM URLs for the hero bg image, video URL, etc. without hand-editing each section instance.

### Symptom: editor Layers panel shows section but no children under "Add block"
→ Template has `"blocks": { ... }` in its schema. Strip it. Let presets do their job.

---

## 9. Presets only fire on FRESH template creation

Editing `presets` in a section schema won't backfill existing template instances. To re-fire:

1. `DELETE /api/application_theme_templates/{id}` (destroys the template record)
2. `POST /api/application_theme_templates` with `name`, `themeable_type`, `application_theme_id`, `content`

The new template gets a fresh ID, presets run, blocks get materialized with `fluid_attributes`.

---

## 10. Color dropdowns populate inline, not via option_group strings

**❌ Symptom:** dropdowns in visual editor show as empty select boxes even though theme has `color_background` settings registered.

**Why it happens:** `"options": "background_colors"` is supposed to resolve via the theme's `option_groups: [{ id: "background_colors", ... }]` cross-refs, but in some theme versions or visual editor builds, this cross-reference doesn't resolve in time for the dropdown render.

**✅ Reliable fix — inline the options array explicitly:**
```json
"options": [
  { "value": "transparent", "label": "Transparent" },
  { "value": "var(--clr-white)", "label": "White" },
  { "value": "var(--clr-light)", "label": "Light" },
  { "value": "var(--clr-gray)", "label": "Gray" },
  { "value": "var(--clr-muted)", "label": "Muted" },
  { "value": "var(--clr-dark)", "label": "Dark" },
  { "value": "var(--clr-black)", "label": "Black" },
  { "value": "var(--clr-primary)", "label": "Primary" },
  { "value": "var(--clr-secondary)", "label": "Secondary" },
  { "value": "var(--clr-accent)", "label": "Accent" },
  { "value": "var(--clr-body)", "label": "Body" },
  { "value": "var(--clr-success)", "label": "Success" },
  { "value": "var(--clr-warning)", "label": "Warning" }
]
```

Keep the values as CSS vars (they resolve at render) so palette swaps still work. Same for `font_families` — inline an explicit array with `var(--ff-heading)`, `var(--ff-body)`, `var(--ff-accent)`, `var(--ff-italic)`, `var(--ff-handwriting)`.

---

## 10b. Grid-style sections — every repeating item is its own BLOCK

If a section renders a grid/row/carousel of repeating things (feature cards, testimonials, press logos, stat cards, ingredient tiles, team members, etc.), each one must be its own block type. Don't hard-code 3 or 4 cards into the section markup. Don't put the cards inside one "content" block. Each card = one block.

**Why:** merchants need to add/remove/reorder cards in the Layers panel without touching code. If card 5 is baked into markup, they can't have 6 cards without a dev.

**Canonical card/feature block contract:**
```
1.  icon / image     — image_picker (with URL text fallback)
2.  image_url        — text (URL-string fallback)
3.  alt              — text
4.  aspect_ratio     — select (if image is primary)
5.  fit              — radio (cover/contain)
6.  object_position  — select (center/top/bottom)
7.  title            — richtext (NOT text — merchants will format)
8.  description      — richtext
9.  link             — url (optional, makes card clickable)
10. background_color — select → inline colors
11. text_color       — select → inline colors
12. padding          — padding struct
13. border_radius    — corner_radius
14. border_width     — range
15. border_color     — select → inline colors
```

**❌ Wrong (baked into markup):**
```liquid
<div class="grid">
  <div class="card">
    <img src="{{ section.settings.card_1_image }}">
    <h3>{{ section.settings.card_1_title }}</h3>
    <p>{{ section.settings.card_1_description }}</p>
  </div>
  <div class="card">
    <img src="{{ section.settings.card_2_image }}">
    ...
  </div>
</div>
```

**✅ Right (block-based iteration):**
```liquid
<div class="grid">
  {% for block in section.blocks %}
    {% if block.type == 'card' %}
      <div class="card" {{ block.fluid_attributes }}>
        ...render block.settings.image / title / description / link...
      </div>
    {% endif %}
  {% endfor %}
</div>
```

Presets populate the initial N cards; merchants can add block 5, 6, 7+ in the editor.

Apply this to:
- feature grids (science-features, feature-image-grid, hover-cards-grid)
- testimonial/review carousels (customer-reviews-2, section-reviews-compact-scroll)
- stat grids (section-about-stats-quote already does this)
- press logo bars (press-logo-bar, as-seen-in already does this)
- team/advisor grids (team, science-advisory-board)
- ingredient tiles (ingredients-carousel, ingredients-details)

---

## 11. Canonical block contracts — ship the FULL setting list

### Canonical `button` block — 12 settings
```
1.  text              — text
2.  link              — url
3.  open_new_tab      — checkbox
4.  style             — radio (filled/outline/text)
5.  font_family       — select → font_families
6.  font_size         — range px (10–32)
7.  padding           — padding struct
8.  background_color  — select → background_colors
9.  text_color        — select → background_colors
10. border_width      — range px (0–10)
11. border_color      — select → background_colors
12. border_radius     — corner_radius struct
```

Render:
```liquid
<a href="{{ link }}"
   class="btn btn--{{ style }}"
   style="padding: ...; background: ...; color: ...; border: ...; border-radius: ...; font-size: ...px; font-family: ...; font-weight: 600; text-transform: uppercase; letter-spacing: 0.2em;"
   {% if open_new_tab %}target="_blank" rel="noopener"{% endif %}
   {{ block.fluid_attributes }}>
  {{ text }}
</a>
```

### Canonical `image` block — 10 settings
```
1.  image            — image_picker
2.  image_url        — text (URL-string fallback)
3.  alt              — text
4.  aspect_ratio     — select (auto/1:1/4:5/3:4/4:3/16:9)
5.  fit              — radio (cover/contain)
6.  object_position  — select (center/top/bottom)
7.  overlay_color    — select → background_colors
8.  overlay_opacity  — range 0–100%
9.  border_radius    — corner_radius
10. border_width     — range
11. border_color     — select → background_colors
```

Render: **always wrap in `<div class="media-wrap" {{ block.fluid_attributes }}>`** even when image is blank. Placeholder renders inside the wrap, not as a separate branch.

### Canonical richtext text block — 1 setting
```
1. text — richtext (with styled HTML default)
```
Default must include inline `style="color/font-family/font-size/line-height"` — first paint needs to look intentional.

### Canonical `card` / icon-card block — 7 settings
```
1. icon             — image_picker
2. text             — richtext
3. link             — url
4. background_color — select → background_colors
5. text_color       — select → background_colors
6. padding          — padding
7. border_radius    — corner_radius
```

**Enforcement rule:** before pushing, grep each section for every canonical block type and count settings. If `"type": "button"` has <12 settings (plus section-specific extras), expand it.

---

## 12. `fluid_attributes` on every section + every block

Every rendered section AND every rendered block needs `{{ section.fluid_attributes }}` / `{{ block.fluid_attributes }}` for the editor to wire up selection, deletion, drag-and-drop.

```liquid
<section class="my-section section-{{ section.id }}" {{ section.fluid_attributes }}>
  <div class="my-section__container">
    {% for block in section.blocks %}
      <div class="my-block block--{{ block.type }}" {{ block.fluid_attributes }}>
        ...
      </div>
    {% endfor %}
  </div>
</section>
```

**❌ Bug we hit:** blocks not clickable/deletable in Layers tree because the outer wrapper was a `<span>` without `fluid_attributes`.

---

## 13. No hardcoded hex — everything through CSS vars

Grep for hex in section files:
```bash
grep -nE '#[0-9A-Fa-f]{3,8}\b' sections/*/index.liquid
```
Expected hits: only inside fallback strings like `'rgba(0,0,0,0.08)'`, `'#F5F5F5'` as fallback after `var(...)`, and hardcoded overlay dims like `rgba(0,0,0,0.25)` (never-changing semantic).

Everything else: route through `var(--clr-primary)`, `var(--clr-white)`, `var(--ff-heading)`, etc.

---

## 14. Legacy Tailwind class settings — DELETE THEM

**❌ Pattern to kill on sight:**
```json
{ "type": "select", "id": "eyebrow_font_size", "options": "font_sizes", "default": "text-xs" }
{ "type": "select", "id": "background_color", "default": "bg-white" }
{ "type": "select", "id": "section_padding_y_mobile", "options": "padding_y_mobile", "default": "py-2xl" }
```

These are Shopify-era patterns. They inject class-name strings that DON'T work with CSS-var colors and can't be swapped out. Replace with:
- Font sizing → `font-size: clamp(Xpx, Yvw, Zpx)` inline in the richtext default
- Backgrounds → `select` with inline color options array (section #10)
- Padding → `"type": "padding"` (4-sided struct), read as `{{ p.top }}px {{ p.right }}px ...`

---

## 15. Migrate legacy co-located `styles.css` into `assets/`

Co-located stylesheets — `sections/{name}/styles.css`, `components/{name}/styles.css`, `{page_type}/{variant}/styles.css` — **are deprecated**. All CSS lives under `assets/`. Leaving one in place means it can still re-inject rules that conflict with whatever you just wrote.

**Do not "blank out" the file by PUTting empty content.** That leaves a deprecated resource on the theme, and once the company has the `STYLESHEET_STRICT_INPUT` flag on, any push carrying that shape is rejected with a 422. Move the bytes and delete the file.

**Fix — per section:**

1. Move the CSS to `assets/{section_name}.css` (flat — `assets/` has no sub-folders). Move it **byte-for-byte**; refactoring the CSS at the same time makes the change unreviewable.
2. Reference it from the top of `{name}/index.liquid` — never append after `{% endschema %}`, which is dead space:
   - **> 2 KB** → external, cacheable: `{{ 'hero_section.css' | asset_url | stylesheet_tag }}`
   - **≤ 2 KB** → inline critical CSS: `{{ 'hero_section.css' | inline_asset_content }}`
   - Check with `wc -c < sections/{name}/styles.css`. The 2 KB threshold is what the backend's own auto-migration used — matching it keeps us consistent with already-migrated themes.
3. Delete the old co-located file.
4. Re-run `fluid theme lint --json` and confirm clean.

**Keep `{%- style -%}` only for genuinely dynamic CSS** — per-section values that depend on schema settings. Static base rules belong in the asset; leave only the setting-driven overrides inline:

```liquid
{{ 'hero_section.css' | asset_url | stylesheet_tag }}
<style>
  .hero[data-section-id="{{ section.id }}"] {
    --section-bg:  {{ section.settings.bg_color }};
    --section-pad: {{ section.settings.section_pad }};
  }
</style>
```

Rule of thumb: an inline `<style>` over ~10 lines, or an inline `<script>` over ~5, should be an asset.

**Careful with leftovers.** If a section's `index.liquid` *already* references an `assets/*.css` and a co-located `styles.css` is still sitting next to it, do not delete blindly — someone may have edited the stale file after the migration. Diff the two; if identical, delete the leftover. If they differ, show the user and ask which to keep.

Theme-root `styles.css` / `global_styles.css` are a different case with fixed filenames and always-inline emission — see [SKILL.md → Fluid Engine Quirks](../SKILL.md#headings-render-at-body-text-size-no-visual-hierarchy).

---

## 16. Responsive breakpoints — 991px / 767px only

SKILL.md enforces `991px` (tablet) and `767px` (mobile) as the canonical breakpoints. Never use `749px`, `768px`, `1023px`, `1024px` (those are Shopify-era). For desktop overrides, `min-width: 1024px` is OK since that's modern-convention desktop; just don't mix `1023` and `1024` in the same section.

---

## 17. Final visual diff — pixel-match source with JS

After refinement, run this against the source site to extract computed values, then match in your section CSS:

```javascript
var el = document.querySelector('.hero-section h1');
var s = getComputedStyle(el);
JSON.stringify({
  color: s.color, fontSize: s.fontSize, fontWeight: s.fontWeight,
  fontFamily: s.fontFamily, lineHeight: s.lineHeight,
  letterSpacing: s.letterSpacing, textTransform: s.textTransform,
  margin: s.margin, padding: s.padding
}, null, 2);
```

Compare vs. target. Any drift → update the richtext default inline style, push, delete+recreate the template to re-fire preset expansion.

---

## The order to do refinement in

When refactoring a ported section from scratch:

1. **Read source measurements** (section 17) — get exact `font-size`, `line-height`, `letter-spacing`, grid dims
2. **Write the new schema** with full 6+9 Section Shell + Container + canonical blocks + inline color options arrays
3. **Write the new liquid** with:
   - `class="my-section section-{{ section.id }}"` (not `section-`)
   - `{%- style -%}` block at top with full scoped CSS
   - URL-string guards on every image
   - CSS-var guards on every color
   - `{{ section.fluid_attributes }}` + `{{ block.fluid_attributes }}` everywhere
4. **Define richtext blocks** for every text element with styled-HTML defaults matching source pixel values
5. **Define preset** that lists the canonical default blocks (don't put blocks in template schema)
6. **Push section files** via `PUT /api/application_themes/{id}/resources`
7. **Delete + POST template** to fire fresh preset expansion
8. **Load visual editor** and verify:
   - Sections render with scoped styles
   - Layers panel shows editable blocks under each section
   - Color dropdowns populate with 13 theme colors
   - Max Width / Container dropdowns populate
   - Hero bg, video poster, etc. flow from section-level settings overrides

If any check fails, go back to the matching rule above.

---

## Template recreation API sequence

```python
import json, urllib.request
TOKEN = "PT-..."

# 1. Delete old template
urllib.request.urlopen(urllib.request.Request(
    f"https://{shop}.fluid.app/api/application_theme_templates/{old_id}",
    method='DELETE', headers={"Authorization": f"Bearer {TOKEN}"}
))

# 2. PUT updated section files first
for key, fn in sections_to_push:
    body = json.dumps({"key": key, "content": open(fn).read()}).encode()
    urllib.request.urlopen(urllib.request.Request(
        f"https://{shop}.fluid.app/api/application_themes/{theme_id}/resources",
        data=body, method='PUT',
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    ))

# 3. POST fresh template — triggers preset expansion
body = json.dumps({
    "application_theme_id": theme_id,
    "application_theme_template": {
        "name": "about-us",            # must be slug-like, matches URL
        "themeable_type": "page",      # or "home_page", "product", etc.
        "content": open("template.liquid").read()
    }
}).encode()
res = urllib.request.urlopen(urllib.request.Request(
    f"https://{shop}.fluid.app/api/application_theme_templates",
    data=body, method='POST',
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
))
print("new id:", json.loads(res.read())['application_theme_template']['id'])
```
