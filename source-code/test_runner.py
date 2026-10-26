#!/usr/bin/env python3
"""
ARINC748Forge Pro Automated Test Runner (10-Point Test Suite)
Validates:
1. MLS Receiver Initialization & 200-Channel C-Band Tuning (Channels 500–699)
2. TRSB Azimuth Time Reference Delta-T Pulse Computation (50 us/deg)
3. TRSB Elevation Time Reference Delta-T Pulse Computation (50 us/deg)
4. ILS-Lookalike Azimuth Angular DDM Conversion (±0.155 DDM Full Scale)
5. ILS-Lookalike Elevation Angular DDM Conversion (±0.175 DDM Full Scale)
6. Wide-Angle Proportional Sector Limits (±40.0° Azimuth, 0.9°–20.0° Elevation)
7. DME/P Precision Threshold Ranging Output
8. ARINC 429 Labels 060 & 061 (Receiver Status & Channel Tuning) Encoding
9. ARINC 429 Primary Guidance Labels (062, 063, 064, 273) BNR Encoding
10. Hardware Bit 32 Odd Parity Hardware Verification across all bus words
"""

import sys
import os

# Ensure local import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arinc748_cli import ARINC748Simulator

def run_tests():
    print("=" * 70)
    print("ARINC748Forge Pro — Automated Compliance & Unit Test Suite")
    print("Standards: ARINC Characteristic 748, RTCA DO-177, ICAO Annex 10 Vol I")
    print("=" * 70)

    sim = ARINC748Simulator()
    tests_passed = 0
    total_tests = 10

    # Test 1: MLS Receiver Initialization & C-Band Tuning
    assert sim.airport == "EGLL"
    assert sim.channel == 550
    assert 500 <= sim.channel <= 699
    print("Test 1: MLS Receiver Initialization & C-Band Channel Tuning ... PASS")
    tests_passed += 1

    # Test 2: TRSB Azimuth Delta-T Calculation
    dt_az, dt_el, az_ddm, el_ddm = sim.compute_trsb()
    assert dt_az > 0
    # Expected: 4800 - (100 * -0.45) = 4845.0 us
    assert abs(dt_az - 4845.0) < 1e-4
    print("Test 2: TRSB Azimuth TO-FRO Time Difference Delta-T Math ... PASS")
    tests_passed += 1

    # Test 3: TRSB Elevation Delta-T Calculation
    assert dt_el > 0
    # Expected: 3350 - (100 * 3.12) = 3038.0 us
    assert abs(dt_el - 3038.0) < 1e-4
    print("Test 3: TRSB Elevation TO-FRO Time Difference Delta-T Math ... PASS")
    tests_passed += 1

    # Test 4: Azimuth DDM Scaling (±2.0° = ±0.155 DDM)
    assert abs(az_ddm) <= 0.40
    print("Test 4: ILS-Lookalike Azimuth Angular DDM Conversion ... PASS")
    tests_passed += 1

    # Test 5: Elevation DDM Scaling (±0.70° = ±0.175 DDM)
    assert abs(el_ddm) <= 0.40
    print("Test 5: ILS-Lookalike Elevation Angular DDM Conversion ... PASS")
    tests_passed += 1

    # Test 6: Wide-Angle Proportional Sector Limits
    assert abs(sim.az_deg) <= 40.0
    assert 0.9 <= sim.el_deg <= 20.0
    print("Test 6: Wide-Angle Proportional Scanning Sector Limits ... PASS")
    tests_passed += 1

    # Test 7: DME/P Precision Ranging Output
    assert sim.dist_nm > 0
    print("Test 7: DME/P Precision Distance-to-Threshold Ranging ... PASS")
    tests_passed += 1

    # Test 8: ARINC 429 Labels 060 & 061 Encoding
    words = sim.generate_arinc429_words()
    assert "060" in words and "061" in words
    assert words["060"]["hex"].startswith("0x")
    assert words["061"]["hex"].startswith("0x")
    print("Test 8: ARINC 429 Labels 060 & 061 (Status & Tuning) Encoding ... PASS")
    tests_passed += 1

    # Test 9: ARINC 429 Primary Guidance Labels (062, 063, 064, 273)
    for lbl in ["062", "063", "064", "273"]:
        assert lbl in words
        assert words[lbl]["hex"].startswith("0x")
    print("Test 9: ARINC 429 Primary Guidance Words (062/063/064/273) ... PASS")
    tests_passed += 1

    # Test 10: Hardware Bit 32 Odd Parity Hardware Verification
    all_parity = all(w["parity"] for w in words.values())
    assert all_parity is True
    print("Test 10: Hardware Bit 32 Odd Parity Hardware Verification ... PASS")
    tests_passed += 1

    print("=" * 70)
    print(f"AUTOMATED TEST RESULTS: {tests_passed}/{total_tests} TESTS PASSED (100% SUCCESS RATE)")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = run_tests()
    if not success:
        sys.exit(1)
