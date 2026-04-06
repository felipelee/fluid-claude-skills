# Products Extended: Bundles, Images, Variants, Tags & Search

## Product Bundles

Create bundle products by linking a parent product to bundled variants.

### Create Bundle
```
POST /api/company/v1/products/:product_id/product_bundles
```

```json
{
  "bundled_variant_id": 456,
  "quantity": 2,
  "display_externally": true
}
```

### List Bundles
```
GET /api/company/v1/products/:product_id/product_bundles
```

### Update Bundle
```
PATCH /api/company/v1/products/:product_id/product_bundles/:id
```

### Delete Bundle
```
DELETE /api/company/v1/products/:product_id/product_bundles/:id
```

---

## Product Images

Manage additional images beyond the main `image_url` on a product.

### Create Product Image
```
POST /api/company/v1/products/:product_id/images
```

```json
{
  "image_url": "https://ik.imagekit.io/fluid/.../image2.jpg",
  "position": 2,
  "alt": "Product side view"
}
```

### List Product Images
```
GET /api/company/v1/products/:product_id/images
```

### Update Product Image
```
PATCH /api/company/v1/products/:product_id/images/:id
```

### Delete Product Image
```
DELETE /api/company/v1/products/:product_id/images/:id
```

---

## Product Subscription Plans

Link subscription plans to products for recurring purchases.

### Add Subscription Plan to Product
```
POST /api/company/v1/products/:product_id/subscription_plans
```

```json
{
  "subscription_plan_id": 123,
  "discount_percentage": 10
}
```

### Update Product Subscription Plan
```
PATCH /api/company/v1/products/:product_id/subscription_plans/:id
```

### Delete Product Subscription Plan
```
DELETE /api/company/v1/products/:product_id/subscription_plans/:id
```

---

## Variants (Standalone Management)

Manage variants independently of their parent product.

### Create Variant
```
POST /api/company/v1/variants
```

```json
{
  "variant": {
    "product_id": 789,
    "title": "Blue / XL",
    "sku": "HOODIE-BLU-XL",
    "price": 49.99,
    "compare_at_price": 69.99,
    "option1": "Blue",
    "option2": "XL",
    "weight": 0.5,
    "weight_unit": "kg",
    "image_url": "https://ik.imagekit.io/fluid/.../blue-xl.jpg",
    "active": true
  }
}
```

### Get Variant
```
GET /api/company/v1/variants/:id
```

### Update Variant
```
PUT /api/company/v1/variants/:id
PATCH /api/company/v1/variants/:id
```

### Bulk Update Variants
```
PUT /api/company/v1/variants/bulk_update
```

```json
{
  "variants": [
    { "id": 456, "price": 39.99 },
    { "id": 457, "price": 44.99, "active": false }
  ]
}
```

### Product-scoped Variant Endpoints
```
GET  /api/company/products/:product_id/variants           # List product variants
POST /api/company/products/:product_id/variants           # Create variant under product
GET  /api/company/products/:product_id/variants/:id       # Get specific variant
PUT  /api/company/products/:product_id/variants/:id       # Update variant
DELETE /api/company/products/:product_id/variants/:id     # Delete variant
```

---

## Variant Countries

Country-specific pricing and availability for variants.

### List Variant Countries
```
GET /api/v1/variants/variant_countries
```

### Create Variant Country
```
POST /api/company/v1/variants/:variant_id/variant_countries
```

```json
{
  "variant_country": {
    "country_id": 214,
    "price": 49.99,
    "compare_at_price": 69.99,
    "active": true
  }
}
```

### Bulk Update Variant Countries
```
POST /api/v1/variants/variant_countries/bulk_update
```

---

## Variant Images

### Create Variant Image
```
POST /api/company/v1/variants/:variant_id/images
```

```json
{
  "image_url": "https://ik.imagekit.io/fluid/.../variant-img.jpg",
  "position": 1
}
```

---

## Tags

### List Tags
```
GET /api/company/tags
```

### Create Tags
```
POST /api/company/tags
```

```json
{
  "tags": ["summer", "new-arrival", "sale"]
}
```

Tags can be applied to products via the product create/update endpoints.

---

## Search

### Global Search
```
POST /api/search
```

```json
{
  "query": "hoodie",
  "types": ["products", "collections", "pages"]
}
```

Searches across all searchable models (products, collections, pages, etc.).
