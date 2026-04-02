# Page Templates Reference

## Template Locations by Page Type

| PAGE_TYPE | File Path |
|-----------|-----------|
| `home` | `home_page/default/index.liquid` |
| `page` | `page/<PAGE_SLUG>/index.liquid` |
| `product` | `product/<PAGE_SLUG>/index.liquid` |
| `collection` | `collection/<PAGE_SLUG>/index.liquid` |

---

## Standard Page Template (`page` type)

```liquid
{% layout 'theme' %}

{% comment %} Page: <SOURCE_URL> {% endcomment %}
{% comment %} Sections: <COUNT> {% endcomment %}

{% section 'exact-<prefix>-hero', id: 'hero' %}
{% section 'exact-<prefix>-content', id: 'content' %}
{% section 'exact-<prefix>-cta', id: 'cta' %}

{% schema %}
{
  "sections": {
    "hero": { "type": "exact-<prefix>-hero" },
    "content": { "type": "exact-<prefix>-content" },
    "cta": { "type": "exact-<prefix>-cta" }
  },
  "order": ["hero", "content", "cta"]
}
{% endschema %}
```

---

## Home Page Template (`home` type)

Update `home_page/default/index.liquid` with the same pattern as a standard page.

---

## Product Page Template (`product` type)

**Always include `main_product` first — never replace it.** It's wired to Fluid's product object.

```liquid
{% layout 'theme' %}

{% section 'main_product', id: 'product_main' %}
{% section 'exact-<prefix>-features', id: 'features' %}
{% section 'exact-<prefix>-ingredients', id: 'ingredients' %}
{% section 'exact-<prefix>-faq', id: 'faq' %}

<script src="{{ 'product.js' | asset_url }}" defer></script>

{% schema %}
{
  "sections": {
    "product_main": {
      "type": "main_product",
      "settings": {
        "background_color": "bg-white",
        "section_padding_y_mobile": "py-md",
        "section_padding_y_desktop": "lg:py-xl"
      }
    },
    "features": { "type": "exact-<prefix>-features" },
    "ingredients": { "type": "exact-<prefix>-ingredients" },
    "faq": { "type": "exact-<prefix>-faq" }
  },
  "order": ["product_main", "features", "ingredients", "faq"]
}
{% endschema %}
```

---

## Key Rules

1. `{% layout 'theme' %}` is **always line 1**
2. Each `{% section %}` call needs a **unique `id`**
3. The `{% schema %}` block maps each `id` to a section `type` and optional `settings`/`blocks` overrides
4. The `order` array controls the rendering order
5. Section settings in the template schema override the section's own defaults

---

## Reusing a Section Multiple Times

You can use the same section type multiple times with different settings by giving each instance a unique `id`:

```liquid
{% section 'exact-hiya-split-feature', id: 'feature_1' %}
{% section 'exact-hiya-split-feature', id: 'feature_2' %}
{% section 'exact-hiya-split-feature', id: 'feature_3' %}
```

Each has its own settings in the schema:

```json
{
  "sections": {
    "feature_1": {
      "type": "exact-hiya-split-feature",
      "settings": {
        "heading": "Made with Honest Ingredients",
        "bg_color": "#E8FAF0"
      }
    },
    "feature_2": {
      "type": "exact-hiya-split-feature",
      "settings": {
        "heading": "No Added Sugar",
        "bg_color": "#FFFFFF",
        "reverse_layout": true
      }
    },
    "feature_3": {
      "type": "exact-hiya-split-feature",
      "settings": {
        "heading": "Optimized for Freshness",
        "bg_color": "#E8FAF0"
      }
    }
  },
  "order": ["feature_1", "feature_2", "feature_3"]
}
```

---

## Template Schema vs Section Schema

**Template schema** (in the page template file):
- Defines which sections appear on the page
- Overrides section defaults with page-specific settings/blocks
- Controls section order

**Section schema** (in the section's `index.liquid`):
- Defines available settings and their types/defaults
- Defines available block types
- Defines presets for the editor

When a template includes a section:
1. Section schema defines what settings ARE POSSIBLE
2. Template schema provides the ACTUAL VALUES for this page
3. Template values override section defaults
