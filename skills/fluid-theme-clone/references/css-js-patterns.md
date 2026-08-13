# CSS & JavaScript Patterns

## Where CSS lives — `assets/` only

**Every stylesheet lives under `assets/`, flat, no sub-folders.** This is the current Fluid contract; getting it wrong is not cosmetic, it breaks pushes.

| Kind | File | Referenced from | How |
|------|------|-----------------|-----|
| Theme foundation | `assets/global_styles.css` | `layouts/theme.liquid`, before `</head>` | `{{ 'global_styles.css' \| inline_asset_content }}` |
| Theme custom overrides | `assets/styles.css` | `layouts/theme.liquid`, before `</head>` | `{{ 'styles.css' \| inline_asset_content }}` |
| Per-section / per-template | `assets/{section_name}.css` | top of that `index.liquid` | `{{ 'hero_section.css' \| asset_url \| stylesheet_tag }}` |

### The two theme-level files are special

`styles.css` and `global_styles.css` were once DB columns (`custom_stylesheet` / `global_stylesheet`) that the renderer inlined on every request. They are now real assets, and they have two hard rules:

- **Exact filenames.** The backend FileResource lookup keys on `styles.css` and `global_styles.css` literally. Renaming to `global.css` / `theme.css` breaks `inline_asset_content` resolution.
- **Always inline, never `stylesheet_tag`.** Inlining matches pre-migration output byte-for-byte and avoids a round trip for foundation CSS on every page.

Order in `layouts/theme.liquid` — after the `{% style %}` variable block so custom CSS wins the cascade at equal specificity, foundation before overrides:

```liquid
    {% style %}
      :root { /* CSS variables from settings */ }
    {% endstyle %}

    {{ 'global_styles.css' | inline_asset_content }}
    {{ 'styles.css'        | inline_asset_content }}
  </head>
```

### Per-section CSS: inline vs external

Reference it at the **top** of the section's `index.liquid` — never after `{% endschema %}`, which is dead space.

- **> 2 KB** → `{{ 'name.css' | asset_url | stylesheet_tag }}` — a cacheable `<link>`. The engine dedupes stylesheets across the page, so declaring per-section is safe and beats loading everything in the layout.
- **≤ 2 KB** → `{{ 'name.css' | inline_asset_content }}` — critical CSS without the extra request.

Check with `wc -c`. The 2 KB threshold is what the backend's own auto-migration used.

### Deprecated: co-located stylesheets

`sections/{name}/styles.css`, `components/{name}/styles.css`, `{page_type}/{variant}/styles.css` — **do not create these.** They're the old convention. A new one is a blocker; an existing one should be migrated to `assets/`.

Once a company has the `STYLESHEET_STRICT_INPUT` flag on, the API **rejects the deprecated shape with a 422** and pushes fail outright. Theme-root `styles.css` / `global_styles.css` count as deprecated too — they belong in `assets/`.

### Inline `<style>` — only for dynamic values

An inline block is right only when the CSS depends on schema settings. Keep the static base in the asset and leave the setting-driven overrides inline:

```liquid
{{ 'hero_section.css' | asset_url | stylesheet_tag }}
<style>
  .hero[data-section-id="{{ section.id }}"] {
    --section-bg:  {{ section.settings.bg_color }};
    --section-pad: {{ section.settings.section_pad }};
  }
</style>
```

Over ~10 lines of static inline CSS → extract it to an asset.

Never hardcode a path (`<link href="/assets/x.css">`) or a third-party CDN URL for CSS the theme owns. Go through `asset_url` so you get the fingerprinted, CDN-fronted URL.

---

## CSS: Scoped Styles with BEM

Use BEM naming with a section-specific prefix so section styles can't leak into each other.

### Naming Convention
```
.eh-<section-name>           → Block (the section)
.eh-<section-name>__element  → Element (child of block)
.eh-<section-name>--modifier → Modifier (variant)
```

### Mobile-First Responsive Pattern

Base styles are mobile. Scale up with `min-width` breakpoints:
- `768px` — tablet
- `1024px` — desktop

`assets/stories.css` — plain CSS, no `<style>` wrapper:

```css
  .eh-stories {
    background-color: #FFFBE0;
    padding: 64px 0;
  }
  .eh-stories__heading {
    font-size: 28px;
    font-weight: 800;
    text-align: center;
    margin: 0 0 32px;
  }
  @media (min-width: 768px) {
    .eh-stories__heading {
      font-size: 36px;
    }
  }
  .eh-stories__grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 24px;
  }
  @media (min-width: 768px) {
    .eh-stories__grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
  @media (min-width: 1024px) {
    .eh-stories__grid {
      grid-template-columns: repeat(4, 1fr);
    }
  }
```

Referenced from the top of the section:

```liquid
{{ 'stories.css' | asset_url | stylesheet_tag }}
```

---

## Where JavaScript lives

Same rule as CSS: **runtime JS belongs in `assets/`, loaded with `defer`.**

```liquid
<script src="{{ 'featured_slider.js' | asset_url }}" defer></script>
```

- Inline `<script>` over ~5 lines → extract to an asset. Inline JS bypasses caching and runs render-blocking.
- `defer` unless the script genuinely must run before DOM (rare in themes) — render-blocking scripts hurt LCP.
- The one acceptable inline case is a tiny config bridge passing settings into the runtime:

  ```liquid
  <script>
    window.fluidFeaturedConfig = {{ section.settings | json }};
  </script>
  <script src="{{ 'featured_slider.js' | asset_url }}" defer></script>
  ```

- Never `<script src="https://unpkg.com/...">` for a library the theme depends on — vendor it into `assets/`. Third-party CDNs go down and you don't control what they serve.
- Never hoist `asset_url` calls into a loop — resolve once above the `{% for %}` and reuse the variable.

The snippets below show the JS logic itself; in a real theme each one is the body of an `assets/*.js` file, not an inline block.

---

## JavaScript: Carousels with Splide.js

Splide.js is usually already loaded in Fluid themes. Use it for carousels and sliders.

```html
<script>
document.addEventListener('DOMContentLoaded', function() {
  if (typeof Splide === 'undefined') return;
  var el = document.getElementById('carousel-{{ section.id }}');
  if (!el) return;
  new Splide(el, {
    type: 'slide',
    perPage: 3,
    gap: '16px',
    pagination: false,
    breakpoints: {
      767: { perPage: 1 },
      1023: { perPage: 2 }
    }
  }).mount();
});
</script>
```

HTML structure for the carousel:
```html
<div id="carousel-{{ section.id }}" class="splide">
  <div class="splide__track">
    <ul class="splide__list">
      {% for block in section.blocks %}
        <li class="splide__slide" {{ block.fluid_attributes }}>
          <!-- slide content -->
        </li>
      {% endfor %}
    </ul>
  </div>
</div>
```

---

## JavaScript: Accordions

```html
<script>
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.eh-faq__question').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var item = this.closest('.eh-faq__item');
      var isOpen = item.classList.contains('is-open');
      // Close all
      document.querySelectorAll('.eh-faq__item').forEach(function(i) {
        i.classList.remove('is-open');
      });
      // Toggle current
      if (!isOpen) item.classList.add('is-open');
    });
  });
});
</script>
```

CSS for accordion:
```css
.eh-faq__answer {
  max-height: 0;
  overflow: hidden;
  transition: max-height 0.3s ease-out;
}
.eh-faq__item.is-open .eh-faq__answer {
  max-height: 500px;
}
.eh-faq__icon {
  transition: transform 0.3s ease;
}
.eh-faq__item.is-open .eh-faq__icon {
  transform: rotate(180deg);
}
```

---

## JavaScript: Scroll Animations (IntersectionObserver)

```html
<script>
document.addEventListener('DOMContentLoaded', function() {
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('[data-animate]').forEach(function(el) {
    observer.observe(el);
  });
});
</script>
```

CSS for scroll animations:
```css
[data-animate] {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}
[data-animate].is-visible {
  opacity: 1;
  transform: translateY(0);
}

/* Stagger children */
[data-animate]:nth-child(2) { transition-delay: 0.1s; }
[data-animate]:nth-child(3) { transition-delay: 0.2s; }
[data-animate]:nth-child(4) { transition-delay: 0.3s; }
[data-animate]:nth-child(5) { transition-delay: 0.4s; }
[data-animate]:nth-child(6) { transition-delay: 0.5s; }
```

Add `data-animate` to any element you want to animate on scroll:
```html
<div class="eh-features__card" data-animate {{ block.fluid_attributes }}>
  ...
</div>
```

---

## Common CSS Patterns

### Full-width section with max-width content
```css
.eh-hero {
  width: 100%;
  padding: 80px 20px;
}
.eh-hero__inner {
  max-width: 1200px;
  margin: 0 auto;
}
```

### Two-column split layout
```css
.eh-split {
  display: flex;
  flex-direction: column;
  gap: 32px;
}
@media (min-width: 768px) {
  .eh-split {
    flex-direction: row;
    align-items: center;
  }
  .eh-split__image,
  .eh-split__text {
    flex: 1;
  }
  .eh-split--reverse {
    flex-direction: row-reverse;
  }
}
```

### Card with hover effect
```css
.eh-card {
  border-radius: 12px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.eh-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
}
```

### Button styles
```css
.eh-btn {
  display: inline-block;
  padding: 14px 32px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  text-decoration: none;
  text-align: center;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.2s ease;
}
.eh-btn:hover {
  transform: translateY(-1px);
}
.eh-btn--primary {
  background-color: #FF6B35;
  color: #FFFFFF;
}
.eh-btn--primary:hover {
  background-color: #E55A2B;
}
```
