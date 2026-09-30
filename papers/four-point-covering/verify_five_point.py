#!/usr/bin/env python3
"""Verify both coefficient bounds for F = {0, 2, 7, 8, 11}."""

import argparse
import importlib.util
from pathlib import Path
import sys


CERTIFICATES = Path(__file__).resolve().parent / 'five-point-certificates'
CONTROLS = {
    'changed_case_index_rejected',
    'changed_dual_gap_rejected',
    'changed_fiber_mass_rejected',
    'duplicate_json_key_rejected',
    'negative_zero_integer_rejected',
    'nonfinite_json_rejected',
}


def read_input(name, limit):
    with (CERTIFICATES / name).open('rb') as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError(f'{name} exceeds its {limit}-byte limit')
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(
            'five_point_verifier', CERTIFICATES / 'verifier_v3.py')
        if spec is None or spec.loader is None:
            raise ImportError('cannot load the certificate verifier')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        result = verifier.verify(
            read_input('basis.json', 65536),
            read_input('certificates.ndjson', 8 * 1024**2),
            read_input('diagnostics.ndjson', 8 * 1024**2),
            checkpoint=lambda: None,
        )
        verifier.require(
            result['status'] == 'VERIFIED' and result['cases'] == 240
            and result['counts'] == {
                'PRIMAL_EXACT': 240, 'DUAL_EXACT': 0, 'UNRESOLVED': 0}
            and result['all_primal'] is True,
            'all 240 certificates must pass the exact primal checks',
        )
        verifier.require(
            result['orders_with_both_primal'] == 120
            and result['all_orders_covered'] is True,
            'both coefficient bounds must hold on all 120 weight orders',
        )
        controls = result['corruption_controls']
        verifier.require(
            set(controls) == CONTROLS
            and all(value is True for value in controls.values()),
            'all six corruption checks must reject the changed inputs',
        )
    except (OSError, ValueError, ImportError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print('Verification stopped.', file=sys.stderr)
        return 130
    print('PASS: 240 exact certificates; both bounds on all 120 orders '
          'of F={0,2,7,8,11}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
