# Onboarding Field Coverage

Every field from the onboarding form, mapped to research sources, API location, and confidence model.

## Fields the Skill CAN Fill

| Field | Research source(s) | API location | Confidence model |
|-------|-------------------|--------------|-----------------|
| Legal name | State registry, website ToS | `entity.legal_name` | HIGH — registry is canonical; website is canonical for their own name |
| Trading name (DBA) | Website, meta.json, LinkedIn | `entity.trading_name` | HIGH — website is canonical |
| Entity classification | State registry | `entity.classification` | HIGH — registry is canonical |
| Registered office address | State registry | `entity.address1`, `city`, `province`, `postal_code`, `country_iso` | HIGH — registry is canonical |
| Principal place of business | Google Maps, state registry, website | `entity.principal_address` | HIGH if 2+ agree; MEDIUM if 1 non-authoritative |
| Registration number | State registry | `entity.registration_number` | HIGH — registry is canonical |
| Date of incorporation | State registry | `entity.date_of_incorporation` | HIGH — registry is canonical |
| Phone number | Website, Google, directories | `entity.phone` | HIGH if on website (canonical); HIGH if 2+ agree; MEDIUM if 1 external only |
| Website | Provided by user | `entity.website` | HIGH |
| Primary MCC | Inferred from products, Google category, Amazon | `entity.primary_mcc` | MEDIUM (inference); HIGH if Google category maps directly |
| Secondary MCC | Same as above | `entity.secondary_mcc` | MEDIUM (inference) |
| Company description | Website homepage + about | `underwriting_info.company_description` | HIGH — website is canonical |
| Is MLM? | DSA, FTC, site language, income disclosure | `underwriting_info.company_is_mlm` | Scored assessment — requires user confirmation |
| Owner full name | Registry officers, LinkedIn, website team page | `owner.full_name` | Only pushed if user identified primary contact in Step 1. HIGH if 2+ sources; MEDIUM if 1 (attempt promotion) |
| Owner position/title | LinkedIn, website, registry | `owner.position` | Only pushed if user identified primary contact. HIGH if 2+ sources; MEDIUM if 1 |
| Owner work email | Website contact, email pattern inference | `owner.work_email` | Only pushed if user identified primary contact. HIGH if on website; MEDIUM if inferred. Generic emails (help@, support@, info@, etc.) are excluded — entity-level only |
| Owner is managing director | Registry officer role, LinkedIn title | `owner.is_managing_director` | Only pushed if user identified primary contact. HIGH if registry says officer; MEDIUM if LinkedIn only |
| Countries of operation | Website shipping page, Shopify meta.json, press | `onboarding_info.countries_info` | HIGH — website/Shopify is canonical for where they ship |
| Settlement currency | Inferred from operating countries | `countries_info[].settlement_currency` | MEDIUM — inference from country |
| Terms & conditions URL | Website footer / policies page | `underwriting_info.terms_and_conditions.link` | HIGH — website is canonical |
| Refund policy URL | Website footer / policies page | `underwriting_info.refund_policy.link` | HIGH — website is canonical |
| Privacy policy URL | Website footer / policies page | `underwriting_info.privacy_policy.link` | HIGH — website is canonical |
| Sells supplements | Product pages, product types, FDA | `underwriting_info.sells_supplements` | HIGH — website product catalog is canonical |
| Contains kratom | Product pages, ingredient lists | `underwriting_info.contains_kratom` | HIGH — website product catalog is canonical |
| Contains CBD | Product pages, ingredient lists | `underwriting_info.contains_cbd` | HIGH — website product catalog is canonical |
| Makes disease claims | Product pages, marketing copy, FDA | `underwriting_info.makes_disease_claims` | HIGH — their own marketing is canonical |
| Supplement ingredients | Product pages, supplement facts panels | `underwriting_info.supplement_ingredients` | HIGH — website product catalog is canonical |
| BBB rating | bbb.org | `underwriting_info.bbb_rating` | HIGH — canonical source (bbb.org profile) |
| Trustpilot rating | trustpilot.com | `underwriting_info.trustpilot_rating` | HIGH — canonical source (trustpilot.com profile) |
| Income disclosure (MLM) | Web search, company site | MLM underwriting fields | HIGH if found — it's a document |
| Compensation plan (MLM) | Company site, DSA listing | MLM underwriting fields | HIGH if found — it's a document |
| Distributor policies (MLM) | Distributor-facing site pages | MLM underwriting fields | HIGH if found — it's a document |

## Fields the Skill Reports but Does NOT Push

| Field | Research source(s) | Why report-only |
|-------|-------------------|-----------------|
| Negative media findings | News search, court records, FTC, FDA | Contextual — no API field for this, goes in report |
| Management stability | LinkedIn tenure analysis, news | MEDIUM (subjective inference) — reported as context |
| Nationality of key persons | Sometimes inferable from name/location | LOW (unreliable) — report only, never push |
| Beneficial ownership (entities) | State cross-reference, SEC | MEDIUM for public companies; incomplete for private |
| Other legal entities | State cross-reference | MEDIUM — incomplete for private companies |
| Ownership percentages | SEC filings (public companies only) | HIGH if SEC; NOT AVAILABLE if private — only push if SEC data found |

## Fields the Skill CANNOT Fill

These require private data or human consent. List them in the report under "NOT AVAILABLE (user must provide)."

| Field | Why | API location |
|-------|-----|-------------|
| Tax ID / EIN | Not public | `entity.tax_id` |
| VAT ID | Not public | `entity.vat_id` |
| Bank account details | Sensitive financial data | `bank_account.*` |
| Owner date of birth | PII | `owner.date_of_birth` |
| Owner place of birth | PII | `owner.place_of_birth` |
| Owner nationality | Unreliable to infer | `owner.nationality` |
| Owner identification number | PII | `owner.identification_number` |
| Owner government ID documents | PII | `owner.government_issued_ids` |
| Owner proof of residence | PII | `owner.proof_of_residence_*` |
| Owner percentage ownership | Private (unless SEC-filing) | `owner.percent_ownership` |
| Financial statements | Private (unless SEC-filing) | `underwriting_info.financials` |
| Processing statements | Private | `entity.last_3_months_processing_statements` |
| Projected annual sales volume | Internal business data | `underwriting_info.projected_annual_sales_volume` |
| Average order value | Internal business data | `underwriting_info.average_order_value` |
| Revenue breakdown %s | Internal business data | `underwriting_info.revenue_from_*` |
| Terms & Conditions signature | Requires human consent | `terms_and_conditions_info.*` |
| Ownership flags (user_is_owner, etc.) | Legal determination by person filling form | `onboarding_info.user_is_owner` etc. |
| Business structure complexity | Legal determination | `onboarding_info.business_structure_complexity` |
| W-9 document | Must be signed by authorized person | `entity.w_9_file_*` |
