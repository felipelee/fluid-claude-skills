# Schema Settings Reference

Complete reference of all supported schema setting types in Fluid. Source: https://docs.fluid.app/docs/themes/schema-components

---

## Text Input Types

| Type | Description | Use Case | Example |
|------|-------------|----------|---------|
| `text` | Single-line text | Titles, labels, short text | Heading, button text |
| `textarea` | Multi-line plain text | Longer text without formatting | Descriptions, captions |
| `richtext` or `rich_text` | Rich text editor | Formatted content | About sections, long descriptions |
| `html` or `html_textarea` | Raw HTML input | Custom HTML code | Embeds, custom widgets |
| `url` | URL input with validation | Links, external resources | Button links, social links |

Example:
```json
{
  "type": "text",
  "id": "heading",
  "label": "Section Heading",
  "default": "Welcome to Our Store",
  "info": "This appears at the top of the section"
}
```

---

## Number & Selection Types

| Type | Description | Use Case | Example |
|------|-------------|----------|---------|
| `range` | Slider with min/max | Numeric settings with bounds | Font size, opacity, spacing |
| `select` | Dropdown menu | Predefined options | Font family, color scheme |
| `radio` | Radio buttons | Visual choice selection | Layout options |
| `checkbox` | Toggle on/off | Boolean settings | Show/hide elements |

**IMPORTANT: The `number` type is NOT supported. Use `range` instead for numeric inputs.**

Example (range):
```json
{
  "type": "range",
  "id": "font_size",
  "label": "Font Size",
  "min": 12,
  "max": 72,
  "step": 2,
  "default": 24,
  "unit": "px"
}
```

Example (select):
```json
{
  "type": "select",
  "id": "layout",
  "label": "Layout Style",
  "default": "grid",
  "options": [
    { "value": "grid", "label": "Grid" },
    { "value": "list", "label": "List" },
    { "value": "carousel", "label": "Carousel" }
  ]
}
```

---

## Visual & Media Types

| Type | Description | Use Case | Example |
|------|-------------|----------|---------|
| `color` | Color picker | Simple colors | Text color, background |
| `color_background` | Color with gradient support | Complex backgrounds | Hero backgrounds |
| `font_picker` | Font family selector | Typography | Heading fonts |
| `image` or `image_picker` | Image upload/select | Images | Logos, backgrounds, photos |
| `video_picker` | Video upload/select | Videos | Hero videos, product demos |

Example:
```json
{
  "type": "color",
  "id": "text_color",
  "label": "Text Color",
  "default": "#000000"
}
```

**Note for page cloning:** For exact clones, prefer `type: "text"` for image URLs (lets you paste DAM URLs directly) rather than `type: "image"` which uses Fluid's native picker.

---

## Resource Selector Types

### Single Resource Selectors

Select **one** item from the specified resource type:

| Type | Description | Returns |
|------|-------------|---------|
| `product` | Single product | Product ID (find from global `products` array) |
| `products` | Alias of `product` | Same |
| `collection` | Single collection | Collection ID (find from global `collections` array) |
| `collections` | Alias of `collection` | Same |
| `category` | Single category | Category ID |
| `categories` | Alias of `category` | Same |
| `post` | Single blog post | Post ID |
| `posts` | Alias of `post` | Same |
| `blog` | Single blog | Blog ID |
| `forms` | Single form | Form ID |
| `enrollment` | Single enrollment | Enrollment ID |
| `enrollments` | Alias of `enrollment` | Same |
| `enrollment_pack` | Single enrollment pack | Enrollment pack ID |

**Tip:** Singular/plural aliases both work for single selection (e.g., `product` and `products`).

**Important:** Resource selectors return IDs. You need to loop through the global array to find the actual object:
```liquid
{% for p in products %}
  {% if p.id == section.settings.featured_product %}
    <h3>{{ p.title }}</h3>
  {% endif %}
{% endfor %}
```

### Multiple Resource Selectors (Lists)

Select **multiple** items — direct iteration possible:

| Type | Description | Returns |
|------|-------------|---------|
| `product_list` or `products_list` | Multiple products | Array of full product objects |
| `collection_list` or `collections_list` | Multiple collections | Array of full collection objects |
| `category_list` or `categories_list` | Multiple categories | Array of full category objects |
| `posts_list` | Multiple blog posts | Array of full post objects |
| `enrollments_list` or `enrollment_list` | Multiple enrollments | Array of enrollment objects |

Example:
```json
{
  "type": "product_list",
  "id": "featured_products",
  "label": "Featured Products",
  "limit": 8,
  "info": "Select up to 8 products to feature"
}
```

---

## Organization Types

| Type | Description | Use Case |
|------|-------------|----------|
| `header` | Section divider with heading | Group related settings |

```json
{
  "type": "header",
  "content": "Typography Settings"
}
```

---

## Special Types

| Type | Description | Use Case |
|------|-------------|----------|
| `text_alignment` | Text alignment picker | Left/center/right alignment |
| `link_list` | Menu selector | Navigation menus |

---

## NOT Supported — Use Alternatives

Using these types in your `{% schema %}` will cause errors or prevent the section from rendering in the editor.

| Unsupported Type | Alternative | Notes |
|-----------------|-------------|-------|
| `number` | `range` | Fluid uses range sliders for numeric inputs |
| `paragraph` | `header` with description | Headers can include instructional text |
| `inline_richtext` | `text` or `richtext` | Not available in Fluid |
| `article` | `post` | Fluid uses "posts" instead of "articles" |
| `article_list` | `posts_list` | Same — use "posts" terminology |
| `video` | `video_picker` or `url` | Different implementation in Fluid |
| `video_url` | `url` or `video_picker` | Use URL type for video links |
| `page` | Not available | Pages are handled differently in Fluid |
| `liquid` | Not available | Cannot inject raw Liquid code |
| `color_scheme` | `color` | Color schemes not implemented |
| `color_scheme_group` | Multiple `color` settings | Group colors manually |
| `metaobject` | Not available | Metaobjects not implemented |
| `metaobject_list` | Not available | Metaobjects not implemented |

### Migration Examples (Shopify → Fluid)

```json
// Shopify (NOT supported)
{ "type": "article", "id": "featured_article" }

// Fluid (correct)
{ "type": "post", "id": "featured_post" }
```

```json
// Shopify (NOT supported)
{ "type": "number", "id": "quantity" }

// Fluid (correct)
{ "type": "range", "id": "quantity", "min": 1, "max": 10, "step": 1, "default": 1 }
```

```json
// Shopify (NOT supported)
{ "type": "video_url", "id": "hero_video" }

// Fluid (correct)
{ "type": "url", "id": "hero_video", "label": "Video URL" }
```
