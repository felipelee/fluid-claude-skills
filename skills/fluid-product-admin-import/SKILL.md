---
name: fluid-product-admin-import
description: >-
  Import products and admin settings into Fluid Commerce — the complete store
  migration pipeline. Use when importing products, categories, collections,
  brand, menus, pages, policies, checkout settings, tax, shipping, customers,
  inventory, compliance rules, discounts, redirects, blog posts, or any store
  data. Triggers on product import, store import, migrate store, import products,
  admin settings, Firecrawl, import pipeline, FluidClient API, IdMapping,
  categories, collections, brand import, menus, pages, agreements, onboarding,
  discounts, redirects, blog posts, customers, inventory, shipping zones.
metadata:
  version: 1.1.0
---

# Fluid Product & Admin Settings Import

Two phases: **Crawl** (Firecrawl discovers and scrapes pages) -> **Import** (push everything to Fluid Commerce APIs). Each import step persists `id-mapping.json` for crash recovery.

## Important: This Is a Skills-Only Repo

This repo contains no runnable code — only documentation and API specs.

### Every run is a fresh run

This skill is used by people migrating many different sites into many different Fluid accounts. **Never assume anything from a previous run.** Each invocation:

- **Always ask for all 4 credentials** — even if you think you have them from earlier in the conversation. The user may be switching to a different site or a different Fluid account.
- **Never reuse id-mapping.json from a previous run** — create a fresh working directory each time (e.g. `/tmp/import-{domain}-{timestamp}/`).
- **Never reuse cached tokens, URLs, or company IDs** — the Fluid account, company ID, country IDs, and company_country_ids will all be different per run.
- **Don't reference or read files from previous import directories** — start clean.

### Step 1: Collect credentials

Ask the user for ALL FOUR of these before doing anything else:

1. **Source site URL** — The ecommerce site to migrate (e.g. `https://yellowbirdfoods.com`)
2. **Fluid URL** — Their Fluid store URL (e.g. `https://companyname.fluid.app`)
3. **Fluid API token** — Developer token from their Fluid admin panel (Settings > API Tokens)
4. **Firecrawl API key** — From [firecrawl.dev](https://firecrawl.dev). Needed for brand extraction, page scraping, and non-Shopify sites.

### Step 2: Validate ALL credentials before starting the import

Run these checks in parallel. If ANY fail, stop and tell the user which one failed — don't start the import.

```python
# 1. Check source site is reachable
requests.get("https://yellowbirdfoods.com", timeout=10)
# Should return 200

# 2. Check Fluid API token
requests.get("https://companyname.fluid.app/api/settings/company_countries",
             headers={"Authorization": f"Bearer {fluid_token}"}, timeout=10)
# Should return 200 with company country data
# Also captures company_country_id and country_id for later use

# 3. Check Firecrawl API key
requests.post("https://api.firecrawl.dev/v1/scrape",
              headers={"Authorization": f"Bearer {firecrawl_key}"},
              json={"url": "https://example.com", "formats": ["markdown"], "limit": 1},
              timeout=15)
# Should return 200 (or valid response, not 401/403)
```

Print the results clearly:
```
[Preflight] Source site: ✓ yellowbirdfoods.com is reachable
[Preflight] Fluid API:  ✓ Connected to companyname.fluid.app (Company: "Acme Corp", Country: US/214)
[Preflight] Firecrawl:  ✓ API key is valid
[Preflight] All checks passed — starting import.
```

If validation fails:
```
[Preflight] Fluid API:  ✗ 401 Unauthorized — check your API token
[Preflight] Aborting. Please fix the issue above and try again.
```

### Step 3: Detect platform and begin import

1. **Detect the source platform** — check if the site is Shopify (`/products.json`), WooCommerce (`/wp-json/wc/v3/`), etc. to determine if the fast-path applies
2. **Write and execute scripts** (Python or Node.js) that call the APIs described below to perform the import
3. **Persist `id-mapping.json`** after each step so the import can resume if interrupted

## Implementation Guidelines

When writing import scripts, follow these rules:

- **Use `python3 -u`** (unbuffered) so output streams in real time — otherwise the user sees no progress
- **Print progress** for long-running steps: `"[Assets] Uploaded 50/200 images..."` every 10-20 items
- **Use concurrent workers** for uploads (5-10 with `asyncio.Semaphore` or `concurrent.futures`). Don't process images sequentially.
- **Don't add artificial rate limit delays.** Fluid returns 429 when rate limited — just retry with exponential backoff. Adding `sleep(0.15)` between requests halves throughput for no reason.
- **Only upload product/brand images** in the assets step. Site-wide images (hero banners, section backgrounds, decorative graphics) belong to the site clone workflow, NOT the import.
- **Omit null/empty fields** from all API payloads. Sending `"parent_id": null`, `"sku": null`, or `"product_ids": []` causes 422 errors on many endpoints. Build payloads conditionally — if a value is null/undefined, don't include the key at all.
- **`company_country_id` vs `country_id`** — these are different IDs. `country_id` is the global country (e.g. 214 = US). `company_country_id` is the company's association with that country (e.g. 55938). Agreements use `company_country_ids`. Menus and variants use `country_id`. Get both from `GET /api/settings/company_countries`.
- **Save id-mapping.json** after each step completes (not just at the end). This enables resume-on-crash.
- **Run steps 5+ in parallel where possible.** Steps 1-4 must be sequential (they build the idMapping). Steps 5-24 are mostly independent and can run concurrently.

## Firecrawl Crawling

Source: `src/crawling/crawler.ts`. Wraps `@mendable/firecrawl-js`. Used for unknown platforms (known platforms like Shopify skip crawling and use direct API calls).

### Firecrawl special formats

Beyond crawling, Firecrawl offers specialized extraction formats:

- **`formats: ["branding"]`** — Extracts logo, favicon, colors, fonts, spacing in one call. Use this for the brand import step (see Step 5).
- **`formats: ["extract"]`** with a schema — Structured data extraction. Use for pulling company info, policies, or any structured data.
- **`/extract` endpoint** — AI-powered extraction across multiple URLs. Give it URLs + a prompt/schema, it crawls and returns structured results.

### Three crawl modes

**1. Full crawl** (`crawler.crawl(url)`) — Traditional spider crawl.
- Default: 200 pages, depth 3
- Returns `markdown`, `html`, `links` per page; optionally `screenshot` for theme work
- `onlyMainContent: true` strips nav/footer boilerplate

**2. Map + Stream** (`crawler.mapAndStreamProducts(url)`) — Fast product discovery (~10-15s to first product).
- Step 1: `mapUrl()` discovers all site URLs in ~2-3s (up to 5000 URLs)
- Step 2: Classify URLs into product/collection/other via `classifyPageType()`
- Step 3: `batchScrapeUrlsAndWatch()` streams pages via WebSocket as they're scraped
- Calls `onPage()` immediately for each product/collection/homepage — no waiting for full crawl
- Capped at 100 URLs per batch (products prioritized, max 10 collections, always includes homepage)
- Falls back to sequential batch scrape (10 at a time) if WebSocket fails
- 3-minute safety timeout on WebSocket

**3. Extract agent** (`crawler.extractProducts(url)`) — Last resort for SPAs.
- Uses Firecrawl's AI agent to navigate JavaScript-heavy sites
- Returns structured `ExtractedProduct[]` with name, price, images, variants
- Only used when modes 1 and 2 find zero products

### URL include/exclude paths

```typescript
// Included (crawled)
'/products/*', '/collections/*', '/shop/*', '/catalog/*', '/store/*', '/category/*',
'/policies/*', '/pages/*', '/privacy*', '/terms*', '/shipping*', '/return*', '/refund*',
'/cookie*', '/legal*', '/accessibility*'

// Excluded (skipped)
'/cart*', '/checkout*', '/account*', '/blog/*', '/wp-admin/*'
```

### Page classification (`classifyPageType`)

Every URL is classified into a page type that determines how it's processed downstream:

| Type | URL patterns |
|------|-------------|
| `homepage` | `/`, `/index`, `/index.html` |
| `policy` | `/policies/*`, `/pages/privacy-policy`, `/terms*`, `/shipping*`, `/return*`, `/refund*`, `/cookie*` |
| `collection` | `/collection*`, `/category*`, `/catalog*`, `/shop*`, `/store` (no sub-path or 1 segment) |
| `product` | `/product*`, `/p/*`, `/items/*`, `/store/x/y` (2+ segments after `/store/`) |
| `content` | `/about*`, `/contact*`, `/faq*`, `/blog*`, `/pages/*`, `/sustainability*`, `/reviews*` |
| `other` | Everything else |

**Order matters:** policy checked before collection/product, collection checked before product (URLs like `/products/category/9` contain both patterns — collection wins).

### Product URL discovery fallbacks

When `classifyPageType` finds zero product URLs from the site map:

1. **Deep URL heuristic:** URLs with 2+ path segments that aren't blog/policy/content -> probe one with `scrape()` to check for JSON-LD `Product` schema -> if found, infer URL pattern prefix
2. **Search-based map:** `mapUrl(url, { search: 'buy product price shop store' })` to find commerce pages
3. **Extract agent:** `extractProducts(url)` as absolute last resort (see mode 3 above)

### CrawledPage shape

```typescript
interface CrawledPage {
  url: string;
  type: 'homepage' | 'product' | 'collection' | 'content' | 'policy' | 'other';
  markdown: string;    // Main content as markdown
  html: string;        // Raw HTML
  links: string[];     // Outbound links
  images: string[];    // Image URLs
  screenshot?: string; // Base64 screenshot (when requested for theme work)
}
```

## Site Import Package (input)

```
site-import-{domain}-{timestamp}/
  products.json           # Required — ImportProduct[]
  categories.json         # Required — ImportCategory[]
  brand.json              # Optional — ImportBrand
  site-metadata.json      # Optional — { languages, countries, currencies, timezone, weight_unit, tax_shipping, taxes_included }
  menus.json              # Optional — ImportMenu[]
  media-manifest.json     # Optional — ThemeMediaItem[]
  onboarding.json         # Optional — OnboardingData
  agreements.json         # Optional — ImportAgreement[] (policies, terms, etc.)
  customers.json          # Optional — ImportCustomer[]
  shipping-zones.json     # Optional — ImportShippingZone[]
  checkout-settings.json  # Optional — CheckoutSettings
  inventory-levels.json   # Optional — ImportInventoryLevel[]
  region-rules.json       # Optional — ImportRegionRule[]
  webhooks.json           # Optional — ImportWebhook[]
  shopify-admin.json      # Optional — { discounts, redirects, blog_posts, shop, policies, shipping_zones, customers, inventory_levels, webhooks }
  pages/                  # Optional — individual ImportPage JSON files
  theme/                  # Optional — Liquid/CSS/JS/binary files
  id-mapping.json         # Auto-generated — persisted after each step
```

## Step Execution Order

Steps run sequentially. Each depends on earlier steps completing first.

| # | Step | Function | Reads | Writes to IdMapping | API Endpoint |
|---|------|----------|-------|---------------------|--------------|
| 1 | **Assets** | `importAssets` | products + categories | `assets` (URL->DAM URL) | `POST /api/dam/assets` (multipart) |
| 2 | **Categories** | `importCategories` | categories.json | `categories` (source_id->Fluid ID) | `POST /api/company/v1/categories` |
| 3 | **Collections** | `importCollections` | products (unique `collection_titles`) | `collections` (title->Fluid ID) | `POST /api/company/v1/collections` |
| — | **Country ID** | `getCompanyCountry` | config or API | — | `GET /api/settings/company_countries` |
| 4 | **Products** | `importProducts` | products.json + idMapping | `products` (source_id->Fluid ID) | `POST /api/company/v1/products` |
| 5 | **Brand** | `importBrand` | brand.json | — | `POST /api/application_themes` + `PATCH /api/settings/brand_guidelines` |
| 6 | **Languages** | `importLanguages` | site-metadata.json | — | `GET/POST /api/settings/languages` |
| 7 | **Countries** | `importCountries` | site-metadata.json | — | `GET/POST /api/settings/company_countries` |
| 8 | **DAM Media** | `importDamMedia` | media-manifest.json | — | `POST /api/dam/assets` (multipart) |
| 9 | **Theme Templates** | `importThemeTemplates` | theme/ directory | — | `PUT /api/application_themes/:id/resources` |
| 10 | **Menus** | `importMenus` | menus.json | — | `POST /api/menus` |
| 11 | **Pages** | `importPages` | pages/*.json | — | `POST /api/company/v1/pages` |
| 12 | **Onboarding** | `importOnboarding` | onboarding.json | — | Multiple onboarding endpoints |
| 13 | **Agreements** | `importAgreements` | agreements.json | — | `POST /api/agreements` |
| 14 | **Checkout Settings** | `importCheckoutSettings` | checkout-settings.json | — | `PUT /api/settings/checkout` |
| 15 | **Tax Configuration** | `importTaxConfig` | site-metadata.json | — | `PATCH /api/companies/set_tax_option` + `set_tax_class` |
| 16 | **Shipping Zones** | `importShippingZones` | shipping-zones.json | — | `POST /api/settings/warehouses` + `POST /api/companies/set_shipping` |
| 17 | **Customers** | `importCustomers` | customers.json | `customers` (source_id->Fluid ID) | `POST /api/customers` |
| 18 | **Inventory Levels** | `importInventoryLevels` | inventory-levels.json | — | `POST /api/inventory_levels/bulk_upsert` |
| 19 | **Region Rules** | `importRegionRules` | region-rules.json | — | `POST /api/theme_region_rules` |
| 20 | **Domains** | `importDomains` | site-metadata.json | — | `POST /api/domains` |
| 21 | **Discounts** | `importDiscounts` | shopify-admin.json | — | `POST /api/v2025-06/discounts` |
| 22 | **Redirects** | `importRedirects` | shopify-admin.json | — | `POST /api/redirects` |
| 23 | **Blog Posts** | `importBlogPosts` | shopify-admin.json | — | `POST /api/posts` |
| 24 | **Webhooks** | `importWebhooks` | webhooks.json | — | `POST /api/webhooks` |
| 25 | **Compliance Scan** | `runComplianceScan` | — (post-import) | — | `POST /api/compliance` |

## Key Dependencies

- **Products** need assets (DAM URLs), categories (IDs), collections (IDs), and country ID
- **Theme Templates** need brand step to complete first (provides `themeId`)
- **DAM Media** is for theme media only — product images use the assets step
- **Inventory Levels** need products to be created first (uses Fluid product/variant IDs)
- **Region Rules** need theme templates to exist first (uses `application_theme_template_id`)
- **Compliance Scan** runs last — scans all imported content for MLM compliance issues
- Steps 5-24 are independent of each other except where noted above

## IdMapping

`src/import/id-mapping.ts` — tracks source -> Fluid ID mappings. Persisted to `id-mapping.json` after steps 1-4.

```typescript
class IdMapping {
  assets: Map<string, string>       // sourceUrl -> damUrl
  categories: Map<string, number>   // source_id -> Fluid category ID
  collections: Map<string, number>  // collection title -> Fluid collection ID
  products: Map<string, number>     // source_id -> Fluid product ID
}
```

`serialize()` / `deserialize()` for JSON persistence. On re-run, items already in the mapping are skipped.

## Step Details

### 1. Assets

Upload product and brand images to Fluid DAM. 5-10 concurrent workers recommended.

**CRITICAL: Only upload product-related and brand images in this step.** Do NOT upload site-wide images like hero banners, section backgrounds, decorative graphics, or page content images. Those belong to the theme/site clone step (separate workflow).

**Images to upload in this step:**
- Product gallery images (`product.images[].url`)
- Variant-specific images (`variant.image_url`, `variant.images[].url`)
- Product featured image (`product.image_url`)
- Category images (`category.image_url`)
- Brand logo, favicon, OG image (`brand.logo_url`, `brand.favicon_url`, `brand.og_image_url`)

**Images to SKIP (handled by site clone later):**
- Hero/banner images from homepage sections
- Background images from page sections
- Decorative site graphics (icons, patterns, textures)
- Content/editorial images embedded in page HTML
- Theme assets (CSS backgrounds, sprite sheets)

**Direct upload:**
```
POST /api/dam/assets  (multipart/form-data)
  Authorization: Bearer <FLUID_API_KEY>
  Fields: asset[file] (binary), asset[name] (string)
  -> { asset: { id, code, default_variant_url } }
```

The returned `default_variant_url` (e.g. `https://ik.imagekit.io/fluid/...`) is the DAM URL stored in `idMapping.assets`.

To upload a remote image, first download it to a buffer, then POST the buffer as `asset[file]`.

**Performance tips:**
- Use 5-10 concurrent workers (not sequential)
- Print progress every 10-20 images: `"Uploaded 50/200 images..."`
- Skip URLs already in `idMapping.assets` (resumability)
- Don't add artificial rate limit delays — Fluid handles rate limiting server-side (429 responses trigger retry)

See the **Deduplication and crash recovery** section below for details on resumability and error handling.

### 2. Categories

Source: `src/import/steps/categories.ts`

**Topological sort:** Categories with `parent_source_id` are sorted so parents are created before children. `parent_id` in the Fluid payload is resolved from `idMapping.categories`.

**IMPORTANT: Omit null/empty fields entirely.** Sending `"parent_id": null` or `"product_ids": []` causes 422 errors. Only include fields that have actual values.

```json
{ "category": {
    "title": "Shoes", "description": "...", "position": 1,
    "public": true, "active": true,
    "source_type": "product", "slug": "shoes"
}}
```

Schema (`ImportCategory`): Required: `source_id`, `title`. Optional: `description`, `image_url`, `position`, `public`, `active`, `slug`, `source_type`, `parent_source_id`, `seo`, `product_source_ids`.

### 3. Collections

Source: `src/import/steps/collections.ts`

Collections are derived from unique `collection_titles` across all products (not from a separate file). Slugified from title.

```json
{ "collection": { "title": "Summer Sale", "slug": "summer-sale", "active": true } }
```

IdMapping key is the **collection title string** (not a source_id).

**REQUIRED: Always create a "New Arrivals" collection.** Fluid's base themes reference a "New Arrivals" collection on the homepage. If it doesn't exist, that section shows up blank. After all products are created:

1. Create the collection if it doesn't already exist:
```json
{ "collection": { "title": "New Arrivals", "slug": "new-arrivals", "active": true } }
```

2. Add up to 12 products to it. Pick the most recent products (by `created_at` or position), or if that's not available, just use the first 12 products imported:
```
POST /api/company/v1/collections/{collection_id}/add_product
{ "product_id": 123 }
```
Repeat for each product (up to 12).

3. Store the collection ID in `idMapping.collections["New Arrivals"]`.

This ensures the homepage "New Arrivals" section is populated from day one.

### 4. Products

See the **API Payload Shape** and **Key Implementation Rules** sections below for full product import details.

### 5. Brand

Source: `src/import/steps/brand.ts`

Three sub-steps: **extract brand assets from source site**, create theme, update brand guidelines.

**Step A — Extract brand assets from the source site BEFORE creating anything.**

This is critical — don't skip this. Two approaches:

**Approach 1: Firecrawl Branding Format (recommended when Firecrawl API key is available)**

Firecrawl has a dedicated branding extraction that pulls logo, colors, fonts, and favicon in one call:

```python
# Python
from firecrawl import FirecrawlApp
fc = FirecrawlApp(api_key="fc-...")
result = fc.scrape_url("https://example.com", params={"formats": ["branding"]})
branding = result.get("branding", {})
```

Returns a `BrandingProfile` with:
```json
{
  "logo": "https://example.com/logo.svg",
  "colors": {
    "primary": "#FF6B35",
    "secondary": "#004E89",
    "accent": "#F77F00",
    "background": "#1A1A1A",
    "textPrimary": "#FFFFFF",
    "textSecondary": "#B0B0B0"
  },
  "typography": {
    "fontFamilies": { "primary": "Inter", "heading": "Inter" },
    "fontSizes": { "h1": "48px", "h2": "36px", "body": "16px" },
    "fontWeights": { "regular": 400, "bold": 700 }
  },
  "images": {
    "logo": "https://example.com/logo.svg",
    "favicon": "https://example.com/favicon.ico"
  }
}
```

Not all sites expose complete branding — Firecrawl often misses favicon and OG image. **Always run Approach 2 as well.**

**Approach 2: HTML scraping (REQUIRED — always run this even if Firecrawl branding worked)**

Firecrawl's branding format frequently misses the favicon and OG image. You MUST scrape these from the HTML directly. Run this script against the source site homepage:

```python
import requests
from html.parser import HTMLParser

html = requests.get(source_url, timeout=15).text

# Extract favicon, OG image, and apple-touch-icon from <head>
favicon_url = None
og_image_url = None
apple_touch_icon = None

class HeadParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global favicon_url, og_image_url, apple_touch_icon
        d = dict(attrs)
        if tag == 'link':
            rel = (d.get('rel') or '').lower()
            href = d.get('href', '')
            if 'icon' in rel and 'apple' not in rel and href:
                favicon_url = href
            if 'apple-touch-icon' in rel and href:
                apple_touch_icon = href
        if tag == 'meta':
            prop = (d.get('property') or '').lower()
            content = d.get('content', '')
            if prop == 'og:image' and content:
                og_image_url = content

HeadParser().feed(html)

print(f"Favicon: {favicon_url}")
print(f"OG Image: {og_image_url}")
print(f"Apple Touch Icon: {apple_touch_icon}")
```

**Resolve relative URLs** — if the extracted URL starts with `/`, prepend the source site origin.

**Fallback chain for each asset:**

| Asset | Priority 1 | Priority 2 | Priority 3 |
|-------|-----------|-----------|-----------|
| **Favicon (= App Icon)** | `<link rel="icon">` | `<link rel="apple-touch-icon">` | `/favicon.ico` (try fetching directly) |
| **OG Image** | `<meta property="og:image">` | Logo URL (reuse) | Favicon URL (last resort) |
| **Logo** | Firecrawl branding `images.logo` | `<img>` in header with "logo" in class/alt | JSON-LD `Organization.logo` |

**The app icon in Fluid IS the favicon.** Use the same URL for both. Upload it once to DAM, use the DAM URL.

**CRITICAL: Do not skip OG image.** If `<meta property="og:image">` is not found:
1. Check `<meta property="og:image:secure_url">`
2. Check `<meta name="twitter:image">`
3. Fall back to the logo URL

On Shopify, also check:
- `/meta.json` for store name and description
- `<script type="application/ld+json">` for `Organization` schema (has `logo`, `name`, `url`)

**Upload all found brand assets to DAM first** via `POST /api/dam/assets`, then use the returned DAM URLs in the brand guidelines payload. You need 3 DAM URLs at the end of this step: one for logo, one for favicon/app icon, one for OG image.

**Step B — Create application theme** — `POST /api/application_themes`
Maps brand colors/fonts -> CSS variables (`--color-primary`, `--font-heading`, etc.) + a `:root` custom stylesheet.

```json
{ "application_theme": {
    "name": "Brand Theme", "description": "...",
    "variables": "{\"primary-color\":\"#1a1a1a\",...}",
    "custom_stylesheet": ":root { --color-primary: #1a1a1a; }",
    "status": "active"
}}
```

Returns `{ application_theme: { id } }` — this `themeId` is needed for theme templates.

**Step C — Update brand guidelines** — `PATCH /api/settings/brand_guidelines`

```json
{
  "brand_guidelines": {
    "name": "Yellowbird Foods",
    "logo_url": "https://ik.imagekit.io/fluid/.../logo.png",
    "favicon_url": "https://ik.imagekit.io/fluid/.../favicon.png",
    "app_icon_url": "https://ik.imagekit.io/fluid/.../favicon.png",
    "og_image_url": "https://ik.imagekit.io/fluid/.../og-image.jpg",
    "primary_color": "#FF6B35",
    "secondary_color": "#1A1A1A",
    "primary_font": "Montserrat",
    "heading_font": "Montserrat"
  }
}
```

**All four image fields MUST be set:** `logo_url`, `favicon_url`, `app_icon_url`, `og_image_url`.
- `app_icon_url` = same as `favicon_url` (the favicon IS the app icon in Fluid)
- `og_image_url` = the OG image, or fall back to logo if not found
- Never leave any of these blank — always have a value, even if it's the logo as fallback

Schema (`ImportBrand`): Required: `name`, `primary_color`. Optional: `secondary_color`, `accent_color`, `background_color`, `text_color`, `primary_font`, `heading_font`, `logo_url`, `favicon_url`, `og_image_url`, `brand_images`, `css_variables`.

### 6. Languages

Source: `src/import/steps/languages.ts`

1. `GET /api/settings/languages` — fetch all available languages with `active_in_company` status
2. Match detected ISO codes against available languages
3. `POST /api/settings/languages` with `{ id: languageId }` for each inactive match

Skips already-active languages. Unknown ISOs logged and skipped.

### 7. Countries

Source: `src/import/steps/countries.ts`

1. `GET /api/settings/company_countries` — fetch currently configured countries
2. Skip already-configured ISOs
3. `POST /api/settings/company_countries` with `{ company_country: { country_id, currency } }`

Uses a hardcoded `ISO_TO_FLUID_COUNTRY_ID` map (e.g., US=214, GB=185, DE=65) and `COUNTRY_CURRENCY` map (US->USD, GB->GBP, etc.). Detected currencies from site metadata override defaults.

### 8. DAM Media

Source: `src/import/steps/dam-media.ts`

For theme media only (product images use step 1). Reads `media-manifest.json` (`ThemeMediaItem[]`), skips video embeds and items with `damUrl` already set (uploaded during extraction). Uploads via `client.uploadMedia()`.

### 9. Theme Templates

Source: `src/import/steps/theme-templates.ts`

Recursively collects all files under `theme/` directory. Two upload paths:

- **Text files** (`.liquid`, `.css`, `.js`, `.json`, `.html`, `.txt`) -> `PUT /api/application_themes/:id/resources` with content string
- **Binary files** (`.png`, `.woff2`, `.svg`, etc.) -> 3-step ImageKit upload -> `PUT` with `dam_asset` reference

Uploads all files in parallel. Requires `themeId` from brand step.

### 10. Menus

Source: `src/import/steps/menus.ts`

```json
{ "menu": {
    "title": "Main Menu", "active": true,
    "country_ids": [214],
    "menu_items_attributes": [
      { "title": "Shop", "linkable_type": "Url", "order": 1, "url": "/collections",
        "sub_menu_items_attributes": [
          { "title": "New", "linkable_type": "Url", "order": 1, "url": "/collections/new" }
        ]
      }
    ]
}}
```

Schema (`ImportMenu`): Required: `title`, `items`. Optional: `active`, `country_ids`.
Schema (`ImportMenuItem`): Required: `title`, `linkable_type`. Optional: `linkable_id`, `order`, `url`, `sub_menu_items` (recursive).

Menu items support nested `sub_menu_items_attributes` for multi-level navigation.

**IMPORTANT:** `country_ids` uses the **country_id** (e.g. `214` for US), NOT the `company_country_id`. Get the country_id from `GET /api/settings/company_countries` — use the nested `country.id` field, not the top-level `id`.

### 11. Pages

Source: `src/import/steps/pages.ts`

```json
{ "page": {
    "title": "About Us", "slug": "about",
    "publish": true, "default": false, "use_for_shop": false,
    "source": "code", "html_code": "<div>...</div>",
    "search_engine_optimizer_attributes": { "title": "...", "description": "..." }
}}
```

Schema (`ImportPage`): Required: `title`. Optional: `slug`, `publish`, `default`, `use_for_shop`, `source` (`'code'` | `'builder'`), `html_code`, `json`, `image_url`, `seo`, `country_ids`, `category_source_id`, `application_theme_template_id`.

Pages with `source: 'code'` use `html_code`. Pages with `source: 'builder'` use `json`.

### 12. Onboarding

Source: `src/import/steps/onboarding.ts`

Requires `companyId` from config. Runs 6 sub-steps:

1. `PUT /companies/{id}/onboarding_info` — business basics, MCC, policies (via `buildOnboardingInfoPayload`)
2. `PATCH /api/settings/social_media` — social links (Facebook, Instagram, Twitter, etc.)
3. `PATCH /api/settings/company` — shipping settings (manual shipping, free shipping threshold)
4. `POST /companies/{id}/entities` — legal entity (if sufficient data from `buildEntityPayload`)
5. `POST /companies/{id}/bank_accounts` — bank accounts from Plaid data (via `buildBankAccountPayloads`)
6. `POST /companies/{id}/owners` — owner/person from Plaid identity (via `buildOwnerPayload`)

Steps 5-6 only run when `data.plaid` is present. Each sub-step is best-effort — failures don't block others.

### 13. Agreements (Policies, Terms & Conditions)

Source: `agreements.json` or scraped from policy pages.

**Extraction:** Crawl `/policies/*`, `/terms*`, `/privacy*`, `/refund*`, `/shipping-policy` pages. On Shopify with admin token: `GET /admin/api/latest/policies.json` returns clean `{ title, body, url, handle }` for each policy. For non-Shopify sites, use Firecrawl to scrape policy pages and extract HTML content.

**Mapping policy types to agreements:**

| Source policy | Agreement title | `show_at_checkout` | `required_on_checkout` |
|---|---|---|---|
| Terms of Service | Terms of Service | `true` | `true` |
| Privacy Policy | Privacy Policy | `true` | `false` |
| Refund Policy | Refund Policy | `true` | `false` |
| Shipping Policy | Shipping Policy | `false` | `false` |
| Subscription Policy | Subscription Policy | `true` | `true` |

```json
{ "agreement": {
    "title": "Terms of Service",
    "description": "<p>Full HTML content of the policy...</p>",
    "active": true,
    "show_at_checkout": true,
    "required_on_checkout": true,
    "default_checked": false,
    "required": true,
    "company_country_ids": [55938],
    "language_iso": "en"
}}
```

**IMPORTANT:** `company_country_ids` uses the **company_country_id** (the top-level `id` from `GET /api/settings/company_countries`), NOT the `country.id`. This is the opposite of menus. For example, if the company_countries response has `{ id: 55938, country: { id: 214, name: "United States" } }`, use `[55938]` here.

`POST /api/agreements` — Response: `{ agreement: { id, title, ... } }`

When updating an existing agreement via `PATCH /api/agreements/:id`, the `title` field is **required** even if you're only updating the description.

Also supports `attachments[]` for PDF policy documents, and `clone` + `bulk_delete` for management.

Schema (`ImportAgreement`): Required: `title`, `description`. Optional: `active`, `show_at_checkout`, `required_on_checkout`, `default_checked`, `required`, `company_country_ids` (number[] — uses company_country_id, not country_id), `language_iso`, `show_path`, `enrollment_pack_id`.

### 14. Checkout Settings

Source: `checkout-settings.json` or inferred from source site behavior.

**Extraction:** From Shopify `GET /admin/api/latest/shop.json`: extract `requires_extra_payments_agreement`, phone collection settings. From site scraping: detect checkout form fields, button colors from CSS.

```json
{ "checkout": {
    "collect_phone": true,
    "require_phone": false,
    "require_billing_zip": true,
    "primary_button_color": "#1a1a1a",
    "text_color": "#ffffff"
}}
```

`PUT /api/settings/checkout` — overwrites checkout configuration.

### 15. Tax Configuration

Source: `site-metadata.json` or Shopify shop settings.

**Extraction:** From Shopify `GET /admin/api/latest/shop.json`: `tax_shipping` (boolean), `taxes_included` (boolean), `county_taxes` (boolean). From Shopify admin: per-country/province tax overrides via `GET /admin/api/latest/countries.json`.

Two API calls:

1. `PATCH /api/companies/set_tax_option` — set whether tax is included in prices, applied to shipping, etc.
2. `PATCH /api/companies/set_tax_class` — set the tax class/category for the company

Tax categories are hierarchical — fetch available options via `GET /api/tax_categories` (supports `parent_id`, `search`).

### 16. Shipping Zones & Warehouses

Source: `shipping-zones.json` or Shopify admin.

**Extraction:** From Shopify `GET /admin/api/latest/shipping_zones.json` — returns zones with countries, provinces, and rate rules (weight-based, price-based, carrier-calculated).

**Step A — Create warehouses:**
```json
{ "warehouse": {
    "name": "Main Warehouse",
    "address1": "123 Main St",
    "city": "Austin",
    "province": "TX",
    "postal_code": "78701",
    "country_iso": "US",
    "active": true
}}
```
`POST /api/settings/warehouses` — then `POST /api/settings/warehouses/:id/assign_to_country` to link warehouse to country.

**Step B — Set shipping rates:**
`POST /api/companies/set_shipping` — configure free shipping threshold, manual shipping rates, handling fees.

Each `company_country` also has `base_shipping` and `handling_fee` fields configurable via `POST /api/settings/company_countries`.

### 17. Customers

Source: `customers.json` or Shopify admin.

**Extraction:** From Shopify `GET /admin/api/latest/customers.json` (paginated, up to 250 per page). Returns: first_name, last_name, email, phone, addresses[], tags, marketing consent, orders_count, total_spent, created_at.

```json
{ "customer": {
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@example.com",
    "phone": "+15551234567",
    "addresses": [{
      "address1": "123 Main St",
      "city": "Austin",
      "province": "TX",
      "zip": "78701",
      "country": "US"
    }],
    "tags": ["vip", "wholesale"]
}}
```

`POST /api/customers` — Response: `{ customer: { id, ... } }`

Also supports `append_metadata` for custom data. Store `source_id -> Fluid ID` in idMapping for future reference.

**Privacy note:** Customer data is PII. The skill should warn users about data handling obligations and confirm they have authorization to transfer customer data.

### 18. Inventory Levels

Source: `inventory-levels.json` or Shopify admin.

**Extraction:** From Shopify `GET /admin/api/latest/inventory_levels.json` — returns `{ inventory_item_id, location_id, available }` per SKU per location.

**Depends on:** Products step (needs Fluid variant IDs from `idMapping.products`).

```json
{ "inventory_levels": [
    { "variant_id": 456, "quantity": 100, "warehouse_id": 1 }
]}
```

`POST /api/inventory_levels/bulk_upsert` — set stock quantities in bulk. Also supports `POST /api/inventory_levels/adjust` for incremental changes.

Individual operations: `GET /api/inventory_levels` (list), `GET /api/inventory_levels/:id`, `POST /api/inventory_levels/set`.

### 19. Theme Region Rules (State/Region Compliance)

Source: `region-rules.json` or inferred from shipping zones / "where we operate" pages.

**Extraction:** Infer operating states/regions from:
- Shopify shipping zones (states with rates = operating states)
- "Available in" / "We ship to" page content
- State-specific legal disclaimers in footer
- For MLM: compliance pages listing approved states

For states where the company does NOT operate, create redirect rules:

```json
{ "theme_region_rule": {
    "application_theme_template_id": 123,
    "region_code": "US-MT",
    "active": true,
    "redirect_type": "302",
    "redirect_url": "/not-available-in-your-state",
    "description": "Montana - not approved for operations",
    "priority": 1
}}
```

Region codes follow ISO 3166-2 format (e.g., `US-CA` for California, `US-TX` for Texas, `CA-ON` for Ontario).

`POST /api/theme_region_rules` — CRUD available. Supports filtering by `company_id`, `region_code`, `active`.

**Depends on:** Brand/theme step (needs `application_theme_template_id`).

### 20. Domains

Source: `site-metadata.json` — extract the source site's custom domain.

```json
{ "domain": {
    "name": "www.example.com"
}}
```

`POST /api/domains` — creates domain record. Then:
- `POST /api/domains/:id/check_cname_propagation` — verify DNS is pointed correctly
- `POST /api/domains/:id/verify_domain` — complete domain verification
- `POST /api/domains/:id/confirm_cname_for_domain` — finalize CNAME setup

**Note:** This step creates the domain record but the user must manually update their DNS records to point to Fluid. The skill should output the required CNAME/A records for the user.

### 21-23. Shopify Admin Extras

Only present when Shopify admin token was used during extraction. Read from `shopify-admin.json`.

**Discounts** -> `POST /api/v2025-06/discounts` with `{ discount: { title, code, discount_type, value, starts_at, ends_at, ... } }`

**Redirects** -> `POST /api/redirects` with `{ redirect: { path, target } }`

**Blog Posts** -> `POST /api/posts` with `{ post: { title, slug, body, author_name, tags, published_at, status } }`

### 24. Webhooks

Source: `webhooks.json` or Shopify admin `GET /admin/api/latest/webhooks.json`.

**Extraction:** From Shopify, extract webhook subscriptions to understand what integrations the store uses (analytics, fulfillment, CRM, etc.). Map to Fluid webhook events.

Fluid webhook event types: `cart_abandoned`, `cart_updated`, `contact_created`, `contact_updated`, `event_created`, `event_deleted`, `event_updated`, `order_cancelled`, `order_completed`, `order_updated`, `order_shipped`, `order_refunded`, `popup_submitted`, `product_created`, `product_updated`, `product_destroyed`, `subscription_started`, `subscription_paused`, `subscription_cancelled`, `user_created`, `user_updated`, `user_deactivated`.

```json
{ "webhook": {
    "url": "https://example.com/webhooks/orders",
    "events": ["order_completed", "order_shipped"]
}}
```

`POST /api/webhooks` — CRUD + `bulk_delete`, `get_payload_example`.

### 25. Compliance Scan (Post-Import)

Runs after all content is imported. Scans products, media, pages, and other content for MLM compliance issues.

`POST /api/compliance` — creates a new compliance scan. Supports scanning: products, media, playlists, categories, collections, posts, enrollment_packs.

Response: `{ compliance: { id, score, status, summary, scanned_at, compliance_issues[] } }`

Status values: `"unknown"`, `"poor"`, `"fair"`, `"good"`, `"excellent"`.

This step should:
1. Trigger a scan for all imported products
2. Wait for scan completion
3. Report the compliance score and any flagged issues
4. Log specific `compliance_issues[]` for user review

## FluidClient API Methods (complete)

### Store entities
| Method | HTTP | Endpoint |
|--------|------|----------|
| `createCategory(params)` | POST | `/api/company/v1/categories` |
| `createCollection(params)` | POST | `/api/company/v1/collections` |
| `createProduct(params)` | POST | `/api/company/v1/products` |
| `createMenu(params)` | POST | `/api/menus` |
| `createPage(params)` | POST | `/api/company/v1/pages` |

### Brand & theme
| Method | HTTP | Endpoint |
|--------|------|----------|
| `createTheme(params)` | POST | `/api/application_themes` |
| `updateBrandGuidelines(params)` | PATCH | `/api/settings/brand_guidelines` |
| `upsertThemeResource(themeId, key, content)` | PUT | `/api/application_themes/:id/resources` |
| `upsertThemeResourceBinary(themeId, key, buffer, fileName, mimeType)` | PUT | `/api/application_themes/:id/resources` (via DAM) |

### Agreements & compliance
| Method | HTTP | Endpoint |
|--------|------|----------|
| `createAgreement(params)` | POST | `/api/agreements` |
| `listAgreements()` | GET | `/api/agreements` |
| `updateAgreement(id, params)` | PATCH | `/api/agreements/:id` |
| `deleteAgreement(id)` | DELETE | `/api/agreements/:id` |
| `cloneAgreement(id)` | POST | `/api/agreements/:id/clone` |
| `createComplianceScan(params)` | POST | `/api/compliance` |
| `getComplianceScan(id)` | GET | `/api/compliance/:id` |
| `listComplianceScans()` | GET | `/api/compliance` |

### Customers
| Method | HTTP | Endpoint |
|--------|------|----------|
| `createCustomer(params)` | POST | `/api/customers` |
| `listCustomers()` | GET | `/api/customers` |
| `getCustomer(id)` | GET | `/api/customers/:id` |
| `updateCustomer(id, params)` | PATCH | `/api/customers/:id` |

### Inventory
| Method | HTTP | Endpoint |
|--------|------|----------|
| `bulkUpsertInventory(params)` | POST | `/api/inventory_levels/bulk_upsert` |
| `setInventoryLevel(params)` | POST | `/api/inventory_levels/set` |
| `adjustInventoryLevel(params)` | POST | `/api/inventory_levels/adjust` |
| `listInventoryLevels()` | GET | `/api/inventory_levels` |

### Settings
| Method | HTTP | Endpoint |
|--------|------|----------|
| `getCompanyCountry()` | GET | `/api/settings/company_countries` |
| `getCompanyCountries()` | GET | `/api/settings/company_countries` |
| `addCompanyCountry(countryId, currency)` | POST | `/api/settings/company_countries` |
| `getLanguages()` | GET | `/api/settings/languages` |
| `enableLanguage(languageId)` | POST | `/api/settings/languages` |
| `updateSocialMediaSettings(params)` | PATCH | `/api/settings/social_media` |
| `setCompanyShipping(settings)` | PATCH | `/api/settings/company` |
| `getCheckoutSettings()` | GET | `/api/settings/checkout` |
| `updateCheckoutSettings(params)` | PUT | `/api/settings/checkout` |
| `setTaxOption(params)` | PATCH | `/api/companies/set_tax_option` |
| `setTaxClass(params)` | PATCH | `/api/companies/set_tax_class` |
| `getTaxCategories()` | GET | `/api/tax_categories` |

### Warehouses
| Method | HTTP | Endpoint |
|--------|------|----------|
| `createWarehouse(params)` | POST | `/api/settings/warehouses` |
| `listWarehouses()` | GET | `/api/settings/warehouses` |
| `assignWarehouseToCountry(warehouseId, countryId)` | POST | `/api/settings/warehouses/:id/assign_to_country` |

### Region rules
| Method | HTTP | Endpoint |
|--------|------|----------|
| `createRegionRule(params)` | POST | `/api/theme_region_rules` |
| `listRegionRules()` | GET | `/api/theme_region_rules` |
| `updateRegionRule(id, params)` | PATCH | `/api/theme_region_rules/:id` |
| `deleteRegionRule(id)` | DELETE | `/api/theme_region_rules/:id` |

### Domains
| Method | HTTP | Endpoint |
|--------|------|----------|
| `createDomain(params)` | POST | `/api/domains` |
| `listDomains()` | GET | `/api/domains` |
| `checkCnamePropagation(id)` | POST | `/api/domains/:id/check_cname_propagation` |
| `verifyDomain(id)` | POST | `/api/domains/:id/verify_domain` |

### Onboarding
| Method | HTTP | Endpoint |
|--------|------|----------|
| `updateOnboardingInfo(companyId, params)` | PUT | `/companies/{id}/onboarding_info` |
| `createEntity(companyId, params)` | POST | `/companies/{id}/entities` |
| `createBankAccount(companyId, params)` | POST | `/companies/{id}/bank_accounts` |
| `createOwner(companyId, params)` | POST | `/companies/{id}/owners` |

### Webhooks
| Method | HTTP | Endpoint |
|--------|------|----------|
| `createWebhook(params)` | POST | `/api/webhooks` |
| `listWebhooks()` | GET | `/api/webhooks` |
| `deleteWebhook(id)` | DELETE | `/api/webhooks/:id` |
| `getWebhookPayloadExample(event)` | GET | `/api/webhooks/payload_example` |

### Shopify extras
| Method | HTTP | Endpoint |
|--------|------|----------|
| `createDiscount(params)` | POST | `/api/v2025-06/discounts` |
| `createRedirect(params)` | POST | `/api/redirects` |
| `createPost(params)` | POST | `/api/posts` |

### DAM & media
| Method | HTTP | Endpoint |
|--------|------|----------|
| `uploadMedia(url, title)` | POST | Download source -> `POST /api/dam/assets` (multipart: `asset[file]`, `asset[name]`) |
| `uploadAsset(buffer, name)` | POST | `POST /api/dam/assets` (multipart: `asset[file]`, `asset[name]`) |

### Metafields
| Method | HTTP | Endpoint |
|--------|------|----------|
| `createMetafieldDefinition(params)` | POST | `/api/v2/metafield_definitions` |
| `createMetafield(params)` | POST | `/api/v2/metafields` |

All methods go through `FluidClient.request()`: rate limited (10 req/sec token bucket), retry (3 attempts, exponential backoff 1s-30s, retries 429/5xx only), 30s timeout, `Authorization: Bearer <apiKey>`.

## Data Extraction Guide

### What to scrape from ANY ecommerce site (no API needed)

| Data | Where to find it | Fluid destination |
|------|-------------------|-------------------|
| **Policies/Terms** | `/policies/*`, `/terms*`, `/privacy*`, footer legal links | `POST /api/agreements` |
| **Contact info** | `/contact`, `/about`, footer, JSON-LD `Organization` | Onboarding info |
| **Company address** | Footer, JSON-LD `LocalBusiness`, contact page | Onboarding info + entity |
| **Social links** | Footer `<a>` tags to facebook/instagram/twitter/tiktok/youtube | `PATCH /api/settings/social_media` |
| **FAQ content** | `/faq`, JSON-LD `FAQPage` schema | `POST /api/company/v1/pages` |
| **Announcement bar** | Header/banner HTML | Informational for marketing setup |
| **Payment methods** | Footer payment icons (Visa, MC, Amex, PayPal, etc.) | Informational |
| **Operating regions** | "We ship to" pages, shipping info, state disclaimers | `POST /api/theme_region_rules` |
| **Currency support** | Currency selector, `<meta>` tags, `Shopify.currency` | `POST /api/settings/company_countries` |
| **Size guides** | Product pages, linked pages | `POST /api/company/v1/pages` or product metafields |
| **Newsletter signup** | Popup/footer form, email provider hints (Klaviyo, Mailchimp) | Informational |
| **Trust badges** | Footer/sidebar (BBB, SSL, guarantees) | Can recreate in theme |
| **Structured data** | JSON-LD in `<head>` — `Organization`, `Product`, `BreadcrumbList`, `FAQPage` | Multiple destinations |

### Shopify public JSON endpoints (no auth needed)

| Endpoint | Data | Use |
|----------|------|-----|
| `/products.json?limit=250&page=N` | All products | Product extraction (already used) |
| `/collections.json` | All collections | Category/collection extraction (already used) |
| `/collections/{handle}/products.json` | Collection membership | Product-collection linking (already used) |
| `/meta.json` | Store name, description, URL | Onboarding, brand settings |
| `/pages/{handle}.json` | Individual page content | Page import |

### Shopify Admin API (with token — extra data beyond products)

When the user provides a Shopify admin token, these additional endpoints provide high-quality structured data:

| Endpoint | Data | Fluid destination |
|----------|------|-------------------|
| `GET /admin/api/latest/shop.json` | Full store config: name, email, address, phone, currency, timezone, weight_unit, tax settings, locales | Onboarding, settings, tax config |
| `GET /admin/api/latest/policies.json` | Store policies with title + body HTML | `POST /api/agreements` |
| `GET /admin/api/latest/shipping_zones.json` | Zones with countries, provinces, rate rules | Warehouses, shipping config, region rules |
| `GET /admin/api/latest/customers.json` | Customer profiles, addresses, consent, tags | `POST /api/customers` |
| `GET /admin/api/latest/inventory_levels.json` | Stock quantities per SKU per location | `POST /api/inventory_levels/bulk_upsert` |
| `GET /admin/api/latest/locations.json` | Warehouse/store addresses | `POST /api/settings/warehouses` |
| `GET /admin/api/latest/countries.json` | Per-country/province tax rates | Tax configuration |
| `GET /admin/api/latest/webhooks.json` | Active webhook subscriptions | `POST /api/webhooks` |
| `GET /admin/api/latest/gift_cards.json` | Active gift card balances (requires special scope) | Manual transfer |
| GraphQL `translatableResources` | Product/page translations per locale | Multi-language content |
| GraphQL `markets` | Multi-market config (countries, currencies, domains) | Country/currency setup |

## Error Handling Patterns

- **Per-entity try/catch:** Each item in a step is wrapped individually — one failure doesn't stop others
- **Duplicate detection:** "already taken" / "already exists" errors are silently skipped (not counted as failures)
- **Best-effort steps:** Brand guidelines, metafields, onboarding sub-steps swallow errors
- **Progress callbacks:** Every step reports `(current, total, detail)` via `ImportProgressCallback`
- **Result aggregation:** All errors collected into a single `errors[]` array, returned with counts

## Source Files

| File | Purpose |
|------|---------|
| `src/crawling/crawler.ts` | Firecrawl crawler — crawl, map+stream, extract agent |
| `src/import/importer.ts` | Orchestrator — step ordering and file I/O |
| `src/import/fluid-client.ts` | HTTP client — all Fluid API methods |
| `src/import/id-mapping.ts` | Source -> Fluid ID persistence |
| `src/import/steps/assets.ts` | DAM image upload (product/category images) |
| `src/import/steps/categories.ts` | Category creation with topological sort |
| `src/import/steps/collections.ts` | Collection creation from product titles |
| `src/import/steps/products.ts` | Product + variant + metafield creation |
| `src/import/steps/brand.ts` | Theme + brand guidelines |
| `src/import/steps/languages.ts` | Language enablement |
| `src/import/steps/countries.ts` | Country configuration |
| `src/import/steps/dam-media.ts` | Theme media upload |
| `src/import/steps/theme-templates.ts` | Liquid/CSS/binary resource upload |
| `src/import/steps/menus.ts` | Navigation menu creation |
| `src/import/steps/pages.ts` | CMS page creation |
| `src/import/steps/onboarding.ts` | Onboarding data (business info, entity, bank, owner) |
| `src/import/steps/agreements.ts` | Policy/terms import as Fluid agreements |
| `src/import/steps/checkout.ts` | Checkout settings configuration |
| `src/import/steps/tax.ts` | Tax option and class configuration |
| `src/import/steps/shipping.ts` | Warehouse creation and shipping zone config |
| `src/import/steps/customers.ts` | Customer profile migration |
| `src/import/steps/inventory.ts` | Inventory level bulk upsert |
| `src/import/steps/region-rules.ts` | State/region compliance rules |
| `src/import/steps/domains.ts` | Domain registration and CNAME setup |
| `src/import/steps/webhooks.ts` | Webhook subscription creation |
| `src/import/steps/compliance.ts` | Post-import compliance scanning |
| `src/import/steps/discounts.ts` | Shopify discount migration |
| `src/import/steps/redirects.ts` | URL redirect creation |
| `src/import/steps/blog-posts.ts` | Blog post migration |
| `src/schemas/category.ts` | ImportCategory schema |
| `src/schemas/brand.ts` | ImportBrand schema |
| `src/schemas/menu.ts` | ImportMenu / ImportMenuItem schemas |
| `src/schemas/page.ts` | ImportPage schema |
| `src/schemas/agreement.ts` | ImportAgreement schema |
| `src/schemas/customer.ts` | ImportCustomer schema |
| `src/schemas/onboarding.ts` | OnboardingData schema |
| `src/onboarding/payload-builder.ts` | Onboarding payload construction |
