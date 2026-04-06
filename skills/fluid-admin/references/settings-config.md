# Settings & Configuration API

## Brand Guidelines

### Update Brand
```
PATCH /api/settings/brand_guidelines
```

```json
{
  "brand_guidelines": {
    "name": "Acme Co",
    "logo_url": "https://ik.imagekit.io/fluid/.../logo.png",
    "favicon_url": "https://ik.imagekit.io/fluid/.../favicon.png",
    "app_icon_url": "https://ik.imagekit.io/fluid/.../favicon.png",
    "og_image_url": "https://ik.imagekit.io/fluid/.../og.jpg",
    "primary_color": "#FF6B35",
    "secondary_color": "#1A1A1A",
    "primary_font": "Montserrat",
    "heading_font": "Montserrat"
  }
}
```

**Rules:**
- All four image URLs must be set. Never leave blank.
- `favicon_url` and `app_icon_url` should be the same image.
- If no OG image exists, use the logo as fallback.
- Colors are hex format with `#` prefix.
- Fonts must be Google Fonts names.

### Get Brand
```
GET /api/settings/brand_guidelines
```

---

## Social Media

### Update Social Links
```
PATCH /api/settings/social_media
```

```json
{
  "social_media": {
    "facebook": "https://facebook.com/acmeco",
    "instagram": "https://instagram.com/acmeco",
    "twitter": "https://twitter.com/acmeco",
    "tiktok": "https://tiktok.com/@acmeco",
    "youtube": "https://youtube.com/@acmeco"
  }
}
```

Only include platforms that have URLs. Omit platforms with no presence.

---

## Checkout Settings

### Get Checkout
```
GET /api/settings/checkout
```

### Update Checkout
```
PUT /api/settings/checkout
```

```json
{
  "checkout": {
    "collect_phone": true,
    "require_phone": false,
    "require_billing_zip": true,
    "primary_button_color": "#1a1a1a",
    "text_color": "#ffffff"
  }
}
```

**Important:** This is a PUT endpoint — it overwrites the entire checkout config. Always GET first, merge your changes, then PUT back.

---

## Company Settings

### Update Company
```
PATCH /api/settings/company
```

Used for general company settings including shipping preferences.

---

## Company Countries

### List Countries
```
GET /api/settings/company_countries
```

Response structure (critical — two different IDs):
```json
[
  {
    "id": 55938,              // <-- company_country_id (used in agreements, checkout, tax)
    "country": {
      "id": 214,              // <-- country_id (used in menus, variants, regions)
      "name": "United States",
      "iso": "US"
    },
    "currency": {
      "iso_code": "USD"
    }
  }
]
```

### Add Country
```
POST /api/settings/company_countries
```

```json
{
  "company_country": {
    "country_id": 38,
    "currency_id": 2
  }
}
```

---

## Languages

### List Languages
```
GET /api/settings/languages
```

### Enable Language
```
POST /api/settings/languages
```

```json
{
  "language": {
    "iso": "es"
  }
}
```

---

## Tax Configuration

### Set Tax Option
```
PATCH /api/companies/set_tax_option
```

```json
{
  "tax_option": {
    "tax_included_in_price": false,
    "charge_tax_on_shipping": true
  }
}
```

### Set Tax Class
```
PATCH /api/companies/set_tax_class
```

```json
{
  "tax_class": {
    "tax_category_id": 456
  }
}
```

### List Tax Categories
```
GET /api/tax_categories
```

Returns a hierarchical list. Common top-level categories:
- General (default)
- Food & Beverage
- Clothing
- Digital Goods
- Health & Beauty

---

## Shipping & Warehouses

### List Warehouses
```
GET /api/settings/warehouses
```

### Create Warehouse
```
POST /api/settings/warehouses
```

```json
{
  "warehouse": {
    "name": "Main Warehouse",
    "address1": "123 Main St",
    "city": "Austin",
    "province": "TX",
    "postal_code": "78701",
    "country_iso": "US",
    "active": true
  }
}
```

### Assign Warehouse to Country
```
POST /api/settings/warehouses/:id/assign_to_country
```

```json
{
  "country_id": 214
}
```

### Configure Shipping
```
POST /api/companies/set_shipping
```

```json
{
  "shipping": {
    "free_shipping_threshold": 75.00,
    "manual_rates": [
      {
        "name": "Standard Shipping",
        "price": 5.99,
        "min_order": 0,
        "max_order": 74.99
      },
      {
        "name": "Free Shipping",
        "price": 0,
        "min_order": 75.00
      }
    ]
  }
}
```

---

## Complete Settings Workflow

When setting up a new store's configuration:

```bash
# 1. Brand
curl -s -X PATCH "${FLUID_URL}/api/settings/brand_guidelines" ...

# 2. Social (in parallel with brand)
curl -s -X PATCH "${FLUID_URL}/api/settings/social_media" ...

# 3. Checkout
CHECKOUT=$(curl -s "${FLUID_URL}/api/settings/checkout" -H "Authorization: Bearer ${FLUID_TOKEN}")
# Merge changes, then:
curl -s -X PUT "${FLUID_URL}/api/settings/checkout" ...

# 4. Tax
curl -s -X PATCH "${FLUID_URL}/api/companies/set_tax_option" ...
curl -s -X PATCH "${FLUID_URL}/api/companies/set_tax_class" ...

# 5. Warehouse + Shipping
curl -s -X POST "${FLUID_URL}/api/settings/warehouses" ...
curl -s -X POST "${FLUID_URL}/api/settings/warehouses/:id/assign_to_country" ...
curl -s -X POST "${FLUID_URL}/api/companies/set_shipping" ...
```
