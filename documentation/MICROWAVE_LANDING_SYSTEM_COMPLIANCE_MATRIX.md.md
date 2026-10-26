# Microwave Landing System Compliance Matrix (RTCA DO-177 & ARINC 748\)

## ARINC748Forge Pro 10-Point Normative Validation Matrix

**Standard Citations:** ARINC Characteristic 748, RTCA DO-177, FAA AC 20-113, ICAO Annex 10 Vol I, ARINC 429-19

| Check ID | Requirement & Standard Reference | Verification Condition & Test Vector | Expected Result | Engine Status |
| :---- | :---- | :---- | :---- | :---- |
| **CHK-01** | C-Band 200-Channel Tuning Range *(ARINC 748 §3.2, ICAO Annex 10\)* | Verify channel tuning across \$500–699\$ mapping to \$5031.0–5090.7\\text{ MHz}\$ at 300 kHz spacing. | Frequency allocation verified across full band. | **PASS (100%)** |
| **CHK-02** | TRSB 20,000°/s Beam Timing Physics *(RTCA DO-177 §2.1, Attachment 2\)* | Validate scanning beam velocity \$V\_s \= 20,000^\\circ/\\text{s}\$ (\$50\\mu\\text{s/deg}\$) and TO-FRO \$\\Delta t\$ decoding. | Sub-microsecond pulse timing accuracy verified. | **PASS (100%)** |
| **CHK-03** | Wide-Angle Proportional Azimuth (±40°) *(ARINC 748 §2.3, DO-177)* | Verify proportional azimuth guidance across \$\\pm 40.0^\\circ\$ coverage sector for curved approaches. | Wide-angle sector guidance validated. | **PASS (100%)** |
| **CHK-04** | Proportional Elevation Coverage (0.9°–20°) *(ARINC 748 §2.4, DO-177)* | Validate vertical coverage from \$0.9^\\circ\$ to \$20.0^\\circ\$ supporting flexible glidepath angles. | Wide-angle vertical elevation validated. | **PASS (100%)** |
| **CHK-05** | Azimuth Deviation DDM Scaling *(ARINC 748 §4.2, Flight Director)* | Convert \$\\theta\_{\\text{az}}\$ to angular localizer DDM; verify \$\\pm 0.155\\text{ DDM}\$ full scale (\$\\pm 2.0^\\circ\$). | Standard ILS localizer sensitivity verified. | **PASS (100%)** |
| **CHK-06** | Elevation Deviation DDM Scaling *(ARINC 748 §4.3, Autoland)* | Convert \$\\theta\_{\\text{el}} \- 3.00^\\circ\$ to glideslope DDM; verify \$\\pm 0.175\\text{ DDM}\$ full scale (\$\\pm 0.70^\\circ\$). | Standard ILS glideslope sensitivity verified. | **PASS (100%)** |
| **CHK-07** | DME/P Precision Ranging Accuracy (\< 30m) *(ARINC 709 / ARINC 748 §4.4)* | Ingest precision DME pulses; verify distance-to-threshold output with sub-30m accuracy. | Precision threshold ranging verified. | **PASS (100%)** |
| **CHK-08** | Auxiliary Data CRC Integrity Verification *(RTCA DO-177 §2.3.4)* | Decode auxiliary data word stream (station coordinates, runway ID) with CRC validation. | Auxiliary data block integrity verified. | **PASS (100%)** |
| **CHK-09** | ARINC 429 Discrete Labels 060–064, 273 *(ARINC 748 Att. 2, ARINC 429-19)* | Verify Labels 060 (Status), 061 (Channel), 062 (Az), 063 (El), 064 (DME/P), 273 (Sector Limit). | Complete ARINC 429 discrete bus suite active. | **PASS (100%)** |
| **CHK-10** | Hardware Bit 32 Odd Parity on all Words *(ARINC 429-19 Standard)* | Verify Bit 32 odd parity computation across all generated ARINC 429 bus words. | 100% valid odd parity verified across all telemetry words. | **PASS (100%)** |

