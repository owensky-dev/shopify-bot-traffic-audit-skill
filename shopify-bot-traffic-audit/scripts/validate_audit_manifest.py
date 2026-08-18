#!/usr/bin/env python3
"""Validate scope, privacy, and source coverage for a bot-traffic audit."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ALLOWED_LAYERS = {
    "shopify_sessions",
    "measurement",
    "behavior",
    "ads",
    "commerce",
}
ALLOWED_STATUSES = {"complete", "partial", "unavailable"}
ALLOWED_PERMISSION_MODES = {"read-only", "browser-authorized-readonly"}
ALLOWED_ACCESS_METHODS = {"browser", "export", "api"}
ALLOWED_IP_HANDLING = {"not_collected"}
SENSITIVE_KEYS = {
    "password",
    "secret",
    "api_key",
    "access_token",
    "refresh_token",
    "authorization",
    "cookie",
    "email",
    "phone",
    "customer_name",
    "shipping_address",
    "billing_address",
    "full_ip",
}


def parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str):
        errors.append(f"{label} must be an ISO 8601 string with a numeric offset")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label} is not valid ISO 8601: {value!r}")
        return None
    if parsed.utcoffset() is None:
        errors.append(f"{label} must include a numeric UTC offset")
        return None
    return parsed


def find_sensitive_keys(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            normalized = str(key).lower().replace("-", "_")
            if normalized in SENSITIVE_KEYS:
                found.append(path)
            found.extend(find_sensitive_keys(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_sensitive_keys(child, f"{prefix}[{index}]"))
    return found


def validate(data: Any) -> tuple[dict[str, Any], int]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(data, dict):
        return {"status": "not_ready", "errors": ["manifest root must be an object"]}, 1

    sensitive = find_sensitive_keys(data)
    if sensitive:
        errors.append("manifest contains prohibited sensitive fields: " + ", ".join(sensitive))

    if data.get("schema_version") != 2:
        errors.append("schema_version must be 2")

    store = data.get("store")
    if not isinstance(store, dict):
        errors.append("store must be an object")
    else:
        if not isinstance(store.get("domain"), str) or not store.get("domain", "").strip():
            errors.append("store.domain is required")
        if store.get("platform") != "shopify_hosted":
            errors.append("store.platform must be 'shopify_hosted'")
        if store.get("storefront_type") != "online_store":
            errors.append("store.storefront_type must be 'online_store'")
        if not isinstance(store.get("timezone"), str) or not store.get("timezone", "").strip():
            errors.append("store.timezone is required")
        if not isinstance(store.get("primary_market"), str) or not store.get("primary_market", "").strip():
            errors.append("store.primary_market is required")

    window = data.get("window")
    start = end = None
    if not isinstance(window, dict):
        errors.append("window must be an object")
    else:
        start = parse_timestamp(window.get("start"), "window.start", errors)
        end = parse_timestamp(window.get("end"), "window.end", errors)
        if start and end and start >= end:
            errors.append("window.start must be earlier than window.end")

    mode = data.get("permission_mode")
    if mode not in ALLOWED_PERMISSION_MODES:
        errors.append(
            "permission_mode must be read-only or browser-authorized-readonly"
        )

    privacy = data.get("privacy")
    if not isinstance(privacy, dict):
        errors.append("privacy must be an object")
    else:
        if privacy.get("contains_customer_pii") is not False:
            errors.append("privacy.contains_customer_pii must be false")
        if privacy.get("ip_handling") not in ALLOWED_IP_HANDLING:
            errors.append("privacy.ip_handling must be not_collected")

    sources = data.get("sources")
    active_layers: set[str] = set()
    source_summary: list[dict[str, str]] = []
    if not isinstance(sources, list) or not sources:
        errors.append("sources must be a non-empty array")
        sources = []

    for index, source in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        name = source.get("name")
        layer = source.get("layer")
        access_method = source.get("access_method")
        status = source.get("status")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label}.name is required")
            name = f"source-{index}"
        if layer not in ALLOWED_LAYERS:
            errors.append(f"{label}.layer must be one of {sorted(ALLOWED_LAYERS)}")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{label}.status must be one of {sorted(ALLOWED_STATUSES)}")

        if status in {"complete", "partial"}:
            if access_method not in ALLOWED_ACCESS_METHODS:
                errors.append(
                    f"{label}.access_method must be one of "
                    f"{sorted(ALLOWED_ACCESS_METHODS)}"
                )
            if layer in ALLOWED_LAYERS:
                active_layers.add(layer)
            if not isinstance(source.get("artifact"), str) or not source.get("artifact", "").strip():
                errors.append(f"{label}.artifact is required for {status} sources")
            coverage_start = parse_timestamp(source.get("coverage_start"), f"{label}.coverage_start", errors)
            coverage_end = parse_timestamp(source.get("coverage_end"), f"{label}.coverage_end", errors)
            if coverage_start and coverage_end and coverage_start >= coverage_end:
                errors.append(f"{label}.coverage_start must be earlier than coverage_end")
            if start and coverage_start and coverage_start > start:
                warnings.append(f"{name} begins after the audit window")
            if end and coverage_end and coverage_end < end:
                warnings.append(f"{name} ends before the audit window")
        elif source.get("artifact"):
            warnings.append(f"{name} is unavailable but still names an artifact; verify it is not stale")

        source_summary.append(
            {
                "name": str(name),
                "layer": str(layer),
                "access_method": str(access_method),
                "status": str(status),
            }
        )

    capabilities = {
        "raw_request_automation": False,
        "shopify_bot_classification": "shopify_sessions" in active_layers,
        "browser_session_analysis": bool(
            {"shopify_sessions", "measurement", "behavior"} & active_layers
        ),
        "revenue_impact": "commerce" in active_layers,
        "paid_click_reconciliation": "ads" in active_layers
        and bool({"shopify_sessions", "measurement"} & active_layers),
        "paid_traffic_audit_ready": {
            "shopify_sessions",
            "measurement",
            "ads",
            "commerce",
        }.issubset(active_layers),
        "corroborated_hosted_store_audit": {
            "shopify_sessions",
            "commerce",
        }.issubset(active_layers)
        and bool({"measurement", "behavior", "ads"} & active_layers),
    }

    if active_layers:
        warnings.append(
            "raw HTTP request identity is unavailable by design for Shopify-hosted stores"
        )
    if mode == "browser-authorized-readonly" and not any(
        source.get("status") in {"complete", "partial"}
        and source.get("access_method") == "browser"
        for source in sources
        if isinstance(source, dict)
    ):
        warnings.append(
            "browser-authorized-readonly is set but no active browser source is recorded"
        )

    if errors:
        status = "not_ready"
        exit_code = 1
    elif capabilities["corroborated_hosted_store_audit"]:
        status = "ready"
        exit_code = 0
    elif active_layers:
        status = "partial"
        exit_code = 0
        warnings.append("source coverage supports only a partial audit")
    else:
        status = "not_ready"
        exit_code = 0
        warnings.append("at least one current evidence layer is needed for an audit")

    return (
        {
            "status": status,
            "active_layers": sorted(active_layers),
            "capabilities": capabilities,
            "sources": source_summary,
            "errors": errors,
            "warnings": warnings,
        },
        exit_code,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Shopify bot-traffic audit manifest."
    )
    parser.add_argument("input", type=Path, help="Path to audit-manifest.json")
    parser.add_argument("--out", type=Path, help="Optional JSON result path")
    args = parser.parse_args()

    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(json.dumps({"status": "not_ready", "errors": ["input file not found"]}))
        return 1
    except json.JSONDecodeError as exc:
        print(
            json.dumps(
                {"status": "not_ready", "errors": [f"invalid JSON: {exc}"]},
                ensure_ascii=False,
            )
        )
        return 1

    result, exit_code = validate(data)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
