# Products, Categories & Collections API

## Products

### Create Product
```
POST /api/company/v1/products
```

```json
{
  "product": {
    "title": "Classic Hoodie",
    "description": "<p>Soft cotton hoodie</p>",
    "source_type": "manual",
    "source_id": "manual-001",
    "sku": "HOODIE-001",
    "price": 49.99,
    "compare_at_price": 69.99,
    "active": true,
    "image_url": "https://ik.imagekit.io/fluid/.../hoodie.jpg",
    "category_id": 123,
    "tags": ["apparel", "hoodie"],
    "variants": [
      {
        "title": "Black / S",
        "sku": "HOODIE-BLK-S",
        "price": 49.99,
        "compare_at_price": 69.99,
        "image_url": "https://ik.imagekit.io/fluid/.../hoodie-black.jpg",
        "option1": "Black",
        "option2": "S",
        "weight": 0.5,
        "weight_unit": "kg",
        "active": true
      }
    ],
    "options": [
      { "name": "Color", "values": ["Black", "Navy", "Gray"] },
      { "name": "Size", "values": ["S", "M", "L", "XL"] }
    ]
  }
}
```

**Key fields:**
- `source_type` + `source_id` — Used for deduplication. For manual creation, use `"manual"` + a unique ID.
- `image_url` — Must be a DAM URL (upload first via `https://upload.fluid.app/upload`)
- `variants` — At least one variant required. Each variant gets its own SKU and price.
- `options` — Define option axes (e.g., Color, Size). Variant `option1`/`option2`/`option3` map to these.
- `active` — Set `false` to create product in draft/inactive state.

### Update Product
```
PUT /api/company/v1/products/:id
```
Same payload structure. Only include fields you want to change.

### Activate/Deactivate Product
```
PUT /api/company/v1/products/:id
```
```json
{
  "product": {
    "active": false
  }
}
```

### List Products
```
GET /api/company/v1/products?page=1&per_page=50
```

Query parameters:
- `page` — Page number (default: 1)
- `per_page` — Items per page (default: 25, max: 50)
- `collection_id` — Filter by collection (supports multiple)
- `category_id` — Filter by category
- `category_title` — Filter by category title (case-sensitive)
- `status` — `active`, `draft`, `archived`
- `availability` — Filter by availability (default: `all`)
- `order_by` — Sort: `title`, `price`, `cv`, `created_at`
- `country_code` — Get country-specific pricing
- `lang` — Language code for translations
- `q` — Search by title/SKU

### Get Single Product
```
GET /api/company/v1/products/:id
```

### Get Collection Details
```
GET /api/company/v1/collections/:id_or_slug
```
Accepts either numeric ID or slug string.

### Delete Product
```
DELETE /api/company/v1/products/:id
```

---

## Categories

### Create Category
```
POST /api/company/v1/categories
```

```json
{
  "category": {
    "title": "Apparel",
    "description": "Clothing and accessories",
    "parent_id": 456,
    "image_url": "https://ik.imagekit.io/fluid/.../apparel.jpg",
    "active": true
  }
}
```

**Key fields:**
- `parent_id` — Omit for top-level categories. Set to another category's ID for nesting.
- Do NOT send `"parent_id": null` — omit the key entirely for top-level.

### List Categories
```
GET /api/company/v1/categories
```

---

## Collections

### Create Collection
```
POST /api/company/v1/collections
```

```json
{
  "collection": {
    "title": "Summer Sale",
    "description": "Hot deals for summer",
    "image_url": "https://ik.imagekit.io/fluid/.../summer.jpg",
    "active": true,
    "sort_order": "best_selling"
  }
}
```

**sort_order options:** `"manual"`, `"best_selling"`, `"title_asc"`, `"title_desc"`, `"price_asc"`, `"price_desc"`, `"created_at_desc"`, `"created_at_asc"`

### Add Product to Collection
```
POST /api/company/v1/products/:id/add_to_collection
```

```json
{
  "collection_id": 789
}
```

### Remove Product from Collection
```
DELETE /api/company/v1/products/:id/remove_from_collection
```

```json
{
  "collection_id": 789
}
```

### Update Collection
```
PUT /api/company/v1/collections/:id
```
Same payload as create. Only include fields you want to change.

### List Collections
```
GET /api/company/v1/collections
```

### Delete Collection
```
DELETE /api/company/v1/collections/:id
```

---

## Bulk Operations

### Create collection with specific products (multi-step)

```bash
# Step 1: Create the collection
COLLECTION=$(curl -s -X POST "${FLUID_URL}/api/company/v1/collections" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"collection": {"title": "New Arrivals", "active": true}}')

COLLECTION_ID=$(echo "$COLLECTION" | jq -r '.collection.id // .id')

# Step 2: Add products (can be parallelized)
for PRODUCT_ID in 101 102 103 104 105; do
  curl -s -X POST "${FLUID_URL}/api/company/v1/collections/${COLLECTION_ID}/add_product" \
    -H "Authorization: Bearer ${FLUID_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"product_id\": ${PRODUCT_ID}}" &
done
wait
```

### Bulk activate/deactivate products

```bash
# Get all products in a category
PRODUCTS=$(curl -s "${FLUID_URL}/api/company/v1/products?category_id=123&per_page=50" \
  -H "Authorization: Bearer ${FLUID_TOKEN}")

# Deactivate each one
echo "$PRODUCTS" | jq -r '.products[].id' | while read PID; do
  curl -s -X PUT "${FLUID_URL}/api/company/v1/products/${PID}" \
    -H "Authorization: Bearer ${FLUID_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"product": {"active": false}}' &
done
wait
```
