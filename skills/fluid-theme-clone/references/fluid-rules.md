# Fluid-Specific Rules

## DO NOT Replace

| Section | Why |
|---------|-----|
| `sections/main_product` | Wired to Fluid's product object (name, price, images, variants, add-to-cart). Clone styling AROUND it. |
| Cart functionality | Fluid-controlled. Don't touch `cart_page` templates. |
| Checkout | Fluid-controlled. Don't clone. |

---

## Theme Directory Structure

```
your-theme/
├── layouts/
│   └── theme.liquid              ← Global wrapper (nav + footer + content)
├── home_page/
│   └── default/index.liquid      ← Homepage template
├── page/
│   ├── about/index.liquid        ← Static page templates
│   └── [slug]/index.liquid
├── product/
│   └── [slug]/index.liquid       ← Product page templates
├── collection/
│   └── default/index.liquid      ← Collection page templates
├── sections/
│   ├── main_navbar/index.liquid  ← Global nav (in theme.liquid)
│   ├── main_footer/index.liquid  ← Global footer (in theme.liquid)
│   ├── main_product/index.liquid ← DO NOT REPLACE
│   └── exact-*/index.liquid      ← Cloned sections
├── config/
│   ├── settings_schema.json      ← Theme setting definitions
│   └── settings_data.json        ← Current theme setting values
└── assets/
    └── product.js, etc.
```

---

## Navigation & Footer

The global nav and footer live in:
- `sections/main_navbar/index.liquid`
- `sections/main_footer/index.liquid`

These are rendered by `layouts/theme.liquid` and appear on every page. Only modify if you are cloning the source site's nav/footer.

---

## Video Handling

| Type | Handling |
|------|----------|
| Self-hosted (`.mp4`, `.webm`) | Upload to DAM via `upload.fluid.app`. Use `asset.default_variant_url`. Add `create_media=true` for Media library visibility. |
| YouTube/Vimeo embeds | Keep original embed URLs. Add a `video_url` text setting. |
| Background videos | Use `autoplay`, `loop`, `muted`, `playsinline` attributes. Include poster image fallback. |

---

## Fluid Liquid Objects

Use these instead of hardcoded values where applicable:

```liquid
{{ product.name }}
{{ product.price | money }}
{{ product.description }}
{{ product.images }}
{{ cart.total | money }}
{{ cart.items }}
{{ company.name }}
{{ company.logo_url }}
{{ company.shop_page_url }}
{{ company.checkout_url }}
{{ 'key' | t }}                          {%- comment -%} Translations {%- endcomment -%}
{{ image.url | img_url: '600x400' }}     {%- comment -%} Product images {%- endcomment -%}
```

---

## Global Sections vs Template Sections

### Global Sections (in `theme.liquid`)
- Appear on EVERY page
- Defined once, shared data
- Examples: `main_navbar`, `main_footer`

### Template Sections (in templates)
- Page-specific
- Each template stores its own section settings
- Same section type can have different data per template

---

## Defensive Liquid Patterns

Always provide fallbacks:
```liquid
{{ company.name | default: 'Company' }}
```

Guard optional structures:
```liquid
{% if product and product.images %}
  <img src="{{ product.images[0].src }}" alt="{{ product.title | default: 'Product' }}">
{% endif %}
```

Use `section.blocks.size` to check if blocks exist:
```liquid
{% if section.blocks.size > 0 %}
  {% for block in section.blocks %}
    ...
  {% endfor %}
{% endif %}
```
