# Customers & Inventory API

## Customers

### Create Customer
```
POST /api/customers
```

```json
{
  "customer": {
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@example.com",
    "phone": "+15551234567",
    "addresses": [
      {
        "address1": "123 Main St",
        "address2": "Apt 4B",
        "city": "Austin",
        "province": "TX",
        "zip": "78701",
        "country": "US",
        "default": true
      }
    ],
    "tags": ["vip", "wholesale"]
  }
}
```

**Key fields:**
- `email` — Required, must be unique
- `phone` — E.164 format recommended (e.g., `+15551234567`)
- `addresses` — Array of addresses. Set `"default": true` on one.
- `tags` — Array of strings for segmentation

### List Customers
```
GET /api/customers?page=1&per_page=50
```

Query parameters:
- `page`, `per_page` — Pagination
- `q` — Search by name or email
- `tag` — Filter by tag

### Get Customer
```
GET /api/customers/:id
```

### Update Customer
```
PATCH /api/customers/:id
```

Only include fields you want to change.

```json
{
  "customer": {
    "tags": ["vip", "wholesale", "loyalty-gold"]
  }
}
```

---

## Inventory

### List Inventory Levels
```
GET /api/inventory_levels
```

Query parameters:
- `variant_id` — Filter by variant
- `warehouse_id` — Filter by warehouse

### Get Single Inventory Level
```
GET /api/inventory_levels/:id
```

### Set Inventory (Absolute)
```
POST /api/inventory_levels/set
```

Sets the quantity to an exact number.

```json
{
  "variant_id": 456,
  "warehouse_id": 1,
  "quantity": 100
}
```

### Adjust Inventory (Relative)
```
POST /api/inventory_levels/adjust
```

Adds or subtracts from current quantity.

```json
{
  "variant_id": 456,
  "warehouse_id": 1,
  "quantity_adjustment": -5
}
```

Use negative numbers to decrease, positive to increase.

### Bulk Set Inventory
```
POST /api/inventory_levels/bulk_upsert
```

Set multiple inventory levels at once.

```json
{
  "inventory_levels": [
    { "variant_id": 456, "quantity": 100, "warehouse_id": 1 },
    { "variant_id": 457, "quantity": 50, "warehouse_id": 1 },
    { "variant_id": 458, "quantity": 200, "warehouse_id": 1 }
  ]
}
```

---

## Common Workflows

### Check and restock low inventory

```bash
# 1. Get all inventory levels for a warehouse
INVENTORY=$(curl -s "${FLUID_URL}/api/inventory_levels?warehouse_id=1" \
  -H "Authorization: Bearer ${FLUID_TOKEN}")

# 2. Find items below threshold (e.g., < 10 units)
LOW_STOCK=$(echo "$INVENTORY" | jq '[.inventory_levels[] | select(.quantity < 10)]')

# 3. Show the user what's low, then bulk update if approved
```

### Tag customers by order history

```bash
# 1. List customers
CUSTOMERS=$(curl -s "${FLUID_URL}/api/customers?per_page=50" \
  -H "Authorization: Bearer ${FLUID_TOKEN}")

# 2. Update tags for specific customers
curl -s -X PATCH "${FLUID_URL}/api/customers/789" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"customer": {"tags": ["vip", "repeat-buyer"]}}'
```
