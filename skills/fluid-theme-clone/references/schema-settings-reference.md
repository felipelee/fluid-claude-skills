# Schema Settings Reference

Complete reference of all supported schema setting types in Fluid. Mirrors the official Fluid Theme Dev docs (controls table in the repo README and `docs/11-settings-reference.md`).

Every control is set in a section or block schema via `{ "type": "<type>", "id": "<id>", "label": "<Label>", ... }`. Labels should use **Title Case**. `visible_if` works on any field.

---

## 🚫 NON-NEGOTIABLE RULES — Read first, every time

These rules are violated most often. Before you write any schema, internalize them.

### 1. Content images MUST be `blocks/image` — never `image_picker`

Any image the merchant can swap — a hero image, a card photo, an avatar, a logo, a step illustration, an ingredient shot, a "before"/"after" photo — **must be added as a canonical `image` block**. Not as a section-level `image_picker`. Not as an inline `image_picker` inside some other block's settings.

**ALLOWED uses of `image_picker`:**

| Location | Id (convention) | Purpose |
|----------|-----------------|---------|
| Section Shell | `background_image` | Decorative full-section background |
| Container | `container_background_image` | Decorative container background |
| Canonical `blocks/image` only | `image` | The single image control inside the canonical image block |
| Data-driven wrappers (`blocks/post_image`, etc.) | varies | Fallback when the resource's own image is blank |

**FORBIDDEN uses of `image_picker`:**

- As a section-level content image (e.g. `before_image`, `after_image`, `hero_image`, `logo_image`)
- As an image field inside a non-image block (e.g. `avatar` on a review card, `photo` on a testimonial, `logo_image` on a press card)
- As an "image override" on a product-picker block that isn't the canonical image block

**Why:** the canonical `image` block ships 7+ controls (aspect ratio, fit, object position, corner radius, border width/color, overlay) that every card/tile/hero needs. When you inline an `image_picker` directly, merchants lose all of those controls, can't duplicate the image independently, and the layout breaks the moment the design needs variation.

**When a section needs images per card** (review grid, testimonial grid, logo bar, step list, before/after, ingredient list), use the **divider block pattern**: one divider block type (e.g. `review`, `step`, `logo_item`) with no image field, plus canonical `image` block instances that render inside the current divider's scope via the stateful walk.

**Pre-push checklist:** grep your section for `"type": "image_picker"`. Every match must fall into one of the three ALLOWED rows above. If any match is a content image, convert it to a canonical `image` block.

### 2. Content fonts MUST come from `font_families` option group — never `font_picker`

`font_picker` only lives in `config/settings_schema.json`. Section-level font choices are `select` pointed at `font_families`, whose values are CSS variables (`var(--ff-heading)`, `var(--ff-italic)`, etc.).

### 3. Content colors MUST come from `background_colors` option group — never raw hex

Same reason as fonts. Section-level color choices are `select` pointed at `background_colors`, whose values are CSS variables (`var(--clr-primary)`, `transparent`, etc.).

### 4. Every section uses Section Shell + Container — no exceptions

Canonical structure (6 + 9 = 15 settings that every section ships):

**Section Shell (6 settings — always at the bottom of the settings array under a `{ "type": "header", "content": "Section Shell" }` header):**
- `padding` — id `section_padding`
- `corner_radius` — id `section_border_radius`
- `select` (background_colors) — id `background_color`
- `image_picker` — id `background_image`
- `range 0–10` — id `section_border_width`
- `select` (background_colors) — id `section_border_color`

**Container (9 settings — under a `{ "type": "header", "content": "Container" }` header, placed just before Section Shell):**
- `select` — id `container_max_width` (options: 1080px / 1280px / 1440px / 100%)
- `padding` — id `container_padding`
- `corner_radius` — id `container_border_radius`
- `select` (background_colors) — id `container_background_color`
- `image_picker` — id `container_background_image`
- `select` (background_colors) — id `container_overlay_color`
- `range 0–100%` — id `container_overlay_opacity`
- `range 0–10` — id `container_border_width`
- `select` (background_colors) — id `container_border_color`

**Implementation in Liquid:**

```liquid
.sec.section-{{ section.id }} {
  {%- assign p = section.settings.section_padding -%}
  {%- if p -%}padding: {{ p.top | default: 80 }}px 0 {{ p.bottom | default: 80 }}px 0;{%- else -%}padding: 80px 0;{%- endif -%}
  background-color: {{ section.settings.background_color | default: 'transparent' }};
}
.sec.section-{{ section.id }} .sec__container {
  max-width: {{ section.settings.container_max_width | default: '1280px' }};
  margin: 0 auto;
  padding: 0 64px;
}
```

Vertical padding on the shell keeps the background edge-to-edge. The container holds content at max-width. **Don't** put horizontal padding on the shell or you'll kill full-bleed backgrounds.

### 5. Hero intros use richtext BLOCKS — not section-level text fields

Every section with an intro (heading, eyebrow, subhead) exposes them as canonical `eyebrow`, `heading`, `subhead` blocks — each a single `richtext` setting with a styled default. Merchant can edit, add, remove, and reorder them independently. Never a single `{ "type": "text", "id": "heading" }` section setting for a visible title.

**Default richtext** ships with inline `style=""` so first-paint looks intentional:

```json
{ "type": "richtext", "id": "text", "label": "Text",
  "default": "<h2 style=\"color: var(--clr-primary); font-size: clamp(32px, 4.5vw, 56px); font-weight: 700; letter-spacing: -0.02em; line-height: 1.05;\">Default heading</h2>" }
```

### 6. `{% render %}` resolves ONLY from `components/` — never `blocks/`

`blocks/*` is a documentation folder for canonical block schemas. Fluid's render engine cannot find files there. If a section needs a shared markup chunk, put it in `components/` and render it from there. For canonical block schemas (like `blocks/cart_button`), **inline** the markup in the section file instead of rendering.

---

## Controls at a glance

### Input

| Type | Returns | Use for |
|------|---------|---------|
| `text` | String | Short single-line text |
| `textarea` | String | Multi-line plain text |
| `richtext` / `rich_text` | HTML string | Formatted rich text (WYSIWYG) |
| `html` / `html_textarea` | HTML string | Raw custom HTML |
| `url` | String | Single URL |

### Number & Selection

| Type | Returns | Use for |
|------|---------|---------|
| `range` | Number | Numeric slider — requires `min`, `max`, `step` |
| `select` | String | Dropdown (5+ choices) — requires `options` |
| `radio` | String | Tab buttons (2–4 choices) — requires `options` |
| `checkbox` | Boolean | Toggle switch |

### Visual & Media

| Type | Returns | Use for |
|------|---------|---------|
| `color` | Hex string | Solid color picker |
| `color_background` | Hex or gradient string | Solid color + gradient picker |
| `font_picker` | String | Font family selector |
| `image_picker` / `image` | Image object | Upload/select image — **only for section/container background or inside canonical `blocks/image`** (see rule 1 above) |
| `video_picker` | Video object | Upload/select video |
| `media_picker` | Media object | Image or video with embed settings |
| `text_alignment` | String (`left` \| `center` \| `right`) | Alignment buttons |

### Layout

| Type | Returns | Use for |
|------|---------|---------|
| `padding` | `{ top, bottom, left, right }` | Four-sided padding |
| `corner_radius` | `{ tl, tr, br, bl }` | Four-corner border radius |
| `border` | `{ width, color }` | Border width + color |
| `gradient_overlay` | `{ enabled, mode, colors, ... }` | Gradient / solid overlay |
| `media_fit` | String | Width/height/fit image sizing |

### Organization

| Type | Returns | Use for |
|------|---------|---------|
| `header` | (none) | Visual divider label — uses `content`, not `label` |

### Resource (Single)

| Type | Returns | Use for |
|------|---------|---------|
| `product` / `products` | Product object | Single product picker |
| `collection` / `collections` | Collection object | Single collection picker |
| `category` / `categories` | Category object | Single category picker |
| `blog` / `posts` | Post object | Single post picker |
| `enrollment_pack` / `enrollment` / `enrollments` | Enrollment object | Single enrollment picker |
| `forms` | Form object | Single form picker |
| `media` | Media object | Single media library resource |
| `link_list` | Linklist object | Navigation menu picker |

### Resource (List — max 24)

| Type | Returns | Use for |
|------|---------|---------|
| `product_list` / `products_list` | Array | Multi-product picker |
| `collection_list` / `collections_list` | Array | Multi-collection picker |
| `category_list` / `categories_list` | Array | Multi-category picker |
| `posts_list` | Array | Multi-post picker |
| `enrollment_list` / `enrollments_list` | Array | Multi-enrollment picker |

---

## Full examples

### Input

```json
{ "type": "text", "id": "heading", "label": "Section Heading", "default": "Welcome" }
{ "type": "textarea", "id": "caption", "label": "Caption", "default": "Short blurb." }
{ "type": "richtext", "id": "body", "label": "Body", "default": "<p>Rich copy.</p>" }
{ "type": "html", "id": "embed", "label": "Custom HTML" }
{ "type": "url", "id": "cta_url", "label": "CTA URL", "default": "https://example.com" }
```

**Access:**
```liquid
{{ section.settings.heading }}
{{ section.settings.body }}   {# already HTML — do NOT escape #}
{{ section.settings.caption | escape }}   {# escape plain text from users #}
```

### Number & Selection

```json
{ "type": "range", "id": "columns", "label": "Columns", "min": 1, "max": 6, "step": 1, "default": 3, "unit": "cols" }

{ "type": "select", "id": "layout", "label": "Layout", "default": "grid",
  "options": [
    { "value": "grid", "label": "Grid" },
    { "value": "list", "label": "List" },
    { "value": "carousel", "label": "Carousel" }
  ]
}

{ "type": "radio", "id": "size", "label": "Size", "default": "md",
  "options": [
    { "value": "sm", "label": "Small" },
    { "value": "md", "label": "Medium" },
    { "value": "lg", "label": "Large" }
  ]
}

{ "type": "checkbox", "id": "show_divider", "label": "Show Divider", "default": true }
```

> `number` is NOT supported — always use `range`.

### Visual & Media

```json
{ "type": "color", "id": "text_color", "label": "Text Color", "default": "#111" }
{ "type": "color_background", "id": "bg", "label": "Background", "default": "#fff" }
{ "type": "font_picker", "id": "heading_font", "label": "Heading Font", "default": "Inter" }

{ "type": "image_picker", "id": "background_image", "label": "Background Image" }   // ✅ decorative BG only
// ❌ DO NOT use image_picker for content images — add a canonical `image` block instead
// See "NON-NEGOTIABLE RULES → rule 1" at the top of this reference.
{ "type": "video_picker", "id": "demo_video", "label": "Demo Video" }
{ "type": "media_picker", "id": "hero_media", "label": "Hero Media" }

{ "type": "text_alignment", "id": "align", "label": "Alignment", "default": "center" }
```

**Access:**
```liquid
{{ section.settings.hero_image.url }}     {# image/video/media return an object #}
{{ section.settings.hero_image | img_url: '1200x' }}
```

### Background color — select with option group

For theme-aware backgrounds, prefer a `select` pointed at the `background_colors` option group declared in `config/settings_schema.json`:

```json
{ "type": "select", "id": "background_color", "label": "Background Color",
  "options": "background_colors", "default": "transparent" }
```

```liquid
background-color: {{ section.settings.background_color | default: 'transparent' }};
```

The option group values are already CSS values (`var(--clr-primary)`, `transparent`, etc.). Never wrap in `var(--clr-…)` again — that produces invalid CSS when empty and silently breaks the entire rule block.

### Layout

```json
{ "type": "padding", "id": "section_padding", "label": "Section Padding" }
{ "type": "corner_radius", "id": "section_border_radius", "label": "Section Border Radius" }
{ "type": "border", "id": "section_border", "label": "Section Border" }
{ "type": "gradient_overlay", "id": "overlay", "label": "Overlay" }
{ "type": "media_fit", "id": "image_fit", "label": "Image Fit" }
```

**Wiring `padding` + `corner_radius` in `{%- style -%}`:**
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

### Organization

```json
{ "type": "header", "content": "Typography Settings" }
```

`header` uses `content`, not `label`. Purely visual — renders no value.

### Resource (Single)

```json
{ "type": "product", "id": "featured_product", "label": "Featured Product" }
{ "type": "collection", "id": "featured_collection", "label": "Featured Collection" }
{ "type": "category", "id": "featured_category", "label": "Featured Category" }
{ "type": "post", "id": "featured_post", "label": "Featured Post" }
{ "type": "enrollment_pack", "id": "starter_pack", "label": "Starter Pack" }
{ "type": "forms", "id": "contact_form", "label": "Contact Form" }
{ "type": "media", "id": "library_asset", "label": "Media Library Asset" }
{ "type": "link_list", "id": "main_menu", "label": "Main Menu" }
```

**Access:** single resource pickers return an object (or an ID, depending on type — check `| json` in dev).
```liquid
{% for p in products %}
  {% if p.id == section.settings.featured_product %}
    <h3>{{ p.title }}</h3>
  {% endif %}
{% endfor %}
```

### Resource (List)

```json
{ "type": "product_list", "id": "grid_products", "label": "Products", "limit": 8 }
{ "type": "collection_list", "id": "grid_collections", "label": "Collections", "limit": 6 }
{ "type": "category_list", "id": "grid_categories", "label": "Categories", "limit": 6 }
{ "type": "posts_list", "id": "grid_posts", "label": "Posts", "limit": 6 }
{ "type": "enrollment_list", "id": "grid_enrollments", "label": "Enrollment Packs", "limit": 6 }
```

List pickers return the full array — iterate directly. Hard cap is 24.

```liquid
{% for product in section.settings.grid_products %}
  <a href="{{ product.url }}">{{ product.title }}</a>
{% endfor %}
```

---

## `visible_if`

Works on any field. Value is a Liquid expression — typically a reference to another setting.

```json
{ "type": "checkbox", "id": "show_overlay", "label": "Show Overlay", "default": false },
{ "type": "gradient_overlay", "id": "overlay", "label": "Overlay",
  "visible_if": "{{ section.settings.show_overlay }}" }
```

---

## Not supported — use alternatives

Using these types will error or silently fail in the editor:

| Unsupported | Use instead |
|-------------|-------------|
| `number` | `range` |
| `paragraph` | `header` (with `content`) |
| `inline_richtext` | `text` or `richtext` |
| `article` / `article_list` | `post` / `posts_list` |
| `video` / `video_url` | `video_picker` or `url` |
| `page` | — (not available) |
| `liquid` | — (cannot inject raw Liquid) |
| `color_scheme` / `color_scheme_group` | `color` (group manually) |
| `metaobject` / `metaobject_list` | — (not available) |

---

## Common schema conventions

- Labels use **Title Case** ("Section Padding", not "section padding")
- Every section schema has `name`, `settings`, `blocks`, `presets`
- Every block schema has `name`, `settings`
- Use `header` to visually group related settings
- Use `visible_if` for dependent settings
- Use `"limit": 1` on blocks that should appear at most once
- Use `"info"` to hint recommended sizes, formats, or examples
- Private blocks start with `_` (e.g., `_product-card`) and are excluded from the `@theme` wildcard

## Live reference

A live, browsable version of every control with rendered examples lives at `page/schema-reference/index.liquid` in the base theme. Push the theme and visit `/pages/schema-reference` on your Fluid store.
