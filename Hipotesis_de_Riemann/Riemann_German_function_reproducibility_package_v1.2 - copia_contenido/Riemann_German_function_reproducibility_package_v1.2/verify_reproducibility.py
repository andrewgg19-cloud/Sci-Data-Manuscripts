#!/usr/bin/env python3
"""Fail-closed verifier for the canonical finite Función Germán audit."""

from __future__ import annotations

import argparse
import copy
import json
import math
from pathlib import Path
from typing import Any


def get_path(data: dict[str, Any], *parts: str) -> Any:
    value: Any = data
    for part in parts:
        if not isinstance(value, dict) or part not in value:
            raise KeyError(".".join(parts))
        value = value[part]
    return value


def find_global_claim_errors(value: Any, path: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key == "global_RH_proved" and child is not False:
                errors.append(f"{child_path} must be false, found {child!r}")
            errors.extend(find_global_claim_errors(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(find_global_claim_errors(child, f"{path}[{index}]"))
    return errors


def audit_errors(data: dict[str, Any]) -> list[str]:
    errors = find_global_claim_errors(data)

    exact_checks = [
        (("status",), "finite_numerical_audit_not_RH_proof"),
        (("ordinate_convention",), "0 < gamma <= T"),
        (("n_used",), 15),
        (("Z_off_finite_audit", "T"), 50.0),
        (("Z_off_finite_audit", "supplied_total_strip_count_N_plus_T"), 10),
        (("Z_off_finite_audit", "critical_line_zeros_in_local_data_up_to_T"), 10),
        (("Z_off_finite_audit", "Z_off_T_empty_conditional_on_supplied_count"), True),
        (("Z_off_finite_audit", "German_function", "value"), 0),
        (("Z_off_finite_audit", "German_bridge_lemma", "status"), "NV_unproved_methodological_lemma"),
        (("prime_limit_detector", "prime_limit_P"), 100),
        (("prime_limit_detector", "prime_count_pi_P"), 25),
        (("prime_limit_detector", "prime_sum_limit_Sigma_pi_P"), 1060),
        (("monte_carlo_selector", "samples"), 2000),
        (("monte_carlo_selector", "seed"), 2510),
    ]
    for parts, expected in exact_checks:
        try:
            observed = get_path(data, *parts)
        except KeyError:
            errors.append(f"missing required field {'.'.join(parts)}")
            continue
        if observed != expected:
            errors.append(
                f"{'.'.join(parts)} expected {expected!r}, found {observed!r}"
            )

    zero_source = str(data.get("zero_source", ""))
    if "critical_line_zero_ordinates_first_15.json" not in zero_source:
        errors.append("canonical audit must use the included frozen zero dataset")

    try:
        psi_100 = float(get_path(data, "prime_limit_detector", "Chebyshev_psi_P"))
        if not math.isclose(psi_100, 94.0453112293574, rel_tol=0.0, abs_tol=1e-12):
            errors.append(f"Chebyshev_psi_P expected 94.0453112293574, found {psi_100}")
    except (KeyError, TypeError, ValueError):
        errors.append("missing or invalid prime_limit_detector.Chebyshev_psi_P")

    try:
        values = get_path(
            data,
            "prime_limit_detector",
            "Chebyshev_error_diagnostic",
            "values",
        )
        if not isinstance(values, list) or len(values) != 3:
            errors.append("Chebyshev diagnostic must contain three epsilon rows")
        elif any(float(row["B_epsilon_P"]) < 0 for row in values):
            errors.append("Chebyshev diagnostic ratios must be nonnegative")
    except (KeyError, TypeError, ValueError):
        errors.append("missing or invalid finite Chebyshev diagnostic")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("audit_json", type=Path)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Also verify that a simulated global-RH claim is rejected.",
    )
    args = parser.parse_args()

    data = json.loads(args.audit_json.read_text(encoding="utf-8"))
    errors = audit_errors(data)
    if errors:
        print("VERIFICATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    if args.self_test:
        tampered = copy.deepcopy(data)
        tampered["global_RH_proved"] = True
        if not audit_errors(tampered):
            print("VERIFIER SELF-TEST FAILED: false global claim was accepted")
            return 2
        print("TAMPER SELF-TEST PASSED: global_RH_proved=true was rejected")

    print("VERIFICATION PASSED")
    print("- finite count identity checked at T=50")
    print("- finite prime channel checked at P=100")
    print("- bridge remains NV_unproved_methodological_lemma")
    print("- every global_RH_proved field remains false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
