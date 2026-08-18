# Source playbooks

Use only the sections needed for available sources. Retrieve current vendor documentation before relying on interface names, report availability, bot-classification coverage, or data-retention windows.

## Shopify Analytics sessions

Use Shopify's sessions reports as the platform view of hosted-store traffic. Record:

- Exact date range and Shopify reporting timezone.
- `Human or bot session` classification.
- Sessions, visitors, conversion rate, product views, add-to-cart, checkout, and completed-checkout metrics when available.
- Referrer, UTM source or campaign, country, device, browser, and landing page dimensions one at a time when supported.

The bot classification is Shopify's proprietary, conservative platform label. It applies to new incoming data from 2025-10-07 and is not retroactive. It is stronger than inferring bots from bounce rate, but it does not reveal raw requests, crawler identity, intent, or ad-platform charging validity.

Do not save a custom report during a read-only audit. Temporary filters, screenshots, and exports are sufficient.

## GA4 and BigQuery

Use GA4 for measured sessions and funnel events, not total HTTP requests. Record:

- Date/hour, session source or medium, campaign, landing page, country, device, browser, and hostname.
- `page_view`, `view_item`, `add_to_cart`, `begin_checkout`, and `purchase` where implemented.
- Transaction IDs only when needed for aggregate reconciliation with paid non-test Shopify orders.

GA4 automatically excludes known bots and cannot show how much it excluded. Browser agents that execute JavaScript may still form ordinary-looking sessions. Prefer BigQuery rows for exact event sequencing when an existing export is available; do not create a new export or integration during the audit.

## Microsoft Clarity

Use Clarity as behavior evidence:

- URL, source or medium, campaign, country or region, device, session duration, pages per session, and observed interactions.
- A small, redacted sample of recordings or heatmaps for the suspicious segment.
- JavaScript errors, dead clicks, quick backs, and page-load symptoms where available.

Clarity is not revenue truth and may filter or fail to collect some automation. A missing recording does not prove a click was fake.

## Meta Ads

Use the exact audit window at campaign, ad set, ad, placement, platform, country, and device level when available. Preserve:

- Spend, impressions, link clicks, landing-page views, and result metrics.
- Placement and publisher delivery for Audience Network when available.
- Attribution setting and report timezone.

Compare link clicks with landing-page views before comparing clicks with sessions. Treat Meta's fraud controls as platform self-report. Do not exclude placements or change delivery settings during the audit.

## Google Ads

Use campaign, ad group, network, placement, country, device, clicks, cost, invalid-click fields, and billing credits for the exact window. Preserve investigation references separately.

Do not submit an investigation or make account changes during the audit. Redact personal data from the working report.

## Shopify orders

Use Shopify as order and revenue truth for the exact audit window. Default to paid, non-test orders and exclude cancelled orders from realized revenue unless cancellations are the subject of the report.

Use aggregate counts and revenue. Do not open customer profiles or copy contact details. Do not create test orders, checkout sessions, customers, or abandoned carts.

## Shared segment table

Build the smallest table current sources support:

| Field | Purpose |
|---|---|
| Store-local date/hour | Time alignment |
| Campaign/ad/placement | Paid-traffic isolation |
| Referrer/source | Acquisition comparison |
| Country/region | Geographic concentration |
| Device/browser | Segment comparison |
| Landing page | Entry-page relevance |
| Clicks/landing-page views/sessions | Delivery and measurement reconciliation |
| Shopify Human/Bot label | Platform classification |
| Product/add-to-cart/checkout events | Intent progression |
| Paid non-test orders/revenue | Commercial impact |
| Confidence and alternative explanation | False-positive control |

Do not join on IP, email, phone, name, address, or other personal identifiers.
