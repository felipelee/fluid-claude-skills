---
name: fluid-onboarding-prefill
description: >-
  Pre-fill the Fluid Commerce payments onboarding (KYC) form by scraping a
  company's website AND researching public records (state registries, Google
  Business Profile, LinkedIn, BBB, Trustpilot, negative media). Cross-verifies
  data across sources with confidence scoring before pushing. Use when helping
  a company get set up for payments processing on Fluid.
metadata:
  version: 2.2.0
---

# Fluid Onboarding Pre-Fill

Scrapes a company's website AND researches public records to pre-fill the Fluid payments onboarding (KYC) form. The form is a 10-step wizard with 80+ fields. This skill automates gathering publicly available data, cross-verifies it across multiple sources, scores confidence, and only pushes verified data.

## Critical Rules

> **NEVER reuse data from a previous run.** This skill is used across many different companies. Always ask for credentials and start clean.

> **NEVER push LOW-confidence data.** Only HIGH and MEDIUM get pushed. LOW is report-only.

> **NEVER overwrite existing data.** Always GET before PUT. Only fill fields that are currently empty/null.

> **PUT /onboarding_info overwrites the entire blob.** Always GET first, deep-merge, then PUT back. Failing to merge will destroy data the user already entered.

> **NEVER fill PII fields** (DOB, nationality, government ID, ownership %). These cannot be reliably sourced from public records.

## Flow Overview

```
1. Collect credentials          — ask user for all 4
2. Validate credentials         — preflight checks in parallel
3. Scrape company website       — Firecrawl extract + page scrapes + Shopify + JSON-LD
4. Research public records      — state registry, Google, LinkedIn, BBB, Trustpilot, negative media
5. Cross-verify & score         — confidence matrix (HIGH / MEDIUM / LOW / CONFLICT)
6. Promote MEDIUM fields        — targeted follow-up searches (max 2 per field)
7. MLM assessment               — scored signals, user confirms before setting flag
8. Map & push                   — GET existing state, merge, push HIGH + MEDIUM only
9. Report                       — confidence matrix + gaps + negative media scan
```

## Reference Files

Read these when you need detailed lookups during execution:
- [references/state-registries.md](references/state-registries.md) — US state business registry domains for `site:` searches
- [references/field-coverage.md](references/field-coverage.md) — complete field map with sources, API locations, and confidence models
- [references/api-endpoints.md](references/api-endpoints.md) — all onboarding API endpoints

---

## Step 1: Collect Credentials

Ask the user for ALL FOUR before doing anything:

1. **Company website URL** — The site to scrape (e.g. `https://yellowbirdfoods.com`)
2. **Fluid URL** — Their Fluid store (e.g. `https://companyname.fluid.app`)
3. **Fluid API token** — Developer token from Fluid admin
4. **Firecrawl API key** — From [firecrawl.dev](https://firecrawl.dev)
5. **Primary contact name** (optional) — Who will be the person primarily filling out the onboarding form? If unknown, leave blank — we'll report all people we find and you can assign later.

If the user provides a primary contact name, attempt to match it against people found during research and create an owner record for that person with `onboarding_contact: true`. If no name is provided, all discovered people are reported as "relevant persons" only — no owner records are created.

## Step 2: Validate Credentials

Run these three checks in parallel. If any fail, stop immediately.

| Check | Method | Success |
|-------|--------|---------|
| Source site reachable | `GET {company_url}` (follow redirects) | 200 |
| Fluid API token works | `GET {fluid_url}/api/settings/company_countries` with Bearer token | 200, extract company ID and name |
| Firecrawl key works | `POST https://api.firecrawl.dev/v1/scrape` with a test URL | 200 |

Print results:

```
[Preflight] Source site: OK {company_domain}
[Preflight] Fluid API:  OK {company}.fluid.app (Company ID: {id}, Name: {Company Name})
[Preflight] Firecrawl:  OK
```

**CRITICAL: Confirm company identity before proceeding.** Display the company name returned by the Fluid API and ask the user to confirm this is the correct store. This prevents accidentally writing onboarding data to the wrong Fluid account.

```
⚠️  This token resolves to: "Yellowbird Foods" (Company ID: 980243068)
    Store URL: https://companyname.fluid.app

Is this the correct store? (yes/no)
```

**Do NOT proceed until the user confirms.**

## Step 3: Scrape Company Website

All sub-steps run in parallel.

### 3a. Firecrawl `/extract` (required — do not skip)

```python
result = firecrawl.extract([
    company_url,
    f"{company_url}/about*",
    f"{company_url}/contact*",
    f"{company_url}/pages/about*",
    f"{company_url}/pages/contact*",
], prompt="""Extract all business information:
- Company legal name and trading/brand name
- Physical address (street, city, state, zip, country)
- Phone number(s)
- Email address(es)
- Year founded / date of incorporation
- Business description (what they sell, industry)
- Key people (names, titles, roles)
- Social media links (Facebook, LinkedIn, Instagram, TikTok, Twitter/X)
- Whether they sell health supplements, CBD, kratom, or make health claims
- Countries they ship to or operate in
- Whether they have a distributor/affiliate/MLM program
""", enableWebSearch=True)
```

### 3b. Scrape specific pages

For each page type, try all URL patterns in parallel. Skip 404s silently.

| Page | URL patterns to try | Data to extract |
|------|---------------------|-----------------|
| **Homepage** | `/` | Company name, tagline, description, hero content, social links from footer |
| **About** | `/about`, `/pages/about`, `/about-us`, `/pages/about-us` | Company story, leadership team, founding date |
| **Contact** | `/contact`, `/pages/contact`, `/contact-us`, `/pages/contact-us` | Address, phone, email, hours |
| **Terms of Service** | `/policies/terms-of-service`, `/terms`, `/pages/terms` | Full policy text, legal entity name from boilerplate |
| **Privacy Policy** | `/policies/privacy-policy`, `/privacy`, `/pages/privacy` | Full policy text |
| **Refund Policy** | `/policies/refund-policy`, `/refund`, `/pages/refund-policy` | Full policy text |
| **Shipping Policy** | `/policies/shipping-policy`, `/shipping`, `/pages/shipping` | Shipping countries, zones |
| **Team/Leadership** | `/team`, `/about/team`, `/leadership`, `/pages/team` | Owner/founder names, titles |

### 3c. Shopify detection

If the site is Shopify (check for `cdn.shopify.com` in page source or try `/meta.json`):

- `GET {company_url}/meta.json` → store name, city, state, country, ships_to_countries, currency, myshopify_domain
- `GET {company_url}/products.json?limit=5` → product types for MCC inference and health product detection

### 3d. JSON-LD structured data

Request HTML format from Firecrawl for the homepage. Parse `<script type="application/ld+json">` blocks for `Organization`, `LocalBusiness`, and `WebSite` schemas (name, legal name, address, phone, email, logo, social links).

### 3e. Social media link harvesting

Extract links to Facebook, LinkedIn, Instagram, TikTok, and Twitter/X from the homepage. Store URLs for use in Step 4 (LinkedIn company page gets fetched directly).

## Step 4: Research Public Records

Run all sub-steps in parallel after Step 3 completes. Use WebSearch and WebFetch.

### 4a. State business registry (US only)

Skip for non-US companies and note in report.

Determine the state from Step 3 results. Look up the registry domain in [references/state-registries.md](references/state-registries.md).

**Search strategy:**
1. WebSearch: `"{legal_name}" site:{registry_domain}`
2. WebSearch: `"{legal_name}" site:opencorporates.com`
3. If HQ state is NOT Delaware, also search Delaware (many companies incorporate in DE)
4. WebFetch any result pages found

**Extract:** entity type, registration/document number, date of incorporation, registered agent, principal office address, officer/director/member names and titles, entity status.

### 4b. Google Business Profile

WebSearch: `"{trading_name}" "{city}" "{state}"`

Extract from Knowledge Panel: full street address, phone, business category, hours, rating and review count.

### 4c. LinkedIn company page

If LinkedIn URL was harvested in 3e, WebFetch it directly. Otherwise WebSearch: `site:linkedin.com/company "{trading_name}"` and fetch the top result.

**Extract:** headquarters location, industry, company size, founded year, description, key employees.

### 4d. Review and trust platforms

**BBB:** WebSearch `site:bbb.org "{trading_name}"` → WebFetch profile. Extract rating (A+ through F), accreditation status, years accredited, complaint count. Canonical source — single source = HIGH confidence.

**Trustpilot:** WebSearch `site:trustpilot.com "{trading_name}"` → WebFetch profile. Extract TrustScore (1-5), total review count. Canonical source — single source = HIGH confidence.

### 4e. Negative media and regulatory scan

Run these 6 searches in parallel:

| Search | Purpose |
|--------|---------|
| `"{company_name}" lawsuit OR sued OR litigation` | Civil litigation |
| `"{company_name}" FTC OR "Federal Trade Commission"` | FTC enforcement |
| `"{company_name}" FDA OR "Food and Drug" OR recall` | FDA actions |
| `"{company_name}" "attorney general" OR "consumer complaint"` | State AG actions |
| `"{company_name}" fraud OR scam OR pyramid` | General negative media |
| `"{company_name}" "data breach" OR "security incident"` | Data/privacy incidents |

**This data is NEVER pushed to any API field.** Report-only for the human reviewer.

### 4f. Supplementary sources

- **WHOIS:** `whois {domain}` → registrant organization, state/country, domain creation date
- **Press/news:** WebSearch `"{company_name}" founded OR founder OR CEO` → founder names, funding mentions
- **Amazon:** If "Buy With Prime" or Amazon links detected, WebSearch `site:amazon.com "{company_name}" store` → brand registry name, product categories

## Step 5: Cross-Verify and Score Confidence

Build a verification matrix for every collected data point.

### Confidence levels

| Scenario | Confidence |
|----------|-----------|
| Data from the company's own website | **HIGH** — canonical for trading name, description, policies, email, products |
| Data from official government registry | **HIGH** — canonical for legal name, entity type, registration #, officers |
| Data from the platform that IS the data (Trustpilot for Trustpilot score, BBB for BBB rating) | **HIGH** — the source itself |
| 2+ independent sources agree on same value | **HIGH** — cross-verified |
| 1 non-authoritative source, data is specific and plausible | **MEDIUM** — plausible but unverified |
| Inferred from other data (MCC from products, email from name pattern) | **MEDIUM** — inference |
| Single secondary source with weak signal | **LOW** — unreliable |
| Inference requiring assumptions (nationality from name, ownership % from role) | **LOW** — do not push |
| Sources conflict | **CONFLICT** — resolve using hierarchy below |

### Generic email filter

Never attribute these email patterns to a specific person — they are company-wide addresses, not personal work emails:

- `help@`, `support@`, `info@`, `contact@`, `sales@`, `hello@`, `admin@`, `team@`, `office@`, `orders@`, `billing@`, `service@`, `customerservice@`, `cs@`

These emails are still valid as **entity-level contact emails** (e.g. `entity.email`) but must NOT be used as `owner.work_email`. If the only email found for a person is a generic one, leave `work_email` blank for that person and note it in the report.

### Conflict resolution hierarchy

1. **State business registry** — highest for legal/corporate data
2. **Company's own website** — highest for trading name, description, policies, contact
3. **Google Business Profile** — strong for address and phone
4. **LinkedIn** — strong for people and titles
5. **Directories and press** — supplementary, lowest authority

Auto-fill from most authoritative source. Note the conflict in the report with both values.

### Build the matrix

```
FIELD               | SOURCES                      | VALUES                  | CONFIDENCE | CONFLICT?
--------------------|------------------------------|-------------------------|------------|----------
legal_name          | website_tos, state_registry  | "Name", "Name LLC"      | HIGH       | Minor
trading_name        | website, meta_json, linkedin | "Name" x3               | HIGH       | No
phone               | google                       | "(555) 123-4567"        | MEDIUM     | No
```

## Step 6: Promote MEDIUM-Confidence Fields

For each MEDIUM field, run up to **2 targeted follow-up searches** to find a second source.

| Field type | Promotion search |
|------------|-----------------|
| **Address** | WebSearch: `"{company_name}" "{street_address}"` — directories, press, job postings |
| **Phone** | WebSearch: `"{company_name}" "{phone_number}"` — Yelp, Yellow Pages, social media |
| **Owner name** | WebSearch: `"{person_name}" "{company_name}" CEO OR founder OR owner` — press, bios |
| **Owner email** | WebSearch: `"{email_address}"` — press contacts, GitHub, speaker bios |
| **MCC code** | Check if Google Business Profile category or Amazon store category aligns. Multiple signals = promote to HIGH |
| **Company size** | WebSearch: `"{company_name}" employees OR team size` — press, Crunchbase, job listings |

**After promotion:**
- Promoted to HIGH → update the verification matrix
- Still MEDIUM → push it, but flag in report as "verify in admin"
- Still LOW → do NOT push, report only

Note: "founded" (press) and "incorporated" (registry) may legitimately differ. Registry date is canonical for `date_of_incorporation`.

## Step 7: MLM Assessment

Gather evidence from these signals, then present findings and **wait for user confirmation** before setting `company_is_mlm`.

| Signal | Search method | Weight |
|--------|--------------|--------|
| DSA membership | `site:dsa.org "{company_name}"` | Strong positive |
| FTC actions | `site:ftc.gov "{company_name}"` + `"{company_name}" FTC multilevel` | Strong positive |
| Recruiting language | Scraped pages: "become a distributor", "compensation plan", "downline", "upline", "income opportunity" | Moderate positive |
| Income disclosure | `"{company_name}" income disclosure statement` | Strong positive |
| Distributor pages | Check for `/pages/distributor*`, `/pages/join*`, `/pages/opportunity*`, `/pages/business-opportunity*` | Moderate positive |
| Compensation plan | `"{company_name}" compensation plan` | Strong positive |
| Product-only ecommerce | No recruitment, no multi-tier comp, direct-to-consumer | Strong negative |

### Output format

```
=== MLM Assessment ===

  DSA member:              {Yes/No match found}
  FTC actions:             {Found/None found}
  Recruiting language:     {Detected/None detected}  {quotes if found}
  Income disclosure:       {Found/Not found}
  Distributor program:     {Found/Not found}
  Compensation plan:       {Found/Not found}
  Business model:          {description}

  Recommendation: {NOT MLM / LIKELY MLM} — {reasoning}
  Set company_is_mlm to {true/false}? [awaiting user confirmation]
```

**Do not proceed to Step 8 until the user confirms.**

If confirmed MLM, also fill: compensation plan URL, income disclosure URL, distributor policy URL (if found).

## Step 8: Map to Onboarding Fields and Push

### 8a. GET existing state first

Run these 3 calls in parallel:

```
GET /api/companies/{company_id}/onboarding_info
GET /api/companies/{company_id}/entities
GET /api/companies/{company_id}/owners
```

### 8b. Create or update legal entity

Only include fields with HIGH or MEDIUM confidence. Omit LOW or missing fields.

```json
POST /api/companies/{company_id}/entities
{
  "entity": {
    "legal_name": "...",
    "trading_name": "...",
    "primary": true,
    "classification": "...",
    "address1": "...",
    "city": "...",
    "province": "...",
    "postal_code": "...",
    "country_iso": "US",
    "phone": "...",
    "phone_country_code": "+1",
    "website": "...",
    "primary_mcc": 5995,
    "registration_number": "...",
    "date_of_incorporation": "YYYY-MM-DD"
  }
}
```

### 8c. Create owner (only if primary contact was identified)

**If the user provided a primary contact name in Step 1:**

Match the name against people discovered during research (registry officers, LinkedIn, website team page). If a match is found, create an owner record using verified data for that person:

```json
POST /api/companies/{company_id}/owners
{
  "owner": {
    "entity_id": "{entity_id}",
    "full_name": "...",
    "work_email": "...",
    "position": "...",
    "is_managing_director": true,
    "is_beneficial_owner": true,
    "onboarding_contact": true
  }
}
```

If the name does NOT match any discovered person, still create the owner record with just the name and `onboarding_contact: true`. Note in the report that no public data was found for this person.

Do NOT fill: `date_of_birth`, `nationality`, `identification_number`, `percent_ownership`, `government_issued_ids`.

**If no primary contact was provided:**

Do NOT create any owner records. All discovered people go into the report under "Relevant Persons Found" (see Step 9).

### 8d. Update onboarding info

> **⚠️ MERGE BEFORE PUT — `PUT /onboarding_info` overwrites the entire blob.** GET first, deep-merge new data into existing, then PUT. Skipping the merge WILL destroy data.

```json
PUT /api/companies/{company_id}/onboarding_info
{
  "onboarding_info": {
    "underwriting_info": {
      "company_description": "...",
      "company_is_mlm": false,
      "sells_supplements": false,
      "contains_kratom": false,
      "contains_cbd": false,
      "makes_disease_claims": false,
      "bbb_rating": "...",
      "trustpilot_rating": "...",
      "terms_and_conditions": { "link": "..." },
      "refund_policy": { "link": "..." },
      "privacy_policy": { "link": "..." }
    },
    "countries_info": [
      {
        "country_iso": "US",
        "country_id": 214,
        "currency": "USD",
        "entity_id": "{entity_id}",
        "entity_legally_registered": true,
        "settlement_currency": "USD"
      }
    ]
  }
}
```

### 8e. Health product detection

Set flags based on product pages, supplement facts panels, FDA disclaimers, product categories, and Shopify `/products.json` types:

```json
{
  "sells_supplements": true,
  "contains_kratom": false,
  "contains_cbd": false,
  "makes_disease_claims": false,
  "supplement_ingredients": "..."
}
```

Also WebSearch `site:fda.gov "{company_name}"` for warnings or registrations.

### 8f. MCC code selection

Fetch `GET /api/mcc_codes` and `GET /api/business_types?country_code={country}`.

Match on: state registry classification, Google Business Profile category, product types, Amazon store category.

| Business type | MCC | Code |
|---------------|-----|------|
| Pet supplies / pet food | Pet Shops, Pet Food, and Supplies | 5995 |
| Health food / supplements | Miscellaneous Food Stores | 5499 |
| Clothing / apparel | Family Clothing Stores | 5651 |
| Cosmetics / beauty | Cosmetic Stores | 5977 |
| General ecommerce | Miscellaneous Specialty Retail | 5999 |
| Cleaning products | Specialty Cleaning | 2842 |
| Direct selling / MLM | Direct Marketing — Combination Catalog and Retail | 5965 |

MCC is MEDIUM confidence unless Google Business Profile category maps directly → promote to HIGH.

## Step 9: Report with Confidence Matrix

Print this structured summary after pushing.

```
=== Onboarding Pre-Fill Complete ===

HIGH CONFIDENCE (auto-filled):
  Legal Name:          {value} ({sources})
  Trading Name:        {value} ({sources})
  Entity Type:         {value} ({sources})
  Registration #:      {value} ({sources})
  Incorporation Date:  {value} ({sources})
  Address:             {street}, {city}, {state} {zip} ({sources})
  Phone:               {value} ({sources})
  Website:             {url}
  Primary Contact:     {name} ({sources}) — user-identified    [only if provided in Step 1]
  Description:         {truncated}...
  MLM:                 {Yes/No} ({reasoning} — user confirmed)
  Health Products:     {summary}
  Policies:            Terms {OK/missing}  Privacy {OK/missing}  Refund {OK/missing}
  Operating Country:   {country} / {currency}
  MCC:                 {code} — {description}
  BBB:                 {rating} ({source})
  Trustpilot:          {score}/5, {count} reviews ({source})

RELEVANT PERSONS FOUND:
  (These people were discovered during research but were NOT pushed as owners.
   To add one as the primary contact, create an owner record in Fluid admin.)

  {name} — {title/role} ({sources})
    Email: {email or "none found"}
    Appears in: {registry officer / LinkedIn / website team page / etc.}

MEDIUM CONFIDENCE (auto-filled, verify in admin):
  ⚠️ {field}: {value} ({reason for medium confidence})

LOW CONFIDENCE (not pushed, for reference):
  {field}: {reason}

CONFLICTS RESOLVED:
  {field}: "{value_a}" ({source_a}) vs "{value_b}" ({source_b})
  → {resolution reasoning}

NOT AVAILABLE (user must provide):
  Tax ID / EIN
  Bank account details
  Owner DOB, nationality, government ID, ownership %
  Financial statements, processing statements
  Revenue breakdown percentages
  Terms & Conditions signature

NEGATIVE MEDIA SCAN:
  Lawsuits:            {Found/None found}
  FTC actions:         {Found/None found}
  FDA actions:         {Found/None found}
  State AG actions:    {Found/None found}
  Data breaches:       {Found/None found}
  General negative:    {Found/None found}

NOTES:
  {contextual observations — shipping countries, Shopify domain, date discrepancies, etc.}

The user can now go to Settings > Onboarding in Fluid admin to review
and complete the remaining fields.
```

## Extension Points (Future Versions)

- **International registries:** UK Companies House API, OpenCorporates for EU, Corporations Canada
- **SEC EDGAR:** Beneficial ownership, financial statements for public companies
- **USPTO:** Trademark registration confirms legal entity details
- **Document pre-upload:** Download policy PDFs and upload via document upload API instead of just saving links
