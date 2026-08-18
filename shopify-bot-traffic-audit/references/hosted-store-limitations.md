# Shopify-hosted evidence limits

Retrieve current vendor documentation before acting because platform support and report fields can change.

## Architecture boundary

- Shopify hosts the Online Store and provides its CDN. The merchant does not operate Shopify's Cloudflare zone and should not assume access to its raw HTTP logs.
- Shopify explicitly states that customer-managed Cloudflare proxy configurations, including orange-cloud DNS proxying and Orange-to-Orange, are unsupported and can interfere with SSL provisioning, resilience, and Shopify bot detection.
- When a merchant uses Cloudflare only as DNS with records set to DNS-only, HTTP and HTTPS traffic does not pass through the merchant's Cloudflare zone. Cloudflare therefore cannot provide HTTP request analytics or logs for those requests.
- Do not enable a Cloudflare proxy solely to obtain logs. Treat that as an unsupported production architecture change, not an audit prerequisite.

Current primary references:

- Shopify domain troubleshooting: https://help.shopify.com/en/manual/domains/troubleshoot-issues-with-domains
- Shopify storefront hosting and CDN: https://help.shopify.com/en/manual/online-store/web-performance/improving-web-performance
- Cloudflare DNS proxy status: https://developers.cloudflare.com/dns/proxy-status/

## Evidence ladder for a hosted store

Use the strongest available layers in this order:

1. Shopify Analytics `Human or bot session`, segmented by referrer, campaign, country, device, browser, and landing page.
2. Shopify paid non-test order counts and revenue for the same store-local window.
3. GA4 or BigQuery sessions, landing pages, attribution, device, browser, country, and funnel events.
4. Clarity behavior evidence for a small, non-personal sample.
5. Meta Ads or Google Ads delivery, placement, landing-page-view, invalid-traffic, and credit reports.

Shopify's bot classification is useful but proprietary and platform-reported. It does not expose raw request identity, prove malicious intent, or prove that an ad platform charged for the session.

## Current Shopify classification limit

Shopify documents a `Human or bot session` dimension and filter for session-related reports. Its classification is conservative, applies only to new incoming data from 2025-10-07, and cannot classify older sessions retroactively.

Primary reference: https://help.shopify.com/en/manual/intro-to-shopify/bots/bot-filtering

If the requested window predates that coverage or the report dimension is unavailable, mark Shopify bot classification `unavailable`; do not substitute an old report or a guessed label.

## Optional future instrumentation

Do not add pixels, apps, scripts, or theme code during this read-only audit. Such changes require a separate proposal and explicit approval. Client-side telemetry still misses automation that does not execute JavaScript, so it is not a replacement for raw request logs.
