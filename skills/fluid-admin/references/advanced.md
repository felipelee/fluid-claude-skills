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

## Regional Rules

Control which regions can access the store and redirect blocked regions.

### Create Region Rule
```
POST /api/theme_region_rules
```

```json
{
  "theme_region_rule": {
    "application_theme_template_id": 123,
    "region_code": "US-MT",
    "active": true,
    "redirect_type": "302",
    "redirect_url": "/not-available-in-your-state",
    "description": "Montana - not approved for operations",
    "priority": 1
  }
}
```

**Key fields:**
- `region_code` — ISO 3166-2 format (e.g., `US-CA` for California, `CA-ON` for Ontario)
- `redirect_type` — `"301"` (permanent) or `"302"` (temporary)
- `redirect_url` — Where blocked visitors go
- `application_theme_template_id` — Get from `GET /api/application_themes`

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
```
POST /api/redirects
```

```json
{
  "redirect": {
    "path": "/old-page",
    "target": "/new-page",
    "type": "301"
  }
}
```

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
