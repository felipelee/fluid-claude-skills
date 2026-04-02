---
name: fluid-product-import
description: >-
  Import products into Fluid Commerce via the Fluid API, including uploading
  images to Fluid DAM via ImageKit. Use when creating, modifying, or debugging
  product import logic, building product payloads, mapping variants/images/
  categories/collections, uploading assets to DAM, or working with the
  ImportProduct schema. Triggers on product import, Fluid product API, DAM
  upload, ImageKit, asset upload, variants, product images, category linking,
  collection linking, metafields, or ImportProduct.
metadata:
  version: 1.1.0
---

# Fluid Product Import

Imports `ImportProduct[]` into Fluid Commerce via `POST /api/company/v1/products`. Includes uploading product/category images to Fluid DAM, then creating products with variants, categories, collections, SEO, and metafields.

## Important: This Is a Skills-Only Repo

This repo contains no runnable code — only documentation and API specs. When a user invokes this skill, you should:

1. **Ask for credentials** before starting: Fluid URL, Fluid API token, and optionally a Firecrawl API key (for non-Shopify sites)
2. **Write and execute scripts** (Python or Node.js) that call the APIs described below
3. **Persist `id-mapping.json`** after each step so the import can resume if interrupted

## Extraction: How Products Are Produced

Before import, products must be extracted from the source store. Two paths exist — the router is `runExtraction()` in `src/extraction/extractor.ts`.

### Path 1: Shopify Fast-Path (~100% accuracy, free)

Source: `src/extraction/fast-path/shopify.ts`. No crawl needed — calls public Shopify JSON APIs directly.

**Product fetching:**
```
GET {origin}/products.json?limit=250&page={n}
```
Paginates until empty page or `crawlLimit` reached. Rate limited at 2 req/sec (burst 10). Retries 3x on 429/430.

**Mapping (`mapShopifyProduct` -> `ImportProduct`):**
- `source_id` = `String(product.id)`
- `description` = `body_html`
- `slug` = `handle`
- `price` / `compare_price` = first variant's prices (parsed from strings to numbers)
- `status` = mapped from Shopify's `active`/`draft`/`archived`
- `public` = `published_at !== null`
- `in_stock` = `true` if any variant is `available`
- `option_attrs` = option names (e.g. `["Size", "Color"]`), filters out `"Default Title"`
- `tags` = comma-split string or array
- `images` = `product.images[]` -> `{ url: src, position, alt_text }`

**Variant mapping (`mapShopifyVariant` -> `ImportVariant`):**
- `option_attrs` = `[option1, option2, option3]` (non-null values)
- `weight` = grams converted to kg string
- `track_quantity` = `inventory_management === 'shopify'`
- `keep_selling` = `inventory_policy === 'continue'`
- `image_url` = `featured_image.src` or matched via `image_id`

**Collection fetching:**
```
GET {origin}/collections.json?limit=250
GET {origin}/collections/{handle}/products.json  (per collection, for membership)
```
Collections -> `ImportCategory[]`. Products get `collection_titles` from membership + `"All Products"`.

**Category inference:** If no collections found, `product_type` values become categories. Each product's `category_title` = its `product_type`.

**Other supported fast-paths:** WooCommerce (`/wp-json/wc/v3/`), Squarespace (`/{slug}?format=json`), BigCommerce (GraphQL). All map to the same `ImportProduct` schema.

### Path 2: Firecrawl + AI Extraction (~85-95% accuracy)

Used for unknown platforms or when fast-path isn't available. Requires `FIRECRAWL_API_KEY` + `ANTHROPIC_API_KEY`.

**Two modes of AI extraction:**

**Streaming mode** (`runStreamingAiExtraction`): Map -> batch-scrape -> extract as pages stream in. Products appear in ~10-15s.
1. `crawler.mapAndStreamProducts(url)` — discovers URLs via Firecrawl sitemap, classifies as product/collection/content
2. For each product page streamed in, immediately calls `extractProductsFromPage()` (concurrent, rate-limited)
3. Falls back to full crawl if map fails
4. Last resort: `crawler.extractProducts(url)` via Firecrawl Extract agent for SPAs

**Traditional mode** (`runAiExtraction`): Full crawl first, then extract.
1. Firecrawl crawls site -> `CrawlResult` with pages classified by type
2. Product pages processed in parallel via `extractProductsFromPage()`
3. Collection pages -> `extractCategoryFromPage()` for categories

**Per-page AI extraction** (`src/extraction/ai/product-extractor.ts`):
- Sends page markdown + JSON-LD structured data to Claude
- System prompt enforces strict JSON output matching `ImportProduct` schema
- JSON-LD is treated as highest-confidence source (prices, SKUs, availability)
- Markdown fills in descriptions, images, variant details
- Each product validated through `ImportProductSchema.safeParse()` — failed products get a retry with defaults
- Returns `{ products, confidence, page_type }` — low confidence (<0.7) logged as warning

### Parallel extraction (fast-path platforms)

For known platforms, extraction splits into two concurrent tracks via `runFastExtraction()` + `runSlowEnrichment()`:
- **Fast track** (immediate): products, categories, brand, menus, site metadata, onboarding
- **Slow track** (background): page layout analysis + theme section cloning via AI vision

## ImportProduct Schema

Source: `src/schemas/product.ts` — Zod-validated. Always use `safeParse()`, never `parse()`.

### Required fields

| Field | Type | Notes |
|-------|------|-------|
| `source_id` | `string` | Unique ID from source platform |
| `title` | `string` | Product name |
| `description` | `string` | HTML body content |
| `price` | `number` | Base price (used for master variant when `variants` is empty) |
| `images` | `ImportImage[]` | May be empty array |
| `variants` | `ImportVariant[]` | May be empty array — a synthetic master variant is created |

### Optional fields

`introduction`, `feature_text`, `slug`, `sku`, `compare_price`, `vendor`, `product_type`, `weight`, `in_stock`, `status` (`'active' | 'draft' | 'archived'`), `public`, `publish_to_retail_store`, `publish_to_rep_store`, `category_title`, `collection_titles` (string[]), `option_attrs` (string[]), `tags` (string[]), `image_url`, `seo` (`{ title?, description?, image_url? }`), `metafields` (`ImportMetafield[]`), `source_metadata` (opaque bag).

### ImportVariant

Required: `source_id`, `price`. Optional: `title`, `sku`, `compare_price`, `position`, `track_quantity`, `keep_selling`, `bar_code`, `taxable`, `weight`, `unit_of_weight`, `physical`, `option_attrs` (string[]), `image_url`, `images` (`ImportImage[]`), `inventory_quantity`, `hs_code`, `metafields`.

### ImportImage

Required: `url`, `position`. Optional: `alt_text`.

### ImportMetafield

Required: `namespace`, `key`, `value` (string | number | boolean), `value_type` (`'string' | 'integer' | 'json_string' | 'boolean'`).

## API Payload Shape

`POST /api/company/v1/products` with `Authorization: Bearer <FLUID_API_KEY>`:

```json
{
  "product": {
    "title": "Widget",
    "description": "<p>HTML description</p>",
    "sku": "WDG-001",
    "introduction": "Short intro",
    "feature_text": "Feature bullets",
    "status": "active",
    "public": true,
    "publish_to_retail_store": true,
    "publish_to_rep_store": true,
    "option_attrs": ["Size", "Color"],
    "category_id": 42,
    "collection_ids": [10, 20],
    "images_attributes": [
      { "position": 0, "image_url": "https://dam.fluid.app/..." }
    ],
    "variants_attributes": [
      {
        "title": "Small / Red",
        "sku": "WDG-001-SR",
        "is_master": true,
        "option_attrs": ["Small", "Red"],
        "track_quantity": false,
        "keep_selling": false,
        "bar_code": "123456789",
        "variant_countries_attributes": [
          {
            "active": true,
            "country_id": 214,
            "price": 29.99,
            "compare_price": 39.99,
            "wholesale": 29.99,
            "subscription_price": 29.99,
            "wholesale_subscription_price": 29.99,
            "cv": 0,
            "shipping": 0,
            "tax": 0
          }
        ],
        "images_attributes": [
          { "position": 0, "image_url": "https://dam.fluid.app/..." }
        ]
      }
    ],
    "search_engine_optimizer_attributes": {
      "title": "SEO Title",
      "description": "SEO meta description"
    }
  }
}
```

Response: `{ "product": { "id": 123, "title": "Widget", "slug": "widget" } }`.

## DAM Asset Upload Pipeline

Before products are created, all images are uploaded to Fluid DAM. Source: `src/import/steps/assets.ts`.

### Image collection

**CRITICAL: Only collect product-related and brand images.** Do NOT include site-wide images (hero banners, section backgrounds, decorative graphics, page content images). Those belong to the theme/site clone workflow.

`collectImageUrls()` deduplicates image URLs from these sources ONLY:
- `product.image_url` (featured image)
- `product.images[].url` (gallery images)
- `product.variants[].image_url` and `product.variants[].images[].url`
- `category.image_url`
- `brand.logo_url`, `brand.favicon_url`, `brand.og_image_url`

Returns a unique `string[]` of source URLs.

### Upload flow

`importAssets()` runs with **5 concurrent workers** (`UPLOAD_CONCURRENCY = 5`).

**Direct upload (recommended):**
```
1. Download source image:  fetch(sourceUrl) -> Buffer
2. Upload to Fluid DAM:
   POST /api/dam/assets  (multipart/form-data)
     Authorization: Bearer <FLUID_API_KEY>
     Fields: asset[file] (binary), asset[name] (string)
     -> { asset: { id, code, default_variant_url } }
```

The returned `default_variant_url` (e.g. `https://ik.imagekit.io/fluid/...`) is the DAM URL stored in `idMapping.assets`.

> **Note:** An older ImageKit 3-step flow exists (`imagekit_auth` -> ImageKit upload -> `backfill_imagekit`) but is unreliable — the auth endpoint doesn't return the `publicKey` needed for ImageKit's upload API. Use the direct `/api/dam/assets` multipart upload instead.

### File name sanitization

`normalizeDamAssetName()` cleans filenames before upload:
- Replace non-word characters (except `.`, `-`, space) with `-`
- Collapse consecutive hyphens and dots
- Fallback to `'unnamed-asset'` if empty

### MIME type guessing

`guessMimeType()` infers from file extension. Falls back to `'application/octet-stream'`.

### Upload variants

| Method | Use case |
|--------|----------|
| `uploadMedia(url, title)` | Remote URL — downloads then uploads via `POST /api/dam/assets` (main path for product import) |
| `uploadAsset(buffer, name)` | In-memory buffer — uploads directly via `POST /api/dam/assets` |

### Resumability

- URLs already in `idMapping.assets` are skipped (`filter` before processing).
- `idMapping` is persisted to `id-mapping.json` after the asset step completes.
- On re-run, only new/failed URLs are attempted.

### Error handling

- Per-URL errors are caught and logged — they don't stop other uploads.
- Failed URLs are tracked in `AssetStepResult.errors`.
- Product import falls back to original source URL when DAM URL is missing.

### ID mapping for images

After asset upload, `idMapping.assets` maps `sourceUrl -> damUrl`:

```typescript
idMapping.assets.set(sourceUrl, damUrl);
// Later in product import:
const image_url = idMapping.assets.get(img.url) ?? img.url;
```

## Key Implementation Rules

### Variant construction

- **Empty `variants` array** -> one synthetic master variant built from product-level `title`, `sku`, `price`, `compare_price`. Sets `is_master: true`, `option_attrs: []`, `track_quantity: false`, `keep_selling: false`.
- **Non-empty `variants`** -> first variant gets `is_master: true`, rest get `is_master: false`.
- Every variant needs `variant_countries_attributes` with a `country_id` (default 214 = US, fetched via `GET /api/settings/company_countries`).
- `compare_price` defaults to `0` when missing.
- **`sku` must be a string or omitted** — never send `null`. If source SKU is null/undefined, omit the field entirely.
- Fixed zero fields on variant country: `wholesale`, `subscription_price`, `wholesale_subscription_price` mirror `price`; `cv`, `shipping`, `tax` are `0`.

### Image URL resolution

Product and variant `image_url` values are replaced with DAM URLs from `idMapping.assets` when available. If an asset upload failed, the original URL is used as fallback.

```typescript
const image_url = idMapping.assets.get(img.url) ?? img.url;
```

### Category linking

`category_title` on the product is matched against `idMapping.categories` keys (the category's `source_id`, not display name). Returns Fluid's numeric `category_id`.

### Collection linking

`collection_titles` are matched against `idMapping.collections` keys (the collection title string). Unmatched titles are silently skipped.

### Metafields (product-level only)

After product creation, metafields are imported best-effort (errors swallowed):

1. Normalize `namespace` (max 20 chars) and `key` (max 30 chars): lowercase, replace non-alphanumeric with `_`, collapse runs, trim edges.
2. `POST /api/v2/metafield_definitions` — create definition once per unique `(namespace, key, value_type)`. Duplicates ignored.
3. `POST /api/v2/metafields` — create metafield with `resource_type: 'product'`, `resource_id`.
4. Value type mapping: `string` -> `single_line_text_field`, `integer` -> `number_integer`, `boolean` -> `boolean`, `json_string` -> `json`.

Variant-level metafields exist in the schema but are **not imported** in the current implementation.

### Deduplication and crash recovery

- **Skip if mapped:** `idMapping.products.has(source_id)` -> skip (supports resumable imports).
- **Duplicate detection:** errors containing `"already taken"` or `"already exists"` are silently ignored.
- **ID mapping persisted** to `id-mapping.json` after each import step via `saveIdMapping()`.

## Import Step Order (dependencies)

Products run as step 6 in the import pipeline. Earlier steps must complete first:

1. **Assets** -> uploads images to DAM, populates `idMapping.assets` (URL -> DAM URL)
2. **Categories** -> creates categories, populates `idMapping.categories` (source_id -> Fluid ID)
3. **Collections** -> creates collections from unique `collection_titles`, populates `idMapping.collections` (title -> Fluid ID)
4. **Country ID** -> resolved from config or `GET /api/settings/company_countries` (fallback 214)
5. **Products** -> uses all of the above

## FluidClient Methods (Product + DAM)

| Method | HTTP | Endpoint |
|--------|------|----------|
| `uploadMedia(url, title)` | POST | Download source -> `POST /api/dam/assets` (multipart: `asset[file]`, `asset[name]`) |
| `uploadAsset(buffer, name)` | POST | `POST /api/dam/assets` (multipart: `asset[file]`, `asset[name]`) |
| `createProduct(params)` | POST | `/api/company/v1/products` |
| `listProducts(page, perPage)` | GET | `/api/company/v1/products?page=&per_page=` |
| `deleteProduct(id)` | DELETE | `/api/company/v1/products/${id}` |
| `createMetafieldDefinition(params)` | POST | `/api/v2/metafield_definitions` |
| `createMetafield(params)` | POST | `/api/v2/metafields` |

DAM upload endpoint:

| Step | HTTP | Endpoint |
|------|------|----------|
| Upload | POST | `/api/dam/assets` (multipart: `asset[file]`, `asset[name]`) |

All calls go through `FluidClient.request()` which applies:
- **Rate limiting:** token bucket, 10 req/sec default
- **Retry:** 3 attempts, exponential backoff (1s base, 30s max), retries on 429 and 5xx only
- **Timeout:** 30s per request via `AbortSignal.timeout`
- **Auth:** `Authorization: Bearer ${apiKey}`

## Testing Patterns

Tests live in `src/import/__tests__/products.test.ts`.

### Mock client

```typescript
function createMockClient() {
  let nextId = 200;
  return {
    createProduct: vi.fn().mockImplementation(async () => ({
      id: nextId++,
      title: 'mock',
      slug: 'mock',
    })),
    createMetafieldDefinition: vi.fn().mockResolvedValue({}),
    createMetafield: vi.fn().mockResolvedValue({}),
  } as unknown as FluidClient;
}
```

### Product factory

```typescript
function makeProduct(overrides: Partial<ImportProduct> = {}): ImportProduct {
  return {
    source_id: 'prod-1',
    title: 'Test Product',
    description: '<p>Description</p>',
    price: 29.99,
    images: [{ url: 'https://example.com/img.jpg', position: 0 }],
    variants: [
      {
        source_id: 'var-1',
        title: 'Default',
        sku: 'TST-001',
        price: 29.99,
        option_attrs: [],
      },
    ],
    ...overrides,
  };
}
```

### What to assert

- `mockClient.createProduct` call args for nested `product.variants_attributes`, `variant_countries_attributes`, `images_attributes`, `category_id`, `collection_ids`, `search_engine_optimizer_attributes`
- `idMapping.products` populated with `source_id -> result.id`
- `StepResult.created` / `failed` / `errors` counts

## Source Files

| File | Purpose |
|------|---------|
| `src/extraction/extractor.ts` | Extraction router (fast-path vs AI, parallel orchestration) |
| `src/extraction/fast-path/shopify.ts` | Shopify JSON API -> ImportProduct mapping |
| `src/extraction/fast-path/woocommerce.ts` | WooCommerce REST API -> ImportProduct mapping |
| `src/extraction/fast-path/squarespace.ts` | Squarespace JSON -> ImportProduct mapping |
| `src/extraction/fast-path/bigcommerce.ts` | BigCommerce GraphQL -> ImportProduct mapping |
| `src/extraction/ai/product-extractor.ts` | Claude-powered per-page product extraction |
| `src/extraction/ai/category-extractor.ts` | Claude-powered category extraction from collection pages |
| `src/schemas/product.ts` | Zod schema + types |
| `src/import/steps/assets.ts` | DAM image upload pipeline |
| `src/import/steps/products.ts` | Product creation logic |
| `src/import/fluid-client.ts` | HTTP client (products + DAM upload) |
| `src/import/id-mapping.ts` | Source -> Fluid ID tracking |
| `src/import/importer.ts` | Orchestrates all import steps |
| `src/import/__tests__/products.test.ts` | Product import tests |
| `src/import/__tests__/fluid-client.test.ts` | Client tests (upload flow, retry) |
