---
name: fluid-theme-refine
description: >-
  Refine and improve a Fluid theme to achieve pixel-perfect 1:1 match with
  the source site. Use after fluid-theme-clone to tighten up visual fidelity.
  Triggers on "refine theme," "improve theme," "make it closer," "pixel perfect,"
  "doesn't match," "fix the spacing," "colors are off," "fonts don't match,"
  "compare and fix," "tighten up," "QA the theme," "visual diff," "side by side
  comparison," "it doesn't look right," "make it exact," or "closer to the original."
metadata:
  version: 1.0.0
---

# Fluid Theme Refine

You are an expert Fluid theme developer doing a pixel-perfect QA pass. Your job is to take an already-cloned Fluid theme, compare it against the original source site screenshot-by-screenshot, identify every visual discrepancy, fix them, and repeat until the two are indistinguishable.

This skill is the polish step after `/fluid-theme-clone`. The clone gets you 80-90% there. This gets you to 99%.

## How This Works

```
┌─────────────────────────────────────────────────────────┐
│                  REFINEMENT LOOP                         │
│                                                          │
│  ┌──────────┐    ┌──────────┐                           │
│  │ SOURCE   │    │ BUILT    │                           │
│  │ (live    │    │ (Fluid   │                           │
│  │  site)   │    │  theme)  │                           │
│  └────┬─────┘    └────┬─────┘                           │
│       │               │                                  │
│       ▼               ▼                                  │
│  ┌─────────────────────────┐                            │
│  │  SCREENSHOT BOTH PAGES  │                            │
│  │  at same viewport width │                            │
│  │  scroll to same section │                            │
│  └───────────┬─────────────┘                            │
│              ▼                                           │
│  ┌─────────────────────────┐                            │
│  │  COMPARE SIDE BY SIDE   │                            │
│  │  List EVERY difference: │                            │
│  │  - colors               │                            │
│  │  - spacing/padding      │                            │
│  │  - font size/weight     │                            │
│  │  - border radius        │                            │
│  │  - layout/alignment     │                            │
│  │  - missing content      │                            │
│  │  - animations           │                            │
│  └───────────┬─────────────┘                            │
│              ▼                                           │
│  ┌─────────────────────────┐     ┌──────────┐          │
│  │  ANY DIFFERENCES?       │────▶│   DONE   │          │
│  │  NO                     │     │  Report  │          │
│  └───────────┬─────────────┘     └──────────┘          │
│         YES  │                                          │
│              ▼                                           │
│  ┌─────────────────────────┐                            │
│  │  EXTRACT EXACT VALUES   │                            │
│  │  from source via JS     │                            │
│  │  getComputedStyle(el)   │                            │
│  └───────────┬─────────────┘                            │
│              ▼                                           │
│  ┌─────────────────────────┐                            │
│  │  FIX THE CSS/HTML       │                            │
│  │  Update section file    │                            │
│  └───────────┬─────────────┘                            │
│              ▼                                           │
│  ┌─────────────────────────┐                            │
│  │  UPLOAD FIXED FILE      │                            │
│  │  to Fluid theme API     │                            │
│  └───────────┬─────────────┘                            │
│              ▼                                           │
│       (loop back to screenshot)                          │
└─────────────────────────────────────────────────────────┘
```

Every round: screenshot → compare → list diffs → extract values → fix → upload → screenshot again. Repeat until no differences remain.

---

## Step 1: Collect Inputs

| Input | Required | Description |
|-------|----------|-------------|
| `SOURCE_URL` | Yes | The original page to match (e.g. `https://yellowbirdfoods.com`) |
| `FLUID_URL` | Yes | The Fluid store URL (e.g. `https://companyname.fluid.app`) |
| `FLUID_TOKEN` | Yes | Fluid API token |
| `THEME_ID` | Yes* | The application theme ID to update. If not provided, fetch via `GET /api/application_themes` and ask the user to confirm which one. |
| `THEME_DIR` | No | Local working directory with theme files. If not provided, work directly against the Fluid API. |

Also ask:
- **Which page?** Homepage, a specific page, or "all pages"?
- **Which breakpoints?** Desktop only, or also tablet/mobile?
- **Specific sections?** Or full page sweep?

---

## Step 2: Validate and Set Up

```python
# 1. Source site reachable
requests.get(source_url, timeout=10)

# 2. Fluid API works
resp = requests.get(f"{fluid_url}/api/application_themes",
                    headers={"Authorization": f"Bearer {fluid_token}"})
# Find the theme, confirm theme_id

# 3. Fluid store page is reachable
requests.get(f"{fluid_url}", timeout=10)
```

Print:
```
[Refine] Source: OK yellowbirdfoods.com
[Refine] Fluid:  OK companyname.fluid.app (Theme ID: 55697)
[Refine] Starting refinement pass.
```

---

## Step 3: Screenshot Both Pages

Open two browser tabs — one for the source, one for the Fluid store.

### 3a: Set up both tabs

```
Tab 1: SOURCE_URL (the original site)
Tab 2: FLUID_URL (the Fluid store with the cloned theme)
```

### 3b: Remove overlays on both

```javascript
// Run on both tabs
document.querySelectorAll('[data-acsb-custom-trigger],.acsb-trigger,.acsb-widget,.acsb-overlay,.popup,.modal,[class*="cookie"],[class*="banner"]').forEach(e => e.remove());
```

### 3c: Set same viewport width

Both pages must be at the same width for comparison. Start with desktop (1280px).

### 3d: Screenshot each section pair

Scroll both pages to the same section. Take a screenshot of each.

**Label every screenshot pair:**
```
Section 1: Hero
  - source_hero_desktop.png
  - built_hero_desktop.png

Section 2: Features Grid
  - source_features_desktop.png
  - built_features_desktop.png
```

---

## Step 4: Detailed Comparison

For each section pair, create a **diff report**. Be exhaustive — catch everything:

```
SECTION: Hero
STATUS: 3 differences found

1. BACKGROUND COLOR
   Source: #1B3A4B
   Built:  #1C3B4C
   Fix:    Update .eh-hero background-color

2. HEADING FONT SIZE (mobile)
   Source: 32px
   Built:  28px
   Fix:    Update @media (max-width: 767px) .eh-hero__heading font-size

3. BUTTON BORDER RADIUS
   Source: 24px (fully rounded)
   Built:  8px
   Fix:    Update .eh-hero__cta border-radius

---

SECTION: Features Grid
STATUS: Match ✓

---

SECTION: Testimonials
STATUS: 2 differences found

1. CARD SHADOW
   Source: 0 4px 12px rgba(0,0,0,0.08)
   Built:  none
   Fix:    Add box-shadow to .eh-testimonials__card

2. GAP BETWEEN CARDS
   Source: 32px
   Built:  24px
   Fix:    Update .eh-testimonials__grid gap
```

### What to Compare (Checklist)

For EVERY section, check all of these:

**Layout**
- [ ] Same column count and arrangement
- [ ] Same max-width / container width
- [ ] Same alignment (left, center, right)
- [ ] Same content order

**Colors**
- [ ] Background color (section level)
- [ ] Background color (card/element level)
- [ ] Heading text color
- [ ] Body text color
- [ ] Button background and text color
- [ ] Border colors
- [ ] Hover state colors

**Typography**
- [ ] Font family
- [ ] Font size (heading, subheading, body, caption)
- [ ] Font weight
- [ ] Line height
- [ ] Letter spacing
- [ ] Text transform (uppercase, capitalize)

**Spacing**
- [ ] Section padding (top and bottom)
- [ ] Element margins
- [ ] Grid/flex gap
- [ ] Content padding inside cards

**Borders & Shapes**
- [ ] Border radius on cards, buttons, images
- [ ] Border width and style
- [ ] Box shadow

**Images**
- [ ] Correct image displayed
- [ ] Same aspect ratio / object-fit
- [ ] Same size
- [ ] Same border radius

**Interactive**
- [ ] Hover effects match
- [ ] Scroll animations match (timing, easing, direction)
- [ ] Carousel behavior matches
- [ ] Accordion behavior matches

---

## Step 5: Extract Exact Values from Source

For every difference found, go to the source site and extract the exact computed value:

```javascript
// Target the specific element
var el = document.querySelector('.hero-section h1');
var s = getComputedStyle(el);

// Extract everything relevant
JSON.stringify({
  color: s.color,
  fontSize: s.fontSize,
  fontWeight: s.fontWeight,
  fontFamily: s.fontFamily,
  lineHeight: s.lineHeight,
  letterSpacing: s.letterSpacing,
  textTransform: s.textTransform,
  margin: s.margin,
  padding: s.padding
}, null, 2);
```

For backgrounds and containers:
```javascript
var el = document.querySelector('.hero-section');
var s = getComputedStyle(el);

JSON.stringify({
  backgroundColor: s.backgroundColor,
  padding: s.padding,
  maxWidth: s.maxWidth,
  borderRadius: s.borderRadius,
  boxShadow: s.boxShadow,
  gap: s.gap
}, null, 2);
```

**Convert `rgb()` values to hex** for cleaner CSS:
```javascript
function rgbToHex(rgb) {
  var m = rgb.match(/\d+/g);
  return '#' + m.slice(0,3).map(x => parseInt(x).toString(16).padStart(2,'0')).join('');
}
```

---

## Step 6: Fix the Section Files

Update the section's `index.liquid` file with the corrected values. Be surgical — only change what's wrong.

**Common fixes:**
- Color off by a shade → update hex value in `<style>` block
- Spacing wrong → update padding/margin/gap values
- Font size wrong at a breakpoint → update the `@media` query
- Missing box-shadow → add the property
- Border radius wrong → update the value
- Missing hover effect → add `:hover` rule
- Animation timing off → adjust `transition-duration` or `transition-delay`

### After fixing, read the file back to verify the change is correct.

---

## Step 7: Upload Fixed Files to Fluid

Push the updated section to the Fluid theme:

```python
with open(filepath, 'r') as f:
    content = f.read()

requests.put(
    f"{fluid_url}/api/application_themes/{theme_id}/resources",
    headers={
        "Authorization": f"Bearer {fluid_token}",
        "Content-Type": "application/json"
    },
    json={"key": key, "content": content}
)
```

The `key` is the path relative to the theme root (e.g. `sections/exact-yb-hero/index.liquid`).

---

## Step 8: Re-Screenshot and Verify

After uploading fixes:

1. **Hard refresh** the Fluid store page (Cmd+Shift+R) to clear cache
2. **Screenshot the fixed section** at the same viewport width
3. **Compare against source again**
4. If still different → go back to Step 5
5. If matching → move to next section

---

## Step 9: Responsive Pass

After desktop matches, repeat the full comparison at:

| Viewport | Width |
|----------|-------|
| Tablet | 768px |
| Mobile | 375px |

At each breakpoint:
1. Resize both source and built pages to the same width
2. Screenshot each section pair
3. Compare, fix, upload, verify

Common responsive issues:
- Grid columns don't collapse at the right breakpoint
- Font sizes don't scale down enough
- Padding is too large on mobile
- Images don't resize properly
- Hamburger menu behavior differs

---

## Step 10: Final Report

After all sections match at all breakpoints, print a summary:

```
=== REFINEMENT COMPLETE ===

Page: https://yellowbirdfoods.com (Homepage)
Theme: companyname.fluid.app (Theme ID: 55697)

ROUNDS: 3
SECTIONS REFINED: 7 of 9 (2 already matched)
TOTAL FIXES: 14

Fixes by type:
  Colors:     4 (background, text, button)
  Spacing:    3 (padding, gap)
  Typography: 3 (font-size, weight, line-height)
  Borders:    2 (border-radius, box-shadow)
  Layout:     1 (grid columns at tablet)
  Animation:  1 (scroll fade-in timing)

Breakpoints verified:
  Desktop (1280px): ✓ Match
  Tablet (768px):   ✓ Match
  Mobile (375px):   ✓ Match

All sections now match the source site.
```

---

## When to Stop

- **All sections match at all 3 breakpoints** → done
- **After 5 rounds on the same section** with no progress → note the remaining deviations (likely custom fonts, dynamic content, or third-party widgets) and move on
- **Differences are in dynamic content** (live prices, counters, user-generated content) → not fixable, note and skip
- **Custom fonts not available** → use the closest match, document the substitution

---

## Running on Specific Sections

If the user says "fix the hero section" or "the testimonials don't match," skip the full-page sweep and jump directly to that section:

1. Screenshot just that section on both source and built
2. Run the comparison checklist
3. Extract values, fix, upload, verify
4. Done

---

## Running on All Pages

If refining a full site clone, work through pages in this order:
1. Homepage (establishes the design language)
2. Product pages
3. Collection/shop pages
4. Static pages (about, FAQ, etc.)

Between pages, check if fixes to shared sections (nav, footer, CTA banners) propagate correctly.
