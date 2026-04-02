# Section Template Reference

## Complete Section File Structure

Every section lives at `sections/<section-name>/index.liquid` and follows this three-part structure: Style, HTML+Liquid, Schema.

```liquid
<style>
  /* Scoped CSS using BEM naming — prefix with section abbreviation */
  .eh-section-name {
    padding: 64px 0;
  }
  .eh-section-name__element { ... }
  .eh-section-name__element--modifier { ... }

  /* Mobile-first: base styles are mobile, then scale up */
  @media (min-width: 768px) { /* tablet */ }
  @media (min-width: 1024px) { /* desktop */ }
</style>

<section class="eh-section-name" {{ section.fluid_attributes }}>
  <div class="container">
    <!-- Section-level content from section.settings -->
    <h2 class="eh-section-name__heading">{{ section.settings.heading }}</h2>

    <!-- Block-level repeating content -->
    {% for block in section.blocks %}
      <div class="eh-section-name__card" {{ block.fluid_attributes }}>
        {{ block.settings.title }}
      </div>
    {% endfor %}
  </div>
</section>

<script>
  /* JavaScript if needed (carousels, accordions, scroll animations) */
</script>

{% schema %}
{
  "name": "Section Display Name",
  "tag": "section",
  "class": "eh-section-name-section",
  "settings": [ ... ],
  "blocks": [ ... ],
  "presets": [ ... ]
}
{% endschema %}
```

---

## Critical Attributes

| Attribute | Where | Purpose |
|-----------|-------|---------|
| `{{ section.fluid_attributes }}` | Outermost `<section>` element | Lets Fluid's visual editor identify and manage the section |
| `{{ block.fluid_attributes }}` | Each block's outermost element | Same purpose for blocks |

**Forgetting these will make the section invisible to the editor.**

---

## Settings vs Blocks Decision Guide

### Use Section Settings For:
Content that appears **once** in the section — heading, subheading, background color, CTA button, layout toggle.

```json
"settings": [
  { "type": "text", "id": "heading", "label": "Heading", "default": "Our Story" },
  { "type": "textarea", "id": "subtext", "label": "Subtext", "default": "..." },
  { "type": "text", "id": "bg_color", "label": "Background Color", "default": "#FFFFFF" },
  { "type": "checkbox", "id": "reverse_layout", "label": "Reverse Layout", "default": false }
]
```

### Use Blocks For:
Content that **repeats** — cards, testimonials, features, FAQ items, team members.

```json
"blocks": [
  {
    "type": "card",
    "name": "Feature Card",
    "settings": [
      { "type": "text", "id": "image_url", "label": "Image URL", "default": "" },
      { "type": "text", "id": "title", "label": "Title", "default": "Feature" },
      { "type": "textarea", "id": "description", "label": "Description", "default": "" }
    ]
  }
]
```

### Multiple Block Types
Sections can accept different block types for flexibility:

```json
"blocks": [
  {
    "type": "text_block",
    "name": "Text Block",
    "settings": [
      { "type": "text", "id": "heading", "label": "Heading" },
      { "type": "richtext", "id": "content", "label": "Content" }
    ]
  },
  {
    "type": "image_block",
    "name": "Image Block",
    "settings": [
      { "type": "text", "id": "image_url", "label": "Image URL" },
      { "type": "text", "id": "caption", "label": "Caption" }
    ]
  }
]
```

In Liquid, check block type:
```liquid
{% for block in section.blocks %}
  {% if block.type == 'text_block' %}
    <div {{ block.fluid_attributes }}>{{ block.settings.heading }}</div>
  {% elsif block.type == 'image_block' %}
    <img {{ block.fluid_attributes }} src="{{ block.settings.image_url }}" />
  {% endif %}
{% endfor %}
```

---

## Image Handling

For "exact clone" sections, store image URLs as `type: "text"` settings — NOT `type: "image"` which uses Fluid's native picker. This lets you paste DAM URLs directly:

```json
{
  "type": "text",
  "id": "image_url",
  "label": "Image URL (DAM)",
  "default": ""
}
```

In the template:
```liquid
{% if section.settings.image_url != blank %}
  <img src="{{ section.settings.image_url }}" alt="{{ section.settings.heading }}" loading="lazy">
{% endif %}
```

---

## Presets — Always Pre-fill Content

Presets define what the section looks like when first added in the editor. **Always include all cloned content** so the section is ready to use:

```json
"presets": [
  {
    "name": "Customer Stories",
    "settings": {
      "heading": "What Parents Are Saying",
      "bg_color": "#FFFBE0"
    },
    "blocks": [
      {
        "type": "story",
        "settings": {
          "photo_url": "https://ik.imagekit.io/fluid/980243104/testimonial-1_abc.png",
          "title": "Changed our mornings",
          "quote": "My kids ask for their vitamins every day now!"
        }
      },
      {
        "type": "story",
        "settings": {
          "photo_url": "https://ik.imagekit.io/fluid/980243104/testimonial-2_def.png",
          "title": "Finally found the right vitamin",
          "quote": "No more fighting over gummy vitamins."
        }
      }
    ]
  }
]
```

---

## Block Limits

Control how many blocks can be added:

```json
"blocks": [
  {
    "type": "card",
    "name": "Card",
    "limit": 8,
    "settings": [ ... ]
  }
]
```

---

## Complete Worked Example

A centered expert quote section with photo, quote text, and expert credentials:

```liquid
<style>
  .eh-expert-quote {
    background-color: {{ section.settings.bg_color | default: '#FFFBE0' }};
    padding: 80px 0;
  }
  .eh-expert-quote__inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 24px;
    max-width: 700px;
    margin: 0 auto;
    text-align: center;
  }
  @media (min-width: 768px) {
    .eh-expert-quote__inner {
      flex-direction: row;
      text-align: left;
      gap: 40px;
      max-width: 800px;
    }
  }
  .eh-expert-quote__photo {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    flex-shrink: 0;
  }
  .eh-expert-quote__text {
    font-size: 22px;
    font-weight: 500;
    color: #3B82C4;
    margin: 0;
    line-height: 1.4;
  }
  @media (min-width: 768px) {
    .eh-expert-quote__text { font-size: 28px; }
  }
  .eh-expert-quote__name {
    font-size: 16px;
    font-weight: 700;
    color: #1B3A4B;
    margin: 0;
  }
  .eh-expert-quote__title {
    font-size: 14px;
    color: #4A6572;
    margin: 4px 0 0;
  }
</style>

<section class="eh-expert-quote" {{ section.fluid_attributes }}>
  <div class="container">
    <div class="eh-expert-quote__inner">
      {% if section.settings.photo_url != blank %}
        <img class="eh-expert-quote__photo"
             src="{{ section.settings.photo_url }}"
             alt="{{ section.settings.name }}"
             loading="lazy">
      {% endif %}
      <div class="eh-expert-quote__content">
        {% if section.settings.quote != blank %}
          <p class="eh-expert-quote__text">"{{ section.settings.quote }}"</p>
        {% endif %}
        {% if section.settings.name != blank %}
          <div>
            <p class="eh-expert-quote__name">{{ section.settings.name }}</p>
            {% if section.settings.credential != blank %}
              <p class="eh-expert-quote__title">{{ section.settings.credential }}</p>
            {% endif %}
          </div>
        {% endif %}
      </div>
    </div>
  </div>
</section>

{% schema %}
{
  "name": "Expert Quote",
  "tag": "section",
  "class": "eh-expert-quote-section",
  "settings": [
    { "type": "text", "id": "bg_color", "label": "Background Color", "default": "#FFFBE0" },
    { "type": "text", "id": "photo_url", "label": "Expert Photo URL", "default": "" },
    { "type": "textarea", "id": "quote", "label": "Quote Text", "default": "So many vitamins are loaded with excess sugar and junk. Hiya is really clean." },
    { "type": "text", "id": "name", "label": "Expert Name", "default": "Dr. Mark Hyman, M.D." },
    { "type": "text", "id": "credential", "label": "Expert Credential", "default": "New York Times Best Selling Author" }
  ],
  "blocks": [],
  "presets": [
    {
      "name": "Expert Quote",
      "settings": {
        "bg_color": "#FFFBE0",
        "photo_url": "https://ik.imagekit.io/fluid/980243104/dr-hyman_abc123.webp",
        "quote": "So many vitamins are loaded with excess sugar and junk. Hiya is really clean.",
        "name": "Dr. Mark Hyman, M.D.",
        "credential": "New York Times Best Selling Author"
      }
    }
  ]
}
{% endschema %}
```
