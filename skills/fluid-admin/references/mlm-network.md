# MLM & Network: Enrollments, Reps, Users, Ranks, Trees, Points & Subscriptions

These endpoints power Fluid's social selling and MLM features — rep management, downline trees, enrollment flows, rank qualification, points/rewards, and recurring subscriptions.

---

## Reps (Affiliates / Distributors)

### List Reps
```
GET /api/v2/reps
```
Query params: `page`, `per_page`, `q` (search)

### Create Rep
```
POST /api/v2/reps
```

```json
{
  "rep": {
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "phone": "+15551234567",
    "enroller_id": 100,
    "rank_id": 1
  }
}
```

### Get Rep
```
GET /api/v2/reps/:id
```

### Update Rep
```
PATCH /api/v2/reps/:id
```

### Delete Rep
```
DELETE /api/v2/reps/:id
```

### Update Rep's Enroller
```
PATCH /api/v2/reps/:id/update_enroller
```

---

## Users

Users represent all user accounts (admins, reps, customers, etc.).

### Create User
```
POST /api/v202506/users
```

```json
{
  "country_code": "US",
  "language_code": "en",
  "user": {
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "phone": "+15551234567"
  }
}
```

### Create and Invite User
```
POST /api/users/create_and_invite
```
Creates user and sends invitation email.

### List Users
```
GET /api/v202506/users
```
Query params: `page`, `per_page`, filters

### Get User
```
GET /api/v202506/users/:id
```

### Find User
```
GET /api/v202506/users/find?email=jane@example.com
```

### Update User
```
PATCH /api/v202506/users/:id
```

### Delete User
```
DELETE /api/v202506/users/:id
```

### Append/Remove User Metadata
```
PATCH /api/v202506/users/:id/append_metadata
```

### Legacy User Endpoints
```
GET    /api/company/users          # List
POST   /api/company/users          # Create
GET    /api/company/users/:id      # Get
PUT    /api/company/users/:id      # Update
DELETE /api/company/users/:id      # Delete
```

---

## Ranks

Ranks define achievement levels in the MLM compensation structure.

### List Ranks
```
GET /api/v202506/ranks
```

### Create Rank
```
POST /api/v202506/ranks
```

```json
{
  "name": "Gold Director",
  "external_id": "rank-gold-director"
}
```

### Update Rank
```
PATCH /api/v202506/ranks/:id
```

---

## Trees (Downline Structure)

Trees represent the organizational hierarchy of the network.

### List Trees
```
GET /api/trees
```

### Create Tree
```
POST /api/trees
```

```json
{
  "tree": {
    "name": "Enrollment Tree",
    "tree_type": "enrollment"
  }
}
```

### Get Tree
```
GET /api/trees/:id
```

### Update Tree
```
PUT /api/trees/:id
```

### Delete Tree
```
DELETE /api/trees/:id
```

---

## Tree Nodes

Individual nodes within a tree (each node = a rep/user).

### List Tree Nodes
```
GET /api/trees/:tree_id/tree_nodes
```

### Create Tree Node
```
POST /api/trees/:tree_id/tree_nodes
```

```json
{
  "tree_node": {
    "user_id": 123,
    "parent_node_id": 456
  }
}
```

### Get Tree Node
```
GET /api/trees/:tree_id/tree_nodes/:id
```

### Update Tree Node
```
PUT /api/trees/:tree_id/tree_nodes/:id
```

### Delete Tree Node
```
DELETE /api/trees/:tree_id/tree_nodes/:id
```

---

## Enrollment Packs

Pre-configured product bundles for new rep enrollment.

### List Enrollment Packs
```
GET /api/enrollment_packs
```

### Create Enrollment Pack
```
POST /api/enrollment_packs
```

```json
{
  "enrollment_pack": {
    "title": "Starter Pack",
    "description": "Everything you need to get started",
    "price": 99.99,
    "active": true,
    "product_ids": [101, 102, 103]
  },
  "language_iso": "en"
}
```

### Get Enrollment Pack
```
GET /api/enrollment_packs/:id
```

### Update Enrollment Pack
```
PATCH /api/enrollment_packs/:id
```

### Delete Enrollment Pack
```
DELETE /api/enrollment_packs/:id
```

### Bulk Update Status
```
PATCH /api/enrollment_packs/bulk_status_update
```

---

## Enrollments

Enrollment forms and field responses for new rep sign-up flows.

### Get Enrollment
```
GET /api/enrollments/:enrollment_token
```
Returns enrollment with fields and current answers.

### Submit Field Answer
```
POST /api/enrollments/:enrollment_token/field/:field_id
```

### Update Field Answer
```
PATCH /api/enrollments/:enrollment_token/answer/:field_answer_id
```

### Submit File Answer
```
POST /api/enrollments/:enrollment_token/file/:field_id
```
Multipart upload for file-type enrollment fields.

---

## Points Ledgers (Loyalty / Rewards)

### List Points Ledger Entries
```
GET /api/v202506/customers/:customer_id/points_ledgers
```

### Create Points Ledger Entry
```
POST /api/v202506/customers/:customer_id/points_ledgers
```

```json
{
  "points": 500,
  "description": "Bonus points for referral",
  "type": "credit"
}
```

---

## Points Values

Configure the monetary value of points per currency.

### List Points Values
```
GET /api/v202506/points_values
```

### Update Points Value
```
PATCH /api/v202506/points_values
```

```json
{
  "currency_iso": "USD",
  "value": 0.01
}
```

### Refresh Points Values
```
POST /api/v202506/points_values/refresh
```

---

## Subscription Plans

Recurring billing plan definitions.

### List Subscription Plans
```
GET /api/subscription_plans
```

### Create Subscription Plan
```
POST /api/subscription_plans
```

```json
{
  "subscription_plan": {
    "name": "Monthly Essentials",
    "interval": "month",
    "interval_count": 1,
    "discount_percentage": 15
  }
}
```

### Get Subscription Plan
```
GET /api/subscription_plans/:id
```

### Update Subscription Plan
```
PUT /api/subscription_plans/:id
```

### Delete Subscription Plan
```
DELETE /api/subscription_plans/:id
```

### Remove Product from Plan
```
POST /api/subscription_plans/:id/remove_product
```

---

## Subscriptions (Active Recurring Orders)

### List Subscriptions
```
GET /api/subscriptions
```

### Create Subscription
```
POST /api/subscriptions
```

```json
{
  "subscription": {
    "customer_id": 123,
    "subscription_plan_id": 456,
    "variant_ids": [789, 790],
    "shipping_address": {
      "address1": "123 Main St",
      "city": "Austin",
      "province": "TX",
      "zip": "78701",
      "country": "US"
    }
  }
}
```

### Get Subscription
```
GET /api/subscriptions/:token
```

### Update Subscription
```
PUT /api/subscriptions/:token
```

### Pause / Resume / Cancel / Reactivate
```
POST /api/subscriptions/:token/pause
POST /api/subscriptions/:token/resume
POST /api/subscriptions/:token/cancel
POST /api/subscriptions/:token/reactivate
```

### Skip Next Billing
```
POST /api/subscriptions/:token/skip_next_billing
```

### Get Subscription Orders
```
GET /api/subscriptions/:token/orders
```

### Send Invoice Email
```
POST /api/subscriptions/send_invoice_email
```

### Bulk Cancel Subscriptions
```
POST /api/subscriptions/bulk_cancel
```

**Note:** Subscriptions use a `token` identifier, not a numeric `id`.
