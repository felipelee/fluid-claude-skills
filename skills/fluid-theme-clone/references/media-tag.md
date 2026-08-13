# Media rendering — the `media_tag` filter

Every setting- or resource-backed image and video renders through `| media_tag`. It emits a complete, responsive element — `srcset`, WebP/AVIF negotiation, `loading`, `decoding="async"`, and `alt` — from one filter.

Docs: <https://docs.fluid.app/docs/themes/media-tag>

## The rule

A hand-rolled `<img>` or `<video>` that renders an `image` / `image_picker` / `video_picker` / `media_picker` setting, or a resource image (`product.image`, `collection.image`, …), is almost always wrong. It ships one fixed-size original — no responsive `srcset`, no format negotiation — which bloats the download, hurts LCP, and makes you remember `loading` / `decoding` / `alt` by hand every time.

```liquid
{%- comment -%} Bad: fixed original, manual attributes {%- endcomment -%}
<img src="{{ section.settings.banner_image }}"
     alt="{{ section.settings.heading | escape }}"
     loading="lazy" decoding="async" />

{%- comment -%} Good {%- endcomment -%}
{{ section.settings.banner_image | media_tag: sizes: '(max-width: 768px) 100vw, 1200px', alt: section.settings.heading }}
```

Two things that follow from this:

- **Don't wrap it in `| escape`.** `media_tag` escapes its own output; double-escaping breaks the markup.
- **The `{%- if image != blank -%}` guard is optional.** `media_tag` renders nothing on blank input. Keep the guard only when surrounding markup (a wrapper, a grid cell) must be suppressed too.

## Options

Filter arguments. Anything not in this table becomes a plain HTML attribute — `class`, `id`, `data-*` all pass through.

| Option    | Default             | Purpose |
|-----------|---------------------|---------|
| `sizes`   | `100vw`             | Browser sizing hint — set it to the real rendered width |
| `widths`  | `400,800,1200,1600` | `srcset` breakpoints |
| `width`   | —                   | Fixed display width; emits a 2× retina `srcset` |
| `height`  | —                   | Layout stability (avoids CLS) |
| `quality` | `80`                | 1–100 |
| `format`  | `auto`              | WebP/AVIF negotiation |
| `crop`    | —                   | Focus point |
| `loading` | `lazy`              | Use `eager` above the fold |
| `alt`     | image's alt text    | Set it for `*_picker` settings; `alt: ''` for decorative |

```liquid
{%- comment -%} Fixed-width logo, retina srcset {%- endcomment -%}
{{ section.settings.logo | media_tag: width: 240, alt: 'Logo' }}

{%- comment -%} Hero — eager, or lazy-loading delays LCP {%- endcomment -%}
{{ section.settings.hero | media_tag: sizes: '100vw', loading: 'eager', alt: section.settings.heading }}

{%- comment -%} Card image in a 3-up grid {%- endcomment -%}
{{ block.settings.image | media_tag: sizes: '(max-width: 767px) 100vw, 33vw', alt: block.settings.title }}
```

**Set `loading: 'eager'` on the hero.** It's the single most common `media_tag` mistake — the default `lazy` applied to the largest above-the-fold image directly delays LCP.

## Video

A video URL (`.mp4` / `.mov` / `.webm` / `.m4v`) or video object renders a `<video>`. Options: `autoplay`, `loop`, `muted`, `controls`, `poster`, `format` (default `mp4`), `quality`.

```liquid
{{ section.settings.bg_video | media_tag: autoplay: true, loop: true, muted: true }}
```

Background video needs `muted: true` — browsers block autoplay with sound.

## What it does *not* replace

- **Static theme assets.** `{{ 'logo.svg' | asset_url }}` is not ImageKit media. `media_tag` passes non-ImageKit URLs through as a plain tag, so `asset_url` plus a plain `<img>` stays correct for files shipped in `assets/`.
- **Your judgement on `alt`.** `media_tag` defaults `alt` from a resource image (`product.featured_image`), but `*_picker` settings carry none — pass one explicitly, or `alt: ''` if the image is decorative.

## Accessibility note

Don't hand-roll `decoding="async"` or `loading="lazy"` alongside `media_tag` — it applies both. The one you do set deliberately is `loading: 'eager'` for above-the-fold imagery.
