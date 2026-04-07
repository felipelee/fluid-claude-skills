# Multi-Step Workflows

These are the most powerful use cases for the fluid-admin skill — the agent chains multiple API calls so you just describe what you want in natural language.

---

## Catalog & Collections

**"Create a 'Best Sellers' collection and add my top products"**
1. GET `/api/company/v1/products?order_by=best_selling` to find top products
2. POST `/api/company/v1/collections` to create the collection
3. POST `/api/company/v1/products/:id/add_to_collection` for each product

**"Raise all prices in collection X by 10%"**
1. GET `/api/company/v1/products?collection_id=X` to get all products in collection
2. GET `/api/company/products/:id/variants` for each product to get current prices
3. Calculate new prices (price × 1.10)
4. PUT `/api/company/v1/variants/bulk_update` with new prices

**"Set up a sale — mark everything in Summer collection as 20% off"**
1. GET `/api/company/v1/products?collection_id=X` to get products
2. GET variants for each to get current prices
3. Set `compare_at_price` = current price, `price` = current price × 0.80
4. PUT `/api/company/v1/variants/bulk_update`
5. Optionally: POST `/api/v2025-06/discounts` to create a promo code too

**"Deactivate all products in category X"**
1. GET `/api/company/v1/products?category_id=X` to list products (paginate if needed)
2. PUT `/api/company/v1/products/:id` with `"active": false` for each

**"Reorganize my catalog — create categories and auto-assign products"**
1. POST `/api/company/v1/categories` to create parent categories
2. POST `/api/company/v1/categories` with `parent_id` for subcategories
3. GET `/api/company/v1/products` to list all products
4. PUT `/api/company/v1/products/:id` with new `category_id` based on title/tags/type

**"Create product bundles — a Starter Kit from these 3 products"**
1. POST `/api/company/v1/products` to create the bundle parent product
2. POST `/api/company/v1/products/:id/product_bundles` for each bundled variant

---

## Navigation

**"Build out my main navigation with dropdowns"**
1. GET `/api/settings/company_countries` to get `country_id` for menus
2. GET `/api/company/v1/collections` to get collection slugs for links
3. POST `/api/menus` with nested `menu_items_attributes` and `sub_menu_items_attributes`

**"Add a new item to the existing nav"**
1. GET `/api/menus` to find the current main menu
2. GET `/api/menus/:id` to get full menu with existing items
3. PUT `/api/menus/:id` with existing items + new item appended

**"Create a footer menu with policy links"**
1. GET `/api/company/v1/pages` to get page slugs
2. GET `/api/agreements` to get policy pages
3. POST `/api/menus` with footer-specific items (About, Contact, Terms, Privacy, etc.)

---

## Orders & Fulfillment

**"Fulfill and ship an order"**
1. GET `/api/v2/orders/:id` to get order details and line items
2. POST `/api/order_fulfillments` with order items + tracking info
3. Notification sent automatically if `send_fulfillment_notification: true`

**"Process a full refund and restock"**
1. GET `/api/v2/orders/:id` to verify order details
2. POST `/api/refunds` with `restock_all_items: true`

**"Find and cancel all orders from a specific customer"**
1. GET `/api/company/orders/find_by_email?email=X` to find orders
2. PATCH `/api/v2/orders/:id/cancel` for each pending order

---

## Subscriptions

**"Set up a subscription plan and link it to products"**
1. POST `/api/subscription_plans` to create the plan (interval, discount)
2. POST `/api/company/v1/products/:id/subscription_plans` for each product
3. Customers can now subscribe at checkout

**"Pause all subscriptions for a specific customer"**
1. GET `/api/subscriptions?customer_id=X` to find active subs
2. POST `/api/subscriptions/:token/pause` for each

---

## MLM / Network

**"Onboard a new rep with a starter pack"**
1. POST `/api/v2/reps` to create the rep account
2. POST `/api/enrollment_packs` to create their starter pack (if needed)
3. POST `/api/trees/:tree_id/tree_nodes` to place them in the downline
4. POST `/api/v202506/customers/:id/points_ledgers` to award welcome bonus points

**"Set up the rank structure"**
1. POST `/api/v202506/ranks` for each rank level (Bronze, Silver, Gold, etc.)

---

## Store Setup

**"Open a new country/market"**
1. POST `/api/settings/company_countries` to add the country
2. POST `/api/settings/warehouses` to create a warehouse (if needed)
3. POST `/api/settings/warehouses/:id/assign_to_country`
4. POST `/api/companies/set_shipping` to configure rates
5. Update menus with new `country_ids`

**"Set up free shipping with tiered rates"**
1. POST `/api/companies/set_shipping` with manual rates:
   - Standard: $5.99 for orders under $75
   - Free: $0 for orders $75+

**"Complete brand setup"**
1. Upload logo/favicon/OG image via `POST https://upload.fluid.app/upload`
2. PATCH `/api/settings/brand_guidelines` with colors, fonts, image URLs
3. PATCH `/api/settings/social_media` with social links
4. GET then PUT `/api/settings/checkout` to set checkout colors to match brand

---

## Discounts & Promotions

**"Create a flash sale with promo code"**
1. POST `/api/company/v1/collections` to create a sale collection
2. POST `/api/company/v1/products/:id/add_to_collection` for sale products
3. POST `/api/v2025-06/discounts` with code, percentage, date range
4. POST `/api/company/announcements` to notify reps about the sale
5. GET + PUT `/api/menus/:id` to add Sale link to nav

**"Set up a BOGO or free product discount"**
1. POST `/api/v2025-06/discounts` with `price_discount_type: "free_product"` and `free_variant_ids`

---

## Content & Engagement

**"Set up store pages (About, FAQ, Contact)"**
1. POST `/api/company/v1/pages` for each page with HTML content and SEO meta
2. GET + PUT `/api/menus/:id` to add page links to navigation

**"Create and publish an announcement to all reps"**
1. Upload image via DAM if needed
2. POST `/api/company/announcements` with title, description, image, `active: true`

**"Build a media library for rep training"**
1. POST `/api/company/libraries` to create the library
2. POST `/api/company/media` for each video/PDF/resource
3. PUT `/api/company/libraries/:id/add_item_to_library` for each media item

---

## Webhooks & Integrations

**"Set up order notifications to my external system"**
1. POST `/api/webhooks` with URL and events (`order_completed`, `order_shipped`, etc.)
2. GET `/api/webhooks/payload_example?event=order_completed` to preview what you'll receive

**"Add a tracking pixel (Facebook, GA4, etc.)"**
1. POST `/api/global_embeds` with the script code and `placement: "head"`

---

## Cleanup & Maintenance

**"End-of-season cleanup"**
1. GET `/api/company/v1/products?collection_id=X` to find seasonal products
2. PUT `/api/company/v1/products/:id` with `"active": false` for each
3. DELETE `/api/company/v1/products/:id/remove_from_collection` to clean up collection
4. GET + PUT `/api/menus/:id` to remove seasonal nav items
5. POST `/api/redirects` from old collection URL to new destination

**"Audit and clean up unused collections"**
1. GET `/api/company/v1/collections` to list all collections
2. GET `/api/company/v1/products?collection_id=X` for each to check if empty
3. DELETE empty collections (with user confirmation)
