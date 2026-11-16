# Advanced API: Webhooks, Domains, Metafields, Compliance & Regional Rules

## Webhooks

### Create Webhook
```
POST /api/webhooks
```

```json
{
  "webhook": {
    "url": "https://example.com/webhooks/orders",
    "events": ["order_completed", "order_shipped"]
  }
}
```

**Available events:**
- Cart: `cart_abandoned`, `cart_updated`
- Contacts: `contact_created`, `contact_updated`
- Events: `event_created`, `event_deleted`, `event_updated`
- Orders: `order_cancelled`, `order_completed`, `order_updated`, `order_shipped`, `order_refunded`
- Forms: `popup_submitted`
- Products: `product_created`, `product_updated`, `product_destroyed`
- Subscriptions: `subscription_started`, `subscription_paused`, `subscription_cancelled`
- Users: `user_created`, `user_updated`, `user_deactivated`

### List Webhooks
```
GET /api/webhooks
```

### Delete Webhook
```
DELETE /api/webhooks/:id
```

### Get Payload Example
```
GET /api/webhooks/payload_example?event=order_completed
```

Returns a sample payload for the given event type. Useful for understanding webhook data structure before building integrations.

---

## Domains

### Register Domain
```
POST /api/domains
```

```json
{
  "domain": {
    "name": "shop.acme.com"
  }
}
```

### List Domains
```
GET /api/domains
```

### Check DNS Propagation
```
POST /api/domains/:id/check_cname_propagation
```

Call this after the user has added CNAME records. Returns whether DNS has propagated.

### Verify Domain
```
POST /api/domains/:id/verify_domain
```

### Confirm CNAME
```
POST /api/domains/:id/confirm_cname_for_domain
```

### Domain Setup Flow
1. POST `/api/domains` to register
2. Tell user to add CNAME record: `shop.acme.com` → (value from response)
3. Poll `check_cname_propagation` until success
4. POST `verify_domain`
5. POST `confirm_cname_for_domain`

---

## Metafields

Metafields allow custom data on products, variants, pages, etc.

### Create Metafield Definition
```
POST /api/v2/metafield_definitions
```

```json
{
  "metafield_definition": {
    "name": "Material",
    "namespace": "custom",
    "key": "material",
    "type": "single_line_text",
    "owner_type": "Product"
  }
}
```

**Types:** `single_line_text`, `multi_line_text`, `number_integer`, `number_decimal`, `boolean`, `date`, `url`, `json`

**Owner types:** `Product`, `Variant`, `Page`, `Collection`, `Customer`

### Create Metafield Value
```
POST /api/v2/metafields
```

```json
{
  "metafield": {
    "namespace": "custom",
    "key": "material",
    "value": "100% Organic Cotton",
    "type": "single_line_text",
    "owner_type": "Product",
    "owner_id": 789
  }
}
```

---

## Compliance Scanning

### Run Compliance Scan
```
POST /api/compliance
```

Initiates an automated compliance scan of the store.

### Get Scan Results
```
GET /api/compliance/:id
```

Response:
```json
{
  "compliance": {
    "id": "scan-123",
    "score": 95,
    "status": "excellent",
    "summary": "Store passes most compliance checks",
    "scanned_at": "2024-01-15T10:30:00Z",
    "compliance_issues": [
      {
        "severity": "warning",
        "category": "privacy",
        "message": "Missing cookie consent banner"
      }
    ]
  }
}
```

**Status values:** `"unknown"`, `"poor"`, `"fair"`, `"good"`, `"excellent"`

### List All Scans
```
GET /api/compliance
```

---

## Sitemap Routes, Country Routes and Redirects

Theme region rules are the routes on the admin's Sitemap page. The API reference calls them "sitemap routes". One rule sets what visitors from one country see at a storefront path: a theme template, a redirect, or nothing (404).

### Create Region Rule
```
POST /api/theme_region_rules
```

This example sends Canadian visitors to another page:

```json
{
  "theme_region_rule": {
    "route_path": "products/starter-kit",
    "region_code": "CA",
    "redirect_type": "redirect",
    "redirect_url": "/home/pages/not-available-in-canada",
    "redirect_status_code": 302,
    "description": "Starter kit not sold in Canada"
  }
}
```

**Key fields:**
- `route_path`: the storefront path without its leading slash or credit segment (required).
- `region_code`: a two-letter country code such as `CA`, or `default` for every country. Rules match countries only. State codes such as `US-MT` never match.
- `redirect_type`: `template`, `redirect` or `disabled`. It isn't an HTTP status.
- `redirect_status_code`: `301` (permanent) or `302` (temporary, the default).
- `redirect_url`: where redirected visitors go.
- `application_theme_template_id`: required for `template` rules. Get it from `GET /api/application_themes`.
- `route_kind`: `non_credit` for a path that answers without a `/<credit>/` prefix, such as `/old-page`. Only custom paths can use it.

A `default` rule works only on custom paths. Paths under `products/`, `pages/`, `collections/`, `categories/`, `media/`, `enrollments/` or `libraries/`, and `shop` and `join`, can take country rules only.

### List Region Rules
```
GET /api/theme_region_rules
```

### Update Region Rule
```
PATCH /api/theme_region_rules/:id
```

### Delete Region Rule
```
DELETE /api/theme_region_rules/:id
```

---

## Discounts (if applicable)
```
POST /api/v2025-06/discounts
```

```json
{
  "discount": {
    "title": "SUMMER20",
    "type": "percentage",
    "value": 20,
    "starts_at": "2024-06-01T00:00:00Z",
    "ends_at": "2024-08-31T23:59:59Z",
    "usage_limit": 1000,
    "once_per_customer": true
  }
}
```

## URL Redirects

Create a redirect as a sitemap route. It then appears on the admin's Sitemap page. Never use `/api/redirects`: that endpoint is deprecated, and the Sitemap page doesn't show its redirects.

```
POST /api/theme_region_rules
```

```json
{
  "theme_region_rule": {
    "route_path": "old-page",
    "region_code": "default",
    "route_kind": "non_credit",
    "redirect_type": "redirect",
    "redirect_url": "/home/pages/new-page",
    "redirect_status_code": 301
  }
}
```

This redirects `/old-page` to `/home/pages/new-page` with a 301 for visitors from every country. Send one request per URL. The call is an upsert on `route_path` and `region_code`, so it's safe to re-run.

## Blog Posts
```
POST /api/posts
```

```json
{
  "post": {
    "title": "Welcome to Our Store",
    "body": "<p>Content here...</p>",
    "published": true,
    "tags": ["news", "launch"]
  }
}
```
