# Orders, Fulfillments, Refunds & Tracking API

## Orders

### List Orders (v2)
```
GET /api/v2/orders
```
Query params: `page`, `per_page`, `status`, `customer_id`, `created_at_min`, `created_at_max`

### List Orders (v202506 — newer)
```
GET /api/v202506/orders
```
Newer version with enhanced filtering.

### Get Order
```
GET /api/v2/orders/:id
```

### Get Order Stats
```
GET /api/v2/orders/stats
GET /api/v202506/orders/stats
```

### Find Orders by Email
```
GET /api/company/orders/find_by_email?email=jane@example.com
```

### Create Order
```
POST /api/orders
```

```json
{
  "order": {
    "customer_id": 123,
    "line_items": [
      {
        "variant_id": 456,
        "quantity": 2
      }
    ],
    "shipping_address": {
      "first_name": "Jane",
      "last_name": "Doe",
      "address1": "123 Main St",
      "city": "Austin",
      "province": "TX",
      "zip": "78701",
      "country": "US"
    }
  }
}
```

### Update Order
```
PATCH /api/orders/:id
PUT /api/orders/:id
```

### Cancel Order
```
PATCH /api/v2/orders/:id/cancel
```

### Archive / Unarchive Order
```
PATCH /api/v2/orders/:id/archive
PATCH /api/v2/orders/:id/unarchive
```

### Transfer Order to Different Customer
```
POST /api/orders/:id/transfer_customer
```

### Update Order Warehouse
```
PATCH /api/orders/:id/update_warehouse
```

### Update Order Sponsor
```
PATCH /api/v2/orders/:id/update_sponsor
```

### Update Order Shipping Address
```
PATCH /api/v2/orders/:id/update_shipping_address
```

### Update Order External ID
```
PATCH /api/v2/orders/:id/update_external_id
```

### Charge an Order
```
POST /api/v2/orders/:id/charge
```

### Append/Remove Metadata
```
PATCH /api/v2/orders/:id/append_metadata
PATCH /api/v2/orders/:id/remove_metadata
```

### Send Invoice Email
```
POST /api/v2/orders/send_invoice_email
```

### Export Orders to CSV
```
GET /api/v202506/orders/export_csv
```

---

## Order Fulfillments

### List Fulfillments
```
GET /api/order_fulfillments
```

### Create Fulfillment
```
POST /api/order_fulfillments
```

```json
{
  "order_id": 789,
  "order_items": [
    { "order_item_id": 101, "quantity": 1 }
  ],
  "tracking_informations": [
    {
      "tracking_number": "1Z999AA10123456784",
      "shipping_carrier": "ups"
    }
  ],
  "send_fulfillment_notification": true
}
```

### Get Fulfillment
```
GET /api/order_fulfillments/:id
```

### Update Fulfillment
```
PUT /api/order_fulfillments/:id
```

### Delete Fulfillment
```
DELETE /api/order_fulfillments/:id
```

---

## Refunds

### Create Refund (Full Restock)
```
POST /api/refunds
```

```json
{
  "order_id": 789,
  "type": "full",
  "amount": 49.99,
  "reason": "Customer request",
  "restock_all_items": true
}
```

### Create Refund for Specific Items
```
POST /api/refunds/items
```

```json
{
  "order_id": 789,
  "items": [
    { "order_item_id": 101, "quantity": 1 }
  ],
  "reason": "Defective item"
}
```

---

## Tracking Informations

### List Tracking Info
```
GET /api/tracking_informations
```

### Create Tracking Info
```
POST /api/tracking_informations
```

```json
{
  "tracking_information": {
    "order_fulfillment_id": 456,
    "tracking_number": "1Z999AA10123456784",
    "shipping_carrier": "ups",
    "tracking_url": "https://ups.com/track?num=1Z999AA10123456784"
  }
}
```

### Get Tracking Info
```
GET /api/tracking_informations/:id
```

### Update Tracking Info
```
PUT /api/tracking_informations/:id
```

### Delete Tracking Info
```
DELETE /api/tracking_informations/:id
```

---

## Customer Orders
```
GET /api/customer_orders
```
Lists orders for a specific customer. Use query params to filter.

---

## Common Workflows

### Fulfill and ship an order
```bash
# 1. Get order details
ORDER=$(curl -s "${FLUID_URL}/api/v2/orders/789" -H "Authorization: Bearer ${FLUID_TOKEN}")

# 2. Create fulfillment with tracking
curl -s -X POST "${FLUID_URL}/api/order_fulfillments" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 789,
    "order_items": [{"order_item_id": 101, "quantity": 1}],
    "tracking_informations": [{"tracking_number": "1Z999AA1", "shipping_carrier": "ups"}],
    "send_fulfillment_notification": true
  }'
```

### Process a refund
```bash
# Full refund with restock
curl -s -X POST "${FLUID_URL}/api/refunds" \
  -H "Authorization: Bearer ${FLUID_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 789, "type": "full", "reason": "Customer request", "restock_all_items": true}'
```
