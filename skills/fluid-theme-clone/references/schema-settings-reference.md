# Schema Settings Reference

Complete reference of all supported schema setting types in Fluid. Mirrors the official Fluid Theme Dev docs (controls table in the repo README and `docs/11-settings-reference.md`).

Every control is set in a section or block schema via `{ "type": "<type>", "id": "<id>", "label": "<Label>", ... }`. Labels should use **Title Case**. `visible_if` works on any field.

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
| `image_picker` / `image` | Image object | Upload/select image |
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

{ "type": "image_picker", "id": "hero_image", "label": "Hero Image" }
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
