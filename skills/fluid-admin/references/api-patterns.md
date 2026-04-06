# API Patterns, Gotchas & Error Handling

## The Two Country ID Problem

This is the #1 source of silent bugs in Fluid API integrations.

`GET /api/settings/company_countries` returns:
```json
[
  {
    "id": 55938,              // company_country_id
    "country": {
      "id": 214,              // country_id
      "name": "United States",
      "iso": "US"
    }
  }
]
```

**Which ID goes where:**

| Endpoint | Uses | Field name |
|----------|------|------------|
| Menus | `country.id` (214) | `country_ids` |
| Variants | `country.id` (214) | `country_id` |
| Regional rules | `country.iso` | `region_code` prefix |
| Agreements | top-level `id` (55938) | `company_country_ids` |
| Checkout | top-level `id` (55938) | `company_country_id` |
| Tax config | top-level `id` (55938) | `company_country_id` |
| Warehouse assign | `country.id` (214) | `country_id` |

**Rule of thumb:** Settings/admin endpoints use `company_country_id`. Customer-facing endpoints use `country_id`.

---

## Null & Empty Value Handling

Fluid's API rejects null values and empty arrays. This causes 422 errors.

**Wrong:**
```json
{
  "product": {
    "title": "Hoodie",
    "parent_id": null,
    "tags": [],
    "image_url": null
  }
}
```

**Right:**
```json
{
  "product": {
    "title": "Hoodie"
  }
}
```

**Rule:** If a field has no value, omit the key entirely. Never send `null`, `""`, or `[]`.

---

## Overwrite Safety (GET-Merge-PUT)

These endpoints **replace the entire object** on write:

- `PUT /api/settings/checkout`
- `PUT /api/companies/:id/onboarding_info`
- `PUT /api/menus/:id`

**Always:**
1. GET the current state
2. Merge your changes into the existing data
3. PUT/PATCH back the full merged object

**Never** PUT with only your changes — you'll erase everything else.

```bash
# Safe pattern
CURRENT=$(curl -s "${FLUID_URL}/api/settings/checkout" \
  -H "Authorization: Bearer ${FLUID_TOKEN}")

# Merge in jq
UPDATED=$(echo "$CURRENT" | jq '.checkout.collect_phone = true')

# Write back
curl -s -X PUT "${FLUID_URL}/api/settings/checkout" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$UPDATED"
```

---

## Rate Limiting

- **Limit:** ~10 requests/second (token bucket)
- **Response:** 429 Too Many Requests
- **Strategy:** Exponential backoff starting at 1 second, max 30 seconds
- **Concurrent workers:** 5-10 for bulk operations
- **No artificial delays:** Don't add `sleep()` between calls. Let the rate limiter tell you when to slow down.

```bash
# Retry pattern
attempt=0
max_attempts=3
while [ $attempt -lt $max_attempts ]; do
  response=$(curl -s -w "\n%{http_code}" -X POST "${FLUID_URL}/api/endpoint" \
    -H "Authorization: Bearer ${FLUID_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '...')

  status=$(echo "$response" | tail -1)

  if [ "$status" = "429" ] || [ "$status" -ge 500 ]; then
    sleep $((2 ** attempt))
    attempt=$((attempt + 1))
  else
    break
  fi
done
```

---

## Pagination

Most list endpoints support pagination:

```
GET /api/company/v1/products?page=1&per_page=50
```

- Default `per_page` is usually 25
- Max `per_page` is usually 50
- Check response for total count to know if more pages exist

```bash
# Fetch all pages
page=1
all_items="[]"
while true; do
  response=$(curl -s "${FLUID_URL}/api/company/v1/products?page=${page}&per_page=50" \
    -H "Authorization: Bearer ${FLUID_TOKEN}")

  items=$(echo "$response" | jq '.products')
  count=$(echo "$items" | jq 'length')

  all_items=$(echo "$all_items" "$items" | jq -s '.[0] + .[1]')

  if [ "$count" -lt 50 ]; then
    break
  fi
  page=$((page + 1))
done
```

---

## Error Response Format

Fluid returns structured error responses:

### 422 Validation Error
```json
{
  "errors": {
    "title": ["can't be blank"],
    "email": ["has already been taken"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Not authorized"
}
```

### 404 Not Found
```json
{
  "error": "Record not found"
}
```

Always show the error body to the user — it contains field-level details.

---

## Common HTTP Status Codes

| Status | Meaning | Action |
|--------|---------|--------|
| 200 | Success (read/update) | Proceed |
| 201 | Created | Resource created, check response for ID |
| 204 | No content | Delete succeeded |
| 400 | Bad request | Check payload format |
| 401 | Unauthorized | Token invalid/expired |
| 403 | Forbidden | Token lacks permission |
| 404 | Not found | Resource doesn't exist |
| 422 | Validation error | Check field errors in response |
| 429 | Rate limited | Back off and retry |
| 500+ | Server error | Retry with backoff (up to 3 times) |

---

## jq Cheat Sheet for Common Operations

```bash
# Extract ID from creation response
echo "$response" | jq -r '.product.id // .id'

# Get all product IDs
echo "$response" | jq -r '.products[].id'

# Filter active products
echo "$response" | jq '[.products[] | select(.active == true)]'

# Count results
echo "$response" | jq '.products | length'

# Get company_country_id for US
echo "$countries" | jq '[.[] | select(.country.iso == "US")][0].id'

# Get country_id for US
echo "$countries" | jq '[.[] | select(.country.iso == "US")][0].country.id'
```
