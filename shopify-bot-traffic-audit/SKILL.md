---
name: shopify-bot-traffic-audit
description: Read-only, evidence-first audit for Shopify-hosted Online Store traffic using Shopify Analytics human-or-bot session classification, browser-authorized Shopify Admin and GA4 review, GA4 or BigQuery, Microsoft Clarity, Meta Ads, Google Ads, and paid non-test Shopify orders. Use when Codex needs to investigate suspected bot or AI-agent traffic, fake-traffic concerns, click spikes without sessions or orders, abnormal countries or devices, app-placement traffic, invalid-click concerns, or a sudden ROAS decline on a standard Shopify-hosted store.
---

# Shopify Bot Traffic Audit

Audit standard Shopify-hosted Online Stores conservatively and read-only. Separate Shopify's bot classification, measurement quality, traffic quality, commercial impact, and advertising fraud. Do not turn one weak signal into a fraud claim.

## Enforce the scope

- Support only Shopify-hosted Online Stores using Shopify's managed storefront infrastructure.
- Stop and state `unsupported_scope` for Headless, Hydrogen, custom-hosted, or reverse-proxied storefronts. Do not improvise an origin-log workflow.
- Treat unavailable raw HTTP, origin, and merchant-owned Cloudflare logs as an architecture constraint, not a failed collection step.
- Read [hosted-store-limitations.md](references/hosted-store-limitations.md) before recommending any Cloudflare, proxy, or logging action.

## Preserve the safety boundary

- Read public pages, approved exports, temporary report views, screenshots, and paid non-test Shopify order aggregates only.
- Do not change DNS or proxy settings, Shopify themes, pixels, consent settings, reports, ad placements, campaigns, budgets, users, permissions, or accounts.
- Do not block, challenge, refund, dispute, report, or exclude traffic without explicit user approval outside this skill.
- Do not request, read, type, or save passwords, MFA codes, API secrets, cookies, authorization headers, payment data, or customer contact data.
- When login is required, ask the user to take over for credential entry and MFA, then continue only after confirming the correct store and analytics property.
- Do not collect IP addresses. Use aggregate segments and non-personal dimensions.
- Treat automation as a behavior type, not proof of abuse.

## Define the audit contract

Confirm or infer these inputs before collecting data:

1. Shopify store domain and primary sales market.
2. Exact start and end timestamps with numeric UTC offsets.
3. Shopify reporting timezone.
4. Suspected channel, campaign, placement, country, device, or landing page.
5. Permission mode: `read-only` or `browser-authorized-readonly`.
6. Available evidence sources and their actual coverage.

Create `audit-manifest.json` using [input-contract.md](references/input-contract.md). Run:

```bash
python3 scripts/validate_audit_manifest.py audit-manifest.json
```

Do not call an audit complete unless the validator reports `ready` and the artifacts cover the stated window.

## Choose an access method

Use either method without depending on another skill:

- **Export-led**: inspect user-provided Shopify, GA4, Clarity, and ad-platform exports.
- **Browser-authorized**: use an available Computer Use capability to read an already authorized Shopify Admin and GA4 session. Read and follow [browser-authorized-audit.md](references/browser-authorized-audit.md). If Computer Use is unavailable, request exports and continue export-led.

The browser is an access method, not a stronger evidence source. Never raise confidence because a number was read directly from the interface.

## Choose the strongest supported audit mode

| Mode | Minimum evidence | Permitted conclusion |
|---|---|---|
| Corroborated hosted-store | Shopify human-or-bot sessions, paid non-test orders, and GA4, Clarity, or ad-platform data | Report Shopify-classified bot sessions, cross-source inconsistencies, and commercial impact |
| Paid-traffic | Ad-platform data plus Shopify sessions or GA4, with paid non-test orders when revenue is discussed | Locate click-to-session and session-to-order gaps; call it complete only when ads, Shopify sessions, measurement, and commerce are all present |
| Shopify-led | Shopify human-or-bot sessions plus Shopify paid non-test orders | Describe Shopify's classification and impact within Shopify only |
| Analytics-only | Shopify sessions, GA4, or Clarity without commerce evidence | Flag suspicious segments, tracking gaps, and traffic-quality issues only |

Label every mode except corroborated hosted-store `partial`. No supported mode proves the raw request identity or charging validity of an individual click.

## Normalize evidence before judging it

Read [source-playbooks.md](references/source-playbooks.md). Keep each source's role separate:

- Shopify Analytics establishes Shopify-reported sessions and its proprietary `Human or bot session` classification.
- GA4 or BigQuery establishes measured browser events and attribution after Google's known-bot exclusion.
- Clarity provides behavior evidence, not revenue truth or causal proof.
- Meta Ads and Google Ads establish platform-reported clicks, placements, charges, and invalid-traffic handling.
- Shopify paid non-test orders establish commercial truth.

Convert all timestamps to the Shopify store timezone while preserving original timestamps. Segment by the smallest stable non-personal key shared across sources, usually date/hour, campaign, placement, country, device, browser, referrer, and landing page.

## Audit in this order

### 1. Verify source integrity

- Record each source as `complete`, `partial`, or `unavailable`.
- Confirm timezone, data latency, sampling, consent effects, bot filtering, and export window.
- For Shopify sessions, confirm the window is on or after 2025-10-07 and that `Human or bot session` is available.
- Treat Shopify and ad-platform filtering as platform self-report, not independent proof.
- Stop exact reconciliation when windows or aggregation grains do not match.

### 2. Establish Shopify's platform classification

In Shopify Analytics, compare Human, Bot, and unclassified or unavailable session totals. Break them down by referrer, UTM source or campaign, country, device, browser, and landing page when the report supports those dimensions.

Call a session `shopify_classified_bot` only when Shopify reports it as Bot. Do not relabel Shopify's Human sessions as proven humans, and do not infer crawler identity or intent from the aggregate classification.

### 3. Reconcile the measurable funnel

Compare ad clicks, platform landing-page views, Shopify sessions, GA4 sessions, Clarity sessions, product views, add-to-cart, checkout, and paid orders. Locate the first observable break.

- Clicks without landing-page views can reflect delivery, redirects, load failure, or differing definitions.
- Landing-page views without sessions can reflect consent, JavaScript, tag failure, filtering, or automation.
- Sessions without product actions can reflect weak traffic, a poor landing page, measurement gaps, or automation.
- Checkouts without paid Shopify orders require checkout and payment diagnosis before a traffic-quality conclusion.

### 4. Classify each suspicious segment

Read [evidence-rubric.md](references/evidence-rubric.md). Assign one class and one confidence level:

- `shopify_classified_bot`
- `suspicious_automation`
- `measurement_gap`
- `traffic_quality_issue`
- `likely_human`
- `unclassified`

Use `confirmed_invalid_traffic` only when the ad platform confirms invalid traffic or credits the affected segment. Shopify's Bot label alone does not prove that an ad platform charged for invalid traffic.

### 5. Estimate business impact

Report affected sessions, ad spend, paid non-test orders, and revenue only when windows and grains match. Show a range when attribution or deduplication is uncertain. Never subtract suspected sessions from ROAS and present the result as fact.

### 6. Recommend the smallest reversible next step

Order recommendations by evidence and risk:

1. Fix broken redirects, tags, consent, landing-page errors, or timezone mismatches.
2. Add a missing temporary report view or read-only export.
3. Run a narrow placement, country, creative, or landing-page test with a control group.
4. Request an ad-platform invalid-traffic investigation with preserved reports.
5. Propose tracking, campaign, placement, or storefront changes only as unexecuted follow-up work requiring explicit approval.

Do not recommend placing a merchant Cloudflare proxy in front of Shopify to obtain logs.

## Deliver the report

Copy [report-template.md](assets/report-template.md) and complete every section. Lead with the answer and report:

- Audit status, access method, and actual coverage.
- What Shopify classified, what is corroborated, what remains unknown, and what is disproved.
- Traffic-class totals without double counting.
- The first observable funnel break.
- Revenue and spend impact with source boundaries.
- P0/P1/P2 actions, owner, validation method, and rollback condition.
- Data gaps and the smallest artifact needed next.

Keep screenshots and exports free of customer details. Store only short, redacted evidence excerpts.

## Acceptance gates

Before reporting completion, verify all of the following:

- The manifest validator passed and reported coverage matches the artifacts.
- The store is a Shopify-hosted Online Store, not Headless or reverse-proxied.
- No Cloudflare or origin logs were requested as a normal merchant prerequisite.
- No weak signal such as short engagement, foreign geography, zero conversion, mobile-app placement, or aggregate dashboard discrepancy was used alone.
- Shopify's `Human or bot session` scope and date limitation are disclosed.
- GA4's known-bot exclusion and inability to show excluded volume are disclosed when relevant.
- AI-agent automation is not mixed with a human who clicked a referral link from an AI product.
- Shopify figures use the exact window and exclude test, cancelled, and unpaid orders as appropriate.
- Every finding has a source, window, segment, confidence, alternative explanation, and validation step.
- Browser access changed no persistent setting and exposed no credentials or customer data.
- A paid-traffic audit marked complete includes current ad-platform evidence; otherwise label the paid-traffic portion `partial`.
- Any proposed external change is clearly separated from completed read-only work.

If the evidence cannot distinguish automation from measurement or traffic-quality failure, conclude `partial` or `unclassified`. Do not fill gaps with old reports, industry averages, or inaccessible request logs.
