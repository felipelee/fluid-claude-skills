---
name: fluid-onboarding-prefill
description: >-
  Pre-fill the Fluid Commerce payments onboarding (KYC) form by scraping a
  company's existing website. Use when helping a company get set up for
  payments processing on Fluid, pre-filling onboarding forms, gathering
  business info from a website, or working with the onboarding API. Triggers
  on onboarding, KYC, payments setup, merchanting, business info, pre-fill
  form, company details, underwriting.
metadata:
  version: 1.0.0
---

# Fluid Onboarding Pre-Fill

Scrapes a company's existing website to pre-fill as much of the Fluid payments onboarding (KYC) form as possible. The onboarding form is a 10-step wizard with 80+ fields — this skill automates gathering the publicly available data.

## Every run is a fresh run

This skill is used across many different companies and Fluid accounts. **Never reuse data from a previous run.** Always ask for credentials and start clean.

## Step 1: Collect credentials

Ask the user for ALL FOUR before doing anything:

1. **Company website URL** — The site to scrape (e.g. `https://yellowbirdfoods.com`)
2. **Fluid URL** — Their Fluid store (e.g. `https://companyname.fluid.app`)
3. **Fluid API token** — Developer token from Fluid admin
4. **Firecrawl API key** — From [firecrawl.dev](https://firecrawl.dev)

## Step 2: Validate credentials

Run these in parallel before scraping. If any fail, stop immediately.

```python
# 1. Source site reachable
requests.get(company_url, timeout=10)  # expect 200

# 2. Fluid API token works + get company ID
resp = requests.get(f"{fluid_url}/api/settings/company_countries",
                    headers={"Authorization": f"Bearer {token}"}, timeout=10)
# expect 200, extract company info

# 3. Firecrawl key works
requests.post("https://api.firecrawl.dev/v1/scrape",
              headers={"Authorization": f"Bearer {fc_key}"},
              json={"url": "https://example.com", "formats": ["markdown"], "limit": 1},
              timeout=15)
# expect 200
```

Print results:
```
[Preflight] Source site: OK yellowbirdfoods.com
[Preflight] Fluid API:  OK companyname.fluid.app (Company ID: 980243068)
[Preflight] Firecrawl:  OK
```

**CRITICAL: Confirm company identity before proceeding.** Display the company name returned by the Fluid API and ask the user to confirm this is the correct store. This prevents accidentally writing onboarding data to the wrong Fluid account.

```
⚠️  This token resolves to: "Yellowbird Foods" (Company ID: 980243068)
    Store URL: https://companyname.fluid.app

Is this the correct store? (yes/no)
```

**Do NOT proceed until the user confirms.**

## Step 3: Scrape the website

Use Firecrawl to extract structured data in parallel:

### 3a. Brand extraction (logo, colors, fonts)

```python
result = firecrawl.scrape_url(company_url, params={"formats": ["branding"]})
branding = result.get("branding", {})
# Returns: logo, favicon, colors (primary, secondary, accent, background, text), typography
```

### 3b. Structured data extraction via Firecrawl Extract

Use the `/extract` endpoint to pull business information across the site:

```python
result = firecrawl.extract([
    company_url,
    f"{company_url}/about*",
    f"{company_url}/contact*",
    f"{company_url}/pages/about*",
], prompt="""Extract all business information:
- Company legal name and trading/brand name
- Physical address (street, city, state, zip, country)
- Phone number(s)
- Email address(es)
- Year founded / date of incorporation
- Business description (what they sell, industry)
- Key people (names, titles, roles)
- Social media links
- Whether they sell health supplements, CBD, kratom, or make health claims
- Countries they ship to or operate in
""")
```

### 3c. Scrape specific pages

Scrape these pages for targeted data (in parallel):

| Page | URL patterns | Data to extract |
|------|-------------|-----------------|
| **Homepage** | `/` | Company name, tagline, description, hero content |
| **About** | `/about`, `/pages/about`, `/about-us` | Company story, leadership team, founding date |
| **Contact** | `/contact`, `/pages/contact`, `/contact-us` | Address, phone, email, hours |
| **Terms of Service** | `/policies/terms-of-service`, `/terms` | Full policy text (for underwriting) |
| **Privacy Policy** | `/policies/privacy-policy`, `/privacy` | Full policy text (for underwriting) |
| **Refund Policy** | `/policies/refund-policy`, `/refund` | Full policy text (for underwriting) |
| **Shipping Policy** | `/policies/shipping-policy`, `/shipping` | Shipping countries, zones |
| **Team/Leadership** | `/team`, `/about/team`, `/leadership` | Owner names, titles, photos |
| **Footer** | (from homepage HTML) | Address, phone, social links, legal name |

For Shopify sites, also fetch:
```
GET {company_url}/meta.json        # Store name, description
GET {company_url}/policies.json    # (if Shopify admin token available)
```

### 3d. JSON-LD structured data

Parse `<script type="application/ld+json">` from the homepage for:
- `Organization` — name, legal name, address, phone, email, logo, social links
- `LocalBusiness` — address, hours, phone, geo coordinates
- `WebSite` — site name, description

## Step 4: Map scraped data to onboarding fields

### What CAN be pre-filled from scraping

| Wizard step | Fields | Source |
|-------------|--------|--------|
| **1. The Basics** | `company_description`, MCC code guess | Homepage, about page, product types |
| **2. Business Info** | `legal_name`, `trading_name`, `address1`, `city`, `province`, `postal_code`, `country_iso`, `phone`, `website` | Contact page, footer, JSON-LD |
| **3. Legal Entities** | Entity name, address, phone, website | Same as business info |
| **6. Personal Info** | Owner `full_name`, `work_email`, `position` | About/team page, JSON-LD |
| **8. Countries** | Operating countries, currencies | Shipping page, currency selector, shipping zones |
| **9. Underwriting** | `company_description`, policy links/content, product type flags, `company_is_mlm` | Homepage, policy pages, product pages |

### What CANNOT be pre-filled (user must provide)

| Wizard step | Fields | Why |
|-------------|--------|-----|
| **1. The Basics** | Business type classification, ownership flags | Legal determination |
| **3. Legal Entities** | Registration number, tax ID, VAT ID, date of incorporation | Not public |
| **4-5. Bank Accounts** | All bank details (account number, routing, SWIFT) | Sensitive financial data |
| **6. Personal Info** | Date of birth, nationality, ID numbers, ownership percentage | PII / not public |
| **7. Relevant Persons** | Additional person details | PII / not public |
| **9. Underwriting** | Financial projections, processing statements, revenue breakdowns | Internal business data |
| **10. Terms** | Agreement signature | Requires human consent |

## Step 5: Push to Fluid onboarding API

### 5a. Get existing onboarding state

```python
# Get current state to avoid overwriting user-entered data
resp = GET /api/companies/{company_id}/onboarding_info
existing = resp["company"]["onboarding_info"]

resp = GET /api/companies/{company_id}/entities
existing_entities = resp["entities"]

resp = GET /api/companies/{company_id}/owners
existing_owners = resp["owners"]
```

**IMPORTANT:** Only fill in fields that are currently empty/null. Never overwrite data the user has already entered.

### 5b. Create or update legal entity

```json
POST /api/companies/{company_id}/entities
{
  "entity": {
    "legal_name": "Yellowbird Foods LLC",
    "trading_name": "Yellowbird",
    "primary": true,
    "address1": "1234 E 6th St",
    "city": "Austin",
    "province": "TX",
    "postal_code": "78702",
    "country_iso": "US",
    "phone": "+15125551234",
    "website": "https://yellowbirdfoods.com",
    "classification": "llc"
  }
}
```

### 5c. Create owner (if found on team/about page)

```json
POST /api/companies/{company_id}/owners
{
  "owner": {
    "entity_id": 123,
    "full_name": "George Milton",
    "work_email": "george@yellowbirdfoods.com",
    "position": "CEO",
    "is_managing_director": true,
    "is_beneficial_owner": true,
    "onboarding_contact": true
  }
}
```

Only create if: the person's name AND role were clearly identified on the site. Don't guess.

### 5d. Update onboarding info

```json
PUT /api/companies/{company_id}/onboarding_info
{
  "onboarding_info": {
    "underwriting_info": {
      "company_description": "Yellowbird Foods makes organic hot sauces...",
      "company_is_mlm": false,
      "terms_and_conditions": {
        "link": "https://yellowbirdfoods.com/policies/terms-of-service"
      },
      "refund_policy": {
        "link": "https://yellowbirdfoods.com/policies/refund-policy"
      },
      "privacy_policy": {
        "link": "https://yellowbirdfoods.com/policies/privacy-policy"
      }
    },
    "countries_info": [
      {
        "country_iso": "US",
        "country_id": 214,
        "currency": "USD",
        "entity_id": 123,
        "entity_legally_registered": true,
        "settlement_currency": "USD"
      }
    ]
  }
}
```

**CRITICAL:** `PUT` overwrites the entire `onboarding_info`. Always `GET` first, merge your data into the existing blob, then `PUT` back. Otherwise you'll wipe out any data the user already entered.

### 5e. Underwriting health product flags

If the site sells supplements, health products, or makes health claims, set the relevant flags:

```json
{
  "underwriting_info": {
    "sells_supplements": true,
    "contains_kratom": false,
    "contains_cbd": false,
    "makes_disease_claims": false,
    "supplement_ingredients": "Habanero, Serrano, various organic peppers..."
  }
}
```

Detect from product pages: look for supplement facts panels, FDA disclaimers, ingredient lists, health-related product categories.

## Step 6: Report what was filled and what's missing

After pushing data, print a clear summary:

```
=== Onboarding Pre-Fill Complete ===

FILLED:
  Business Info:     Yellowbird Foods LLC, Austin TX
  Website:           https://yellowbirdfoods.com
  Phone:             +15125551234
  Primary Contact:   George Milton (CEO)
  Company Description: Organic hot sauce maker...
  Policies:          Terms, Privacy, Refund (links saved)
  Operating Country: US (USD)

NEEDS USER INPUT:
  Business type classification
  Tax ID / EIN
  Registration number & date of incorporation
  Bank account details (account, routing, SWIFT)
  Owner personal details (DOB, nationality, ID, ownership %)
  Financial projections & processing statements
  Revenue breakdown percentages
  Terms & Conditions signature

The user can now go to Settings > Onboarding in Fluid admin to review
and complete the remaining fields.
```

## MCC Code Guessing

If the product type is identifiable, suggest an MCC code. Common ones:

| Business type | MCC | Code |
|---------------|-----|------|
| Health food / supplements | 5499 | Miscellaneous Food Stores |
| Clothing / apparel | 5651 | Family Clothing Stores |
| Cosmetics / beauty | 5977 | Cosmetic Stores |
| General ecommerce | 5999 | Miscellaneous Retail |
| Hot sauce / condiments | 5499 | Miscellaneous Food Stores |

Fetch the full list from `GET /api/mcc_codes` to find the best match. Fetch business types from `GET /api/business_types?country_code=US`.

## API Reference

### Onboarding Info
| Method | Endpoint |
|--------|----------|
| GET | `/api/companies/{id}/onboarding_info` |
| PUT | `/api/companies/{id}/onboarding_info` |

### Legal Entities
| Method | Endpoint |
|--------|----------|
| GET | `/api/companies/{id}/entities` |
| POST | `/api/companies/{id}/entities` |
| PUT | `/api/companies/{id}/entities/{eid}` |
| DELETE | `/api/companies/{id}/entities/{eid}` |

### Bank Accounts
| Method | Endpoint |
|--------|----------|
| GET | `/api/companies/{id}/bank_accounts` |
| POST | `/api/companies/{id}/bank_accounts` |
| PUT | `/api/companies/{id}/bank_accounts/{bid}` |
| DELETE | `/api/companies/{id}/bank_accounts/{bid}` |

### Owners
| Method | Endpoint |
|--------|----------|
| GET | `/api/companies/{id}/owners` |
| POST | `/api/companies/{id}/owners` |
| PUT | `/api/companies/{id}/owners/{oid}` |
| DELETE | `/api/companies/{id}/owners/{oid}` |

### Document Upload
| Method | Endpoint |
|--------|----------|
| POST | `/api/companies/{id}/onboarding_info/upload_document` (multipart, 10MB max) |

### Lookups
| Method | Endpoint |
|--------|----------|
| GET | `/api/mcc_codes` |
| GET | `/api/business_types?country_code={iso}` |

### Payments Status
| Method | Endpoint |
|--------|----------|
| GET | `/api/companies/{id}/payments_status` |
