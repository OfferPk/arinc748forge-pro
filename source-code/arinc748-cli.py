#!/usr/bin/env python3
"""
ARINC748Forge Pro — Standalone Python 3 CLI Runner & MLS Receiver
Microwave Landing System (MLS) Precision Approach & TRSB Signal Processor
Standards: ARINC Characteristic 748, RTCA DO-177, ICAO Annex 10 Vol I
"""

import sys
import math

class ARINC748Simulator:
    def __init__(self):
        self.airport = "EGLL"
        self.runway = "27R"
        self.channel = 550 # 5046.0 MHz
        self.gpa_deg = 3.00

        # Dynamics
        self.dist_nm = 3.80
        self.az_deg = -0.45 # Left of centerline
        self.el_deg = 3.12  # Above 3.00° glidepath

        # TRSB Timing constants (20,000 deg/s => 50 us/deg)
        self.az_t0_us = 4800.0
        self.el_t0_us = 3350.0

    def compute_trsb(self):
        # Delta-T TO-FRO pulse intervals
        delta_t_az = self.az_t0_us - (100.0 * self.az_deg)
        delta_t_el = self.el_t0_us - (100.0 * self.el_deg)

        # DDM scaling: Az ±2.0° = ±0.155 DDM; El ±0.70° = ±0.175 DDM
        az_ddm = max(-0.4, min(0.4, (self.az_deg / 2.0) * 0.155))
        el_dev = self.el_deg - self.gpa_deg
        el_ddm = max(-0.4, min(0.4, (el_dev / 0.70) * 0.175))

        return delta_t_az, delta_t_el, az_ddm, el_ddm

    def encode_bnr(self, val, label_octal, num_bits, res):
        label_int = int(label_octal, 8)
        norm = int(round(val / res))
        mask = (1 << num_bits) - 1

        if norm < 0:
            norm = ((~abs(norm) + 1) & mask)
        else:
            norm = norm & mask

        word = (label_int & 0xFF) | ((norm & mask) << 10) | (0x03 << 28)
        word = self.apply_odd_parity(word)
        return word

    def apply_odd_parity(self, word):
        bits = word & 0x7FFFFFFF
        count = bin(bits).count('1')
        if count % 2 == 0:
            bits |= (1 << 31)
        return bits

    def verify_odd_parity(self, word):
        return bin(word).count('1') % 2 == 1

    def generate_arinc429_words(self):
        dt_az, dt_el, az_ddm, el_ddm = self.compute_trsb()

        # Label 060: MLS Approach Status (Octal 060 = Hex 0x30)
        w060 = (0x30) | ((3 & 0x07) << 10) | (1 << 13) | (1 << 14) | (1 << 15) | (0x03 << 28)
        w060 = self.apply_odd_parity(w060)

        # Label 061: Channel Tuning (Octal 061 = Hex 0x31)
        w061 = (0x31) | ((self.channel & 0xFFFF) << 10) | (0x03 << 28)
        w061 = self.apply_odd_parity(w061)

        # Label 062: Azimuth DDM (Octal 062 = Hex 0x32)
        w062 = self.encode_bnr(az_ddm, "062", 12, 0.4 / (1 << 11))

        # Label 063: Elevation DDM (Octal 063 = Hex 0x33)
        w063 = self.encode_bnr(el_ddm, "063", 12, 0.4 / (1 << 11))

        # Label 064: DME/P Distance (Octal 064 = Hex 0x34)
        w064 = self.encode_bnr(self.dist_nm, "064", 15, 64.0 / (1 << 15))

        # Label 273: Azimuth Sector Limit (Octal 273 = Hex 0xBB)
        w273 = self.encode_bnr(40.0, "273", 12, 64.0 / (1 << 12))

        return {
            "060": {"name": "MLS Approach Status", "hex": hex(w060), "parity": self.verify_odd_parity(w060)},
            "061": {"name": "MLS Tuning Channel", "hex": hex(w061), "parity": self.verify_odd_parity(w061)},
            "062": {"name": "Azimuth Deviation DDM", "hex": hex(w062), "parity": self.verify_odd_parity(w062)},
            "063": {"name": "Elevation Deviation DDM", "hex": hex(w063), "parity": self.verify_odd_parity(w063)},
            "064": {"name": "DME/P Precision Distance", "hex": hex(w064), "parity": self.verify_odd_parity(w064)},
            "273": {"name": "Azimuth Sector Limit", "hex": hex(w273), "parity": self.verify_odd_parity(w273)}
        }

def run_cli():
    sim = ARINC748Simulator()
    print("=" * 70)
    print("ARINC748Forge Pro — Microwave Landing System (MLS) Receiver CLI")
    print("Standards: ARINC Characteristic 748, RTCA DO-177, ICAO Annex 10 Vol I")
    print("=" * 70)
    dt_az, dt_el, az_ddm, el_ddm = sim.compute_trsb()
    print(f"\n[ACTIVE MLS PRECISION APPROACH: {sim.airport} RUNWAY {sim.runway}]")
    print(f"  C-Band Channel       : CH {sim.channel} (5046.0 MHz TRSB Scanning Beam)")
    print(f"  Glidepath / Distance : Nominal GPA {sim.gpa_deg:.2f}° | DME/P {sim.dist_nm:.2f} NM")
    print(f"  Azimuth TRSB Timing  : Delta-T {dt_az:.1f} us (Angle {sim.az_deg:+.2f}° | {az_ddm:+.4f} DDM)")
    print(f"  Elevation TRSB Timing: Delta-T {dt_el:.1f} us (Angle {sim.el_deg:.2f}° | {el_ddm:+.4f} DDM)")
    print(f"  Approach Status      : FULL TRSB AUTOLAND ACTIVE (CAT III)")

    words = sim.generate_arinc429_words()
    print("\n" + "-" * 70)
    print("ARINC 429 Navigation Discrete Avionics Bus Stream (100 kbps):")
    for octal, data in words.items():
        parity_str = "VALID (PASS)" if data["parity"] else "FAIL"
        print(f"  Label {octal} ({data['name']:<27}) : {data['hex']:<12} | Parity: {parity_str}")
    print("=" * 70)

if __name__ == "__main__":
    run_cli()
