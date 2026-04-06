# Payments, Carts & Checkout API

---

## Payment Transactions

### Tokenize Credit Card
```
POST /api/v202506/payments/tokenize_card
```

### Create Payment
```
POST /api/v202506/payments/:payment_account_id
```
Creates a payment record using a payment account UUID and cart.

### List Transactions
```
GET /api/v202506/transactions
```
Query params for filtering, sorting, and pagination.

### Get Transaction Filter Options
```
GET /api/v202506/transactions/filter_options
```

### Get Payment Transaction
```
GET /api/payments/:payment_uuid
```

### Update Payment Transaction
```
PATCH /api/payments/:payment_uuid
```

### Settle Authorized Payment
```
POST /api/v202506/payments/settle
```

### Cancel Authorized Payment
```
PATCH /api/v202506/payments/cancel/:order_token
```

### Klarna Payment Sessions
```
POST /api/v202506/carts/:cart_token/klarna/create_session
POST /api/v202506/carts/:cart_token/klarna/update_session
```

---

## Payment Accounts

Payment gateway configurations (Stripe, etc.).

### List Payment Accounts
```
GET /api/payment_accounts
```

### Create Payment Account
```
POST /api/payment_accounts
```

```json
{
  "payment_account": {
    "name": "Primary Stripe",
    "payment_integration_id": 1,
    "credentials": {
      "secret_key": "sk_live_...",
      "publishable_key": "pk_live_..."
    },
    "active": true
  }
}
```

### Get Payment Account
```
GET /api/payment_accounts/:id
```

### Update Payment Account
```
PUT /api/payment_accounts/:id
```

### Delete Payment Account
```
DELETE /api/payment_accounts/:id
```

### Get Credentials Schema
```
GET /api/payment_accounts/credentials_schema
```
Returns the required credential fields for each payment integration.

---

## Fluid Pay

Fluid's built-in payment system for saved payment methods and addresses.

### Get Payment Methods
```
GET /api/fluid_pay/payment_methods
```

### Create Payment Method
```
POST /api/fluid_pay/create_payment_method
```

### Update Payment Method
```
PATCH /api/fluid_pay/update_payment_method/:payment_method_id
```

### Delete Payment Method
```
DELETE /api/fluid_pay/delete_payment_method/:payment_method_id
```

### Get Addresses
```
GET /api/fluid_pay/addresses
```

### Create / Update / Delete Address
```
POST   /api/fluid_pay/create_address
PATCH  /api/fluid_pay/update_address/:address_id
DELETE /api/fluid_pay/delete_address/:address_id
```

### Get Account Info
```
GET /api/fluid_pay/me
```

### Update Current Customer
```
PATCH /api/fluid_pay/update_me
```

### Vault Access Token
```
GET /api/fluid_pay/vault
```

---

## Carts (44 endpoints)

Full cart lifecycle — creation, item management, checkout, attribution.

### Core Cart Operations

```
POST   /api/carts                              # Create cart
GET    /api/carts/:cart_token                   # Get cart
PATCH  /api/carts/:cart_token                   # Update cart
```

### Cart Items

```
POST   /api/carts/:cart_token/items             # Add items (or update qty)
DELETE /api/carts/:cart_token/items             # Remove items (bulk)
DELETE /api/carts/:cart_token/items/:item_id    # Remove single item
```

### Cart Item Modifications

```
PATCH  /api/carts/:cart_token/items/:item_id/variant        # Change item variant
PATCH  /api/carts/:cart_token/items/:item_id/bundled_items  # Update bundled items
PATCH  /api/carts/:cart_token/items/:item_id/update_volumes # Update volume totals
POST   /api/carts/:cart_token/items/:item_id/subscribe      # Add subscription to item
DELETE /api/carts/:cart_token/items/:item_id/subscribe      # Remove subscription from item
```

### Discounts

```
POST   /api/carts/:cart_token/discount                      # Apply discount code
DELETE /api/carts/:cart_token/discount                      # Remove all discounts
DELETE /api/carts/:cart_token/discount/:discount_code       # Remove specific discount
```

### Address & Shipping

```
POST /api/carts/:cart_token/address                         # Update cart address
POST /api/carts/:cart_token/shipping_method                 # Set shipping method
```

### Payment

```
POST /api/carts/:cart_token/payment_methods/:type           # Set payment method
POST /api/carts/:cart_token/set_saved_payment_method        # Use saved payment method
GET  /api/carts/:cart_token/payment_account/:id/vault       # VGS vault token
POST /api/carts/:cart_token/vault                           # VGS vault token (alt)
```

### Points

```
POST   /api/carts/:cart_token/apply_points                  # Apply points redemption
DELETE /api/carts/:cart_token/remove_points                 # Remove points
```

### Checkout

```
POST /api/carts/:cart_token/checkout                        # Complete checkout
GET  /api/carts/:cart_token/cart_info                       # Cart company info
POST /api/carts/:cart_token/recalculate                     # Recalculate totals
PATCH /api/carts/:cart_token/update_totals                  # Manual total update
```

### Cart Metadata & Messages

```
PATCH  /api/carts/:cart_token/append_metadata               # Append metadata
PATCH  /api/carts/:cart_token/remove_metadata               # Remove metadata
PATCH  /api/carts/:cart_token/metadata                      # Update metadata
POST   /api/carts/:cart_token/messages                      # Update messages
DELETE /api/carts/:cart_token/messages                      # Clear messages
PATCH  /api/carts/:cart_token/redirect_urls                 # Update redirect URLs
```

### Cart Attribution & Reps

```
PATCH /api/carts/:cart_token/attribution                    # Update attribution
PATCH /api/carts/:cart_token/buyer_rep                      # Set buyer rep
PATCH /api/carts/:cart_token/volume_rep                     # Set volume rep
DELETE /api/carts/:cart_token/logout                        # Remove rep/customer
POST  /api/carts/:cart_token/sync_customer                  # Sync with auth customer
```

### Cart Enrollment & Language

```
POST  /api/carts/:cart_token/enrollment                     # Add enrollment to cart
GET   /api/carts/:cart_token/enroll                         # Get enrollment info
PATCH /api/carts/:cart_token/change_language                # Change cart language
PATCH /api/carts/:cart_token/update_country                 # Change cart country
```

### Cart Magic Link (Passwordless Auth)

```
POST /api/carts/:cart_token/magic_link                      # Create magic link
POST /api/carts/:cart_token/confirm_magic_link              # Confirm magic link
```

**Note:** Carts use a `cart_token` string identifier, not a numeric ID.
