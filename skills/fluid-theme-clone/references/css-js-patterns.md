# CSS & JavaScript Patterns

## CSS: Scoped Styles with BEM

All CSS lives in a `<style>` block inside the section file. Use BEM naming with a section-specific prefix to avoid conflicts.

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

```html
<style>
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
</style>
```

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
