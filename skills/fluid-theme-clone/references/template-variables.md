# Template Variables & Scopes

Complete reference of which data is available on each page type. Source: https://docs.fluid.app/docs/themes/theme-variables

---

## Scope Rules (STRICT)

1. Each page type exposes a specific set of data (its "template scope")
2. Sections can only use data provided by their page's scope
3. **Global variables are always available on every page**
4. Referencing data not in scope will render empty
5. Do NOT assume cross-page access (e.g., `product.*` is not available on Home)

---

## Global Variables (Available on ALL Pages)

### Company (`company.*`)
```
company.id                  → Company id
company.name                → Company name
company.logo_url            → Company logo url
company.shop_page_url       → Shop page url
company.checkout_url        → Checkout url
company.subdomain           → Company subdomain
company.home_page_url       → Home page url
company.company_color       → Company primary color
```

### Request (`request.*`)
```
request.path                → Request path
request.host                → Request host
request.page_type           → Page type (shop, product, etc.)
request.query_parameters    → Query parameters
```

### Affiliate (`affiliate.*`)
```
affiliate.logged_in_rep_for_store → Is affiliate logged in?
affiliate.name                    → Affiliate name
affiliate.email                   → Affiliate email
affiliate.my_site_url             → Affiliate my site url
affiliate.sign_in_url             → Sign in url
affiliate.sign_out_url            → Sign out url
```

### Localization (`localization.*`)
```
localization.country              → Current Country object
localization.language             → Current Language object
localization.available_countries  → Array of country objects
localization.available_languages  → Array of language objects
```

### Products (`products`)
Global array of all products. Each product has:
```
product.id, product.title, product.url, product.price,
product.description, product.short_description,
product.images[].src, product.out_of_stock,
product.subscription_price, product.allow_subscription,
product.selected_or_first_available_variant.price,
product.ratings, product.reviews[].body,
product.tags[], product.variants[], product.metafields
```

### Collections (`collections`)
Global array of collections. Each has: `title`, `products[]`, and each product's `title`, `url`, `price`, `images`.

### Enrollment Packs (`enrollment_packs`)
Global array with: `title`, `price`, `images`, `description`, `membership_products[]`, `subscription_products[]`.

---

## Per-Template Variables

### Home Template
- `base_url`, `logo_url`, `shop_url`
- `products_pagination` (total_count, current_page, per_page)
- `enrollment_packs[]` (detailed enrollment pack objects)

### Product Template
- `product.*` — Full product object:
  - `title`, `url`, `id`, `description`, `short_description`, `feature_text`
  - `price`, `subscription_price`, `unit_price`
  - `images[]` (with `src`, `aspect_ratio`, `media_type`)
  - `featured_media`, `media` (alias of images)
  - `variants[]` (with `id`, `title`, `image_url`, `option_values[]`, `variant_countries[]`)
  - `selected_or_first_available_variant`
  - `options_with_values[]`
  - `subscription_plans[]`
  - `recommendations[]` (with full product-like objects)
  - `ratings`, `reviews[]`
  - `out_of_stock`, `available_for_country`, `buyable_quantity`
  - `tags[]`, `metadata`, `metafields`
- `all_products[]` — Array of all products
- `current_user_token`, `shop_path`

**Deprecated fields** (avoid these): bare `title`, `introduction`, `description`, `price`, `subscription_price`, `images`, `ratings`, `reviews` at root level. Use `product.title`, `product.price`, etc. instead.

### Shop/Collection Template
- `collection.*`:
  - `all_products_count`, `products_count`
  - `filters[]` (with `label`, `values[]`, `url_to_add`, `url_to_remove`)
  - `sort_options[]`
  - `products[]`
- `pagination` (total_count, current_page, per_page, pagination_html)
- `search_query`, `sorted_by`
- `options[]`, `categories[]`, `price_ranges[]`

### Cart Template
- `cart.*`:
  - `id`, `cart_token`
  - `amount_total`, `amount_total_in_currency`
  - `sub_total`, `tax_total`, `shipping_total`, `discount_total` (each with `_in_currency` variant)
  - `items[]` (each with `product`, `quantity`, `price`, `variant_id`, `variant_title`)
  - `checkout_url`
  - `currency_code`, `currency_symbol`

### Media Template
- `id`, `title`, `kind`, `description`
- `embed_url`, `video_url`, `pdf_url`, `image_url`, `powerpoint_url`
- `poster`, `cta_url`, `cta_button_text`
- `comments[]`, `social_media`

### Enrollment Pack Template
- `enrollment_pack.*` — Full enrollment pack object

### Library Template
- `library_items[]` — Mixed array (products, enrollment packs, media)

### My Site Template
- `fluid_affiliate.*` — Affiliate profile, social links, favorites

### Join Template
- `collection.enrollment_packs[]` — Enrollment pack listing with pagination

---

## Defensive Usage Patterns

### Always provide fallbacks
```liquid
{{ company.name | default: 'Company' }}
{{ product.title | default: 'Product Title' }}
```

### Guard optional structures
```liquid
{% if product and product.images %}
  <img src="{{ product.images[0].src }}" alt="{{ product.title | default: 'Product' }}">
{% endif %}
```

### Do / Don't Examples

**Home template:**
- DO: Use `products` (Global) to render a product list
- DON'T: Use `media.embed_url` — not available on Home

**Product template:**
- DO: Use `product.title`, `product.images`, `product.selected_or_first_available_variant.price`
- DON'T: Use `collection.filters` — not guaranteed on Product pages

**Shop/Collection template:**
- DO: Use `collection.filters` and `collection.products`
- DON'T: Use `product.selected_or_first_available_variant` — product-specific fields are only on Product pages

---

## Global Theme Settings

Defined in `config/settings_schema.json`. Accessed via `settings.*` (NOT `section.settings.*`):

```liquid
{{ settings.primary_color }}
{{ settings.logo_url }}
```
