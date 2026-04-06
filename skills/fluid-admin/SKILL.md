---
name: fluid-admin
description: >-
  Manage a Fluid Commerce store via API. Use when the user wants to create collections,
  activate/deactivate products, update navigation, change brand/checkout/tax/shipping settings,
  manage pages and policies, handle customers and inventory, configure webhooks, or perform
  any store administration task. Triggers on "update my Fluid store," "create a collection,"
  "deactivate products," "change the nav," "update settings," "manage products," "Fluid admin,"
  or any store management task requiring Fluid API access.
metadata:
  version: 1.0.0
---

# Fluid Admin

General-purpose skill for managing a Fluid Commerce store through its API. Unlike the import or clone skills which run fixed pipelines, this skill is an **interactive admin tool** — the user describes what they want, and you execute the right API calls.

---

## 1. Session Setup

### Collect Credentials

Before any API call, you need two things:

| Credential     | Example                              | How to get it                                    |
|----------------|--------------------------------------|--------------------------------------------------|
| **Fluid URL**  | `https://acme.fluid.app`            | The company's Fluid subdomain                    |
| **API Token**  | `PT-xxxxxxxx`                       | Developer API token from Fluid admin panel       |

Ask the user for both. Store them as shell variables for the session:

```bash
FLUID_URL="https://acme.fluid.app"
FLUID_TOKEN="PT-xxxxxxxx"
```

### Validate Credentials

Run these two calls in parallel to verify access and discover store context:

```bash
# 1. Validate token + get company info
curl -s -w "\n%{http_code}" "${FLUID_URL}/api/settings/company" \
  -H "Authorization: Bearer ${FLUID_TOKEN}"

# 2. Get active countries (needed for many operations)
curl -s -w "\n%{http_code}" "${FLUID_URL}/api/settings/company_countries" \
  -H "Authorization: Bearer ${FLUID_TOKEN}"
```

If either returns 401/403, the token is invalid. Stop and tell the user.

From the countries response, extract and note:
- **`id`** (top-level) = `company_country_id` — used in agreements, checkout, tax
- **`country.id`** (nested) = `country_id` — used in menus, variants, regions
- **`country.iso`** = country ISO code (e.g., `US`)

These IDs are **different** and used in different contexts. Getting them mixed up causes silent failures.

### Store Discovery (Optional)

If the user's request requires understanding current state, fetch what you need:

```bash
# Current products
curl -s "${FLUID_URL}/api/company/v1/products" -H "Authorization: Bearer ${FLUID_TOKEN}"

# Current collections
curl -s "${FLUID_URL}/api/company/v1/collections" -H "Authorization: Bearer ${FLUID_TOKEN}"

# Current menus
curl -s "${FLUID_URL}/api/menus" -H "Authorization: Bearer ${FLUID_TOKEN}"

# Current theme
curl -s "${FLUID_URL}/api/application_themes" -H "Authorization: Bearer ${FLUID_TOKEN}"

# Brand guidelines
curl -s "${FLUID_URL}/api/settings/brand_guidelines" -H "Authorization: Bearer ${FLUID_TOKEN}"
```

Only fetch what's relevant to the user's request.

---

## 2. Operation Catalog

Every Fluid admin operation maps to one or more API calls. Below is the full catalog organized by domain. Each operation links to a reference file with detailed payload structures.

### Products & Catalog
See [references/products-collections.md](references/products-collections.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create product | POST | `/api/company/v1/products` |
| List products | GET | `/api/company/v1/products` |
| Get product | GET | `/api/company/v1/products/:id` |
| Update product | PUT | `/api/company/v1/products/:id` |
| Delete product | DELETE | `/api/company/v1/products/:id` |
| Create category | POST | `/api/company/v1/categories` |
| List categories | GET | `/api/company/v1/categories` |
| Create collection | POST | `/api/company/v1/collections` |
| List collections | GET | `/api/company/v1/collections` |
| Update collection | PUT | `/api/company/v1/collections/:id` |
| Delete collection | DELETE | `/api/company/v1/collections/:id` |
| Add product to collection | POST | `/api/company/v1/collections/:id/add_product` |
| Remove product from collection | POST | `/api/company/v1/collections/:id/remove_product` |

### Navigation & Menus
See [references/navigation-content.md](references/navigation-content.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create menu | POST | `/api/menus` |
| List menus | GET | `/api/menus` |
| Get menu | GET | `/api/menus/:id` |
| Update menu | PUT | `/api/menus/:id` |
| Delete menu | DELETE | `/api/menus/:id` |

### Pages & Content
See [references/navigation-content.md](references/navigation-content.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create page | POST | `/api/company/v1/pages` |
| List pages | GET | `/api/company/v1/pages` |
| Update page | PUT | `/api/company/v1/pages/:id` |
| Delete page | DELETE | `/api/company/v1/pages/:id` |

### Policies & Agreements
See [references/navigation-content.md](references/navigation-content.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create agreement | POST | `/api/agreements` |
| List agreements | GET | `/api/agreements` |
| Update agreement | PATCH | `/api/agreements/:id` |
| Delete agreement | DELETE | `/api/agreements/:id` |
| Clone agreement | POST | `/api/agreements/:id/clone` |

### Brand & Settings
See [references/settings-config.md](references/settings-config.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Update brand guidelines | PATCH | `/api/settings/brand_guidelines` |
| Update social media | PATCH | `/api/settings/social_media` |
| Get checkout settings | GET | `/api/settings/checkout` |
| Update checkout settings | PUT | `/api/settings/checkout` |
| Update company settings | PATCH | `/api/settings/company` |
| Get company countries | GET | `/api/settings/company_countries` |
| Add country | POST | `/api/settings/company_countries` |
| List languages | GET | `/api/settings/languages` |
| Enable language | POST | `/api/settings/languages` |

### Tax & Shipping
See [references/settings-config.md](references/settings-config.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Set tax option | PATCH | `/api/companies/set_tax_option` |
| Set tax class | PATCH | `/api/companies/set_tax_class` |
| List tax categories | GET | `/api/tax_categories` |
| List warehouses | GET | `/api/settings/warehouses` |
| Create warehouse | POST | `/api/settings/warehouses` |
| Assign warehouse to country | POST | `/api/settings/warehouses/:id/assign_to_country` |
| Set shipping config | POST | `/api/companies/set_shipping` |

### Customers
See [references/customers-commerce.md](references/customers-commerce.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List customers | GET | `/api/customers` |
| Get customer | GET | `/api/customers/:id` |
| Create customer | POST | `/api/customers` |
| Update customer | PATCH | `/api/customers/:id` |

### Inventory
See [references/customers-commerce.md](references/customers-commerce.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List inventory levels | GET | `/api/inventory_levels` |
| Set inventory level | POST | `/api/inventory_levels/set` |
| Adjust inventory | POST | `/api/inventory_levels/adjust` |
| Bulk set inventory | POST | `/api/inventory_levels/bulk_upsert` |

### Webhooks
See [references/advanced.md](references/advanced.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List webhooks | GET | `/api/webhooks` |
| Create webhook | POST | `/api/webhooks` |
| Delete webhook | DELETE | `/api/webhooks/:id` |
| Get payload example | GET | `/api/webhooks/payload_example?event=:event` |

### Domains
See [references/advanced.md](references/advanced.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List domains | GET | `/api/domains` |
| Register domain | POST | `/api/domains` |
| Check DNS propagation | POST | `/api/domains/:id/check_cname_propagation` |
| Verify domain | POST | `/api/domains/:id/verify_domain` |

### Metafields
See [references/advanced.md](references/advanced.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create metafield definition | POST | `/api/v2/metafield_definitions` |
| Create metafield value | POST | `/api/v2/metafields` |

### Compliance
See [references/advanced.md](references/advanced.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Run compliance scan | POST | `/api/compliance` |
| Get scan results | GET | `/api/compliance/:id` |
| List scans | GET | `/api/compliance` |

### Regional Rules
See [references/advanced.md](references/advanced.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List region rules | GET | `/api/theme_region_rules` |
| Create region rule | POST | `/api/theme_region_rules` |
| Update region rule | PATCH | `/api/theme_region_rules/:id` |
| Delete region rule | DELETE | `/api/theme_region_rules/:id` |

### Image & Asset Upload
See [references/assets-upload.md](references/assets-upload.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Upload asset | POST | `https://upload.fluid.app/upload` |
| Upload theme resource (text) | PUT | `/api/application_themes/:id/resources` |
| Upload theme resource (image) | PUT | `/api/application_themes/:id/resources` |

### Orders & Fulfillment (42 endpoints)
See [references/orders-fulfillment.md](references/orders-fulfillment.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List orders | GET | `/api/v2/orders` or `/api/v202506/orders` |
| Get order | GET | `/api/v2/orders/:id` |
| Create order | POST | `/api/orders` |
| Update order | PATCH | `/api/orders/:id` |
| Cancel order | PATCH | `/api/v2/orders/:id/cancel` |
| Archive/Unarchive order | PATCH | `/api/v2/orders/:id/archive` |
| Create fulfillment | POST | `/api/order_fulfillments` |
| Create refund | POST | `/api/refunds` |
| Create tracking info | POST | `/api/tracking_informations` |
| Export orders CSV | GET | `/api/v202506/orders/export_csv` |

### Products Extended (28 endpoints)
See [references/products-extended.md](references/products-extended.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create product bundle | POST | `/api/company/v1/products/:id/product_bundles` |
| Manage product images | POST/GET/DELETE | `/api/company/v1/products/:id/images` |
| Link subscription plan | POST | `/api/company/v1/products/:id/subscription_plans` |
| Create/update variant | POST/PUT | `/api/company/v1/variants` |
| Bulk update variants | PUT | `/api/company/v1/variants/bulk_update` |
| Manage variant countries | POST | `/api/company/v1/variants/:id/variant_countries` |
| Manage tags | GET/POST | `/api/company/tags` |
| Global search | POST | `/api/search` |

### MLM & Network (65 endpoints)
See [references/mlm-network.md](references/mlm-network.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List/create/update reps | GET/POST/PATCH | `/api/v2/reps` |
| List/create/update users | GET/POST/PATCH | `/api/v202506/users` |
| Manage ranks | GET/POST/PATCH | `/api/v202506/ranks` |
| Manage trees | GET/POST/PUT/DELETE | `/api/trees` |
| Manage tree nodes | GET/POST/PUT/DELETE | `/api/trees/:id/tree_nodes` |
| Manage enrollment packs | GET/POST/PATCH/DELETE | `/api/enrollment_packs` |
| Manage points ledgers | GET/POST | `/api/v202506/customers/:id/points_ledgers` |
| Manage subscription plans | GET/POST/PUT/DELETE | `/api/subscription_plans` |
| Manage subscriptions | GET/POST/PUT | `/api/subscriptions` |
| Pause/resume/cancel sub | POST | `/api/subscriptions/:token/pause\|resume\|cancel` |

### CRM & Engagement (65 endpoints)
See [references/crm-engagement.md](references/crm-engagement.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Manage contacts | GET/POST/PUT/DELETE | `/api/company/contacts` |
| Customer notes | GET/POST | `/api/customer_notes` |
| Conversations & messages | GET/POST | `/api/company/messaging/conversations` |
| Manage forms | GET/POST/PUT/DELETE | `/api/forms` |
| Manage events | GET/POST/PATCH/DELETE | `/api/company/events` |
| Manage announcements | GET/POST/PUT/DELETE | `/api/company/announcements` |
| Manage labels | GET/POST/PUT/DELETE | `/api/company/labels` |
| Manage media content | GET/POST/PUT/DELETE | `/api/company/media` |
| Manage libraries | GET/POST/PATCH/DELETE | `/api/company/libraries` |

### Platform & Configuration (86 endpoints)
See [references/platform-config.md](references/platform-config.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Manage admins | GET/POST/PATCH/DELETE | `/api/v2/admins` |
| Manage roles | GET/POST/PUT/DELETE | `/api/company/roles` |
| Display settings | GET/PATCH | `/api/settings/displays` |
| Feature flags | GET/POST/PUT/DELETE | `/api/v202506/feature_flags` |
| Global embeds | GET/POST/PUT/DELETE | `/api/global_embeds` |
| Sitemap | GET/PATCH | `/api/v2025-06/sitemap` |
| Droplets & installations | GET/POST/PUT/DELETE | `/api/droplets` |
| Custom pages | GET/POST/PUT/DELETE | `/api/company/custom_pages` |
| Trainings | GET/POST/PATCH/DELETE | `/api/v202506/trainings` |
| Tiles & mobile widgets | GET/POST/PATCH/DELETE | `/api/company/tiles` |

### Payments & Carts (71 endpoints)
See [references/payments-carts.md](references/payments-carts.md)

| Operation | Method | Endpoint |
|-----------|--------|----------|
| List transactions | GET | `/api/v202506/transactions` |
| Create/get/update payment | POST/GET/PATCH | `/api/v202506/payments` |
| Manage payment accounts | GET/POST/PUT/DELETE | `/api/payment_accounts` |
| Create cart | POST | `/api/carts` |
| Get/update cart | GET/PATCH | `/api/carts/:cart_token` |
| Add/remove cart items | POST/DELETE | `/api/carts/:cart_token/items` |
| Apply/remove discount | POST/DELETE | `/api/carts/:cart_token/discount` |
| Cart checkout | POST | `/api/carts/:cart_token/checkout` |
| Fluid Pay methods | GET/POST/DELETE | `/api/fluid_pay/payment_methods` |

---

## 3. Making API Calls

### Standard curl format

```bash
# GET (read)
curl -s "${FLUID_URL}/api/endpoint" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json"

# POST/PUT/PATCH (write)
curl -s -X POST "${FLUID_URL}/api/endpoint" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "resource": {
      "field": "value"
    }
  }'

# DELETE
curl -s -X DELETE "${FLUID_URL}/api/endpoint" \
  -H "Authorization: Bearer ${FLUID_TOKEN}"
```

Always include `-w "\n%{http_code}"` on write operations to check the status code.

### Pagination

List endpoints return paginated results. Use `?page=1&per_page=50` parameters. Check response for `total_count` or `meta.total` to know if more pages exist.

```bash
curl -s "${FLUID_URL}/api/company/v1/products?page=1&per_page=50" \
  -H "Authorization: Bearer ${FLUID_TOKEN}"
```

---

## 4. Safety Rules

### Always GET before PUT/PATCH on settings
Settings endpoints (checkout, brand, company, onboarding) **overwrite the entire object**. Always fetch current state first, merge your changes, then write back.

### Never send null values or empty arrays
Fluid rejects `"field": null` and `"field": []` with 422 errors. **Omit the key entirely** if the value is empty.

### Confirm destructive operations with the user
Before DELETE operations or bulk deactivations, list what will be affected and ask for confirmation.

### Rate limiting
Fluid allows ~10 requests/second. For bulk operations, use 5-10 concurrent workers. If you get 429, back off and retry (exponential backoff, 1s-30s).

### ID mapping matters
See [references/api-patterns.md](references/api-patterns.md) for the critical distinction between `company_country_id` and `country_id`, plus other gotchas.

---

## 5. Multi-Step Workflows

Many user requests require chaining operations. Common patterns:

### "Create a collection of X products"
1. GET `/api/company/v1/products` to find/filter products
2. POST `/api/company/v1/collections` to create the collection
3. POST `/api/company/v1/collections/:id/add_product` for each product

### "Deactivate all products in category X"
1. GET `/api/company/v1/products?category_id=X` to list products
2. PUT `/api/company/v1/products/:id` with `"active": false` for each

### "Update the main navigation"
1. GET `/api/menus` to find the current main menu
2. PUT `/api/menus/:id` with updated `menu_items_attributes`

### "Set up shipping for a new country"
1. POST `/api/settings/company_countries` to add the country
2. POST `/api/settings/warehouses` (if needed)
3. POST `/api/settings/warehouses/:id/assign_to_country`
4. POST `/api/companies/set_shipping` to configure rates

### "Fulfill and ship an order"
1. GET `/api/v2/orders/:id` to get order details and line items
2. POST `/api/order_fulfillments` with order items + tracking info
3. Notification sent automatically if `send_fulfillment_notification: true`

### "Set up a subscription plan with products"
1. POST `/api/subscription_plans` to create the plan
2. POST `/api/company/v1/products/:id/subscription_plans` to link products
3. Customers can now subscribe at checkout

### "Onboard a new rep"
1. POST `/api/v2/reps` to create the rep account
2. POST `/api/enrollment_packs` to create their starter pack (if needed)
3. POST `/api/trees/:tree_id/tree_nodes` to place them in the downline

### "Add a tracking pixel globally"
1. POST `/api/global_embeds` with the script code and `placement: "head"`

---

## 6. Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| 200/201 | Success | Proceed |
| 401 | Unauthorized | Token invalid or expired — ask user for new token |
| 403 | Forbidden | Token lacks permission for this operation |
| 404 | Not found | Resource doesn't exist — verify the ID |
| 422 | Validation error | Check payload — usually null fields or missing required fields |
| 429 | Rate limited | Back off and retry after 1-2 seconds |
| 500+ | Server error | Retry up to 3 times with exponential backoff |

Always show the user the error response body — it usually contains specific field-level errors.

---

## 7. Response to User

After each operation:
1. **Confirm what was done** — e.g., "Created collection 'Summer Sale' with 8 products"
2. **Show key IDs** — the user may need them for follow-up operations
3. **Note any warnings** — e.g., "3 products were already inactive"
4. **Suggest next steps** if relevant — e.g., "Want me to add this collection to the nav?"
