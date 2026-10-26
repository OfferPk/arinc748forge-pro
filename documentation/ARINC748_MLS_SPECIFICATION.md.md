# ARINC Characteristic 748 & RTCA DO-177 Engineering Specification

## Microwave Landing System (MLS) Airborne Receiver & TRSB Signal Processor

**Document Version:** 1.0.0 • **Status:** Approved for Implementation • **Standard Baseline:** ARINC 748, RTCA DO-177, ICAO Annex 10 Vol I, FAA AC 20-113, ARINC 429-19

---

### 1\. Executive Summary

ARINC Characteristic 748 defines the commercial avionics requirements for the **Microwave Landing System (MLS) Airborne Receiver**, providing all-weather precision approach and autoland capabilities across Category I, Category II, and Category III operational minimums.

Unlike legacy Instrument Landing Systems (ILS) which are restricted to a single fixed straight-in approach path prone to multipath reflections and terrain masking, MLS operates in the 5 GHz microwave band (5031.0 to 5090.7 MHz across 200 channels) using the **Time Reference Scanning Beam (TRSB)** technique. This provides wide-angle proportional guidance (\$\\pm 40^\\circ\$ azimuth and \$0.9^\\circ–20.0^\\circ\$ elevation), enabling curved segmented approaches around noise-sensitive urban communities or mountainous terrain.

ARINC748Forge Pro provides an avionics-grade reference implementation of the C-band 200-channel tuner, TRSB pulse timing demodulation engine, ILS-lookalike Difference in Depth of Modulation (DDM) converter, Precision DME (DME/P) interface, ARINC 429 discrete bus synthesizer, and a 10-point normative compliance audit suite.

---

### 2\. Normative Industry Standards Baseline

1. **ARINC Characteristic 748**: *Microwave Landing System (MLS) Airborne Receiver* — Avionics form factor (4-MCU LRU), RF channel tuning, discrete bus definitions, and flight deck interface standards.  
2. **RTCA DO-177**: *Minimum Operational Performance Standards (MOPS) for Microwave Landing System (MLS) Airborne Receiving Equipment* — Signal-in-space tolerances, TRSB pulse timing receiver accuracy, and flight director deviation sensitivity.  
3. **ICAO Annex 10 Volume I (Radio Navigation Aids)**: International Standards and Recommended Practices (SARPs) for microwave precision landing systems.  
4. **FAA Advisory Circular AC 20-113**: *Airworthiness Approval of Microwave Landing System (MLS) Airborne Equipment*.  
5. **ARINC 429-19**: *Mark 33 Digital Information Transfer System* — High-speed (100 kbps) digital avionics bus signaling and Bit 32 odd parity.

---

### 3\. C-Band Microwave Channel Tuning Architecture

The airborne receiver covers 200 paired channels spaced at 300 kHz increments:

- **Frequency Range**: 5031.0 MHz to 5090.7 MHz.  
- **Channel Pairing**: Channel numbers 500 to 699\.  
- **Channel Formula**: \$\$\\text{Frequency (MHz)} \= 5031.0 \+ (\\text{Channel} \- 500\) \\times 0.3\$\$ For example, Channel `550` corresponds to \$5046.0\\text{ MHz}\$ (London Heathrow EGLL Rwy 27R MLS).

---

### 4\. Time Reference Scanning Beam (TRSB) Principles

The ground transmitter sweeps a narrow fan beam back and forth across the coverage sector at a constant angular velocity: \$\$V\_s \= 20,000^\\circ/\\text{s} \= 0.05\\text{ ms/deg} \= 50\\mu\\text{s/deg}\$\$ The airborne receiver detects two pulses: the "TO" pulse during the outbound sweep and the "FRO" pulse during the return sweep.

#### 4.1 Azimuth Beam Calculation

The time interval \$\\Delta t\_{\\text{az}}\$ between TO and FRO pulses uniquely identifies the aircraft's azimuth angle \$\\theta\_{\\text{az}}\$ relative to the runway centerline: \$\$\\Delta t\_{\\text{az}} \= T\_{0,\\text{az}} \- (2 \\times V\_s^{-1} \\times \\theta\_{\\text{az}}) \= 4800\\mu\\text{s} \- (100 \\times \\theta\_{\\text{az}})\$\$ \$\$\\theta\_{\\text{az}} \= \\frac{4800\\mu\\text{s} \- \\Delta t\_{\\text{az}}}{100\\mu\\text{s/deg}}\$\$

#### 4.2 Elevation Beam Calculation

Similarly, for elevation scanning with nominal reversal interval \$T\_{0,\\text{el}} \= 3350\\mu\\text{s}\$: \$\$\\Delta t\_{\\text{el}} \= T\_{0,\\text{el}} \- (2 \\times V\_s^{-1} \\times \\theta\_{\\text{el}}) \= 3350\\mu\\text{s} \- (100 \\times \\theta\_{\\text{el}})\$\$ \$\$\\theta\_{\\text{el}} \= \\frac{3350\\mu\\text{s} \- \\Delta t\_{\\text{el}}}{100\\mu\\text{s/deg}}\$\$

---

### 5\. ILS-Lookalike DDM Guidance Scaling

To drive existing cockpit flight directors, PFD deviation needles, and Category III autoland autopilot channels without avionics refits, the ARINC 748 receiver converts angular deviations into standard Difference in Depth of Modulation (DDM):

- **Azimuth / Localizer Equivalent**: Full-scale deflection (\$\\pm 2.0\\text{ dots}\$ / \$\\pm 0.155\\text{ DDM}\$) corresponds to \$\\pm 2.00^\\circ\$ angular deviation.  
- **Elevation / Glideslope Equivalent**: Full-scale deflection (\$\\pm 2.0\\text{ dots}\$ / \$\\pm 0.175\\text{ DDM}\$) corresponds to \$\\pm 0.70^\\circ\$ displacement from the nominal \$3.00^\\circ\$ glidepath.

---

### 6\. ARINC 429 Discrete Bus Output Specification

The receiver outputs digital precision guidance on the avionics bus at high speed (100 kbps) with **Bit 32 Odd Parity**:

| Label (Octal) | Parameter Description | Format / Units | Range | Resolution |
| :---- | :---- | :---- | :---- | :---- |
| **060** | MLS Receiver Status & Mode | Discrete / Bitfield | Mode 0–3 | Discretes |
| **061** | MLS Channel Tuning Number | BNR Integer | 500 to 699 | 1 Count |
| **062** | Azimuth Deviation DDM | BNR Signed | \$\\pm 0.400\\text{ DDM}\$ | \$0.4 / 2^{11} \\text{ DDM}\$ |
| **063** | Elevation Deviation DDM | BNR Signed | \$\\pm 0.400\\text{ DDM}\$ | \$0.4 / 2^{11} \\text{ DDM}\$ |
| **064** | DME/P Precision Range | BNR Positive | \$0–64.0\\text{ NM}\$ | \$64 / 2^{15} \\text{ NM}\$ |
| **273** | Azimuth Sector Limit | BNR Positive | \$\\pm 40.0^\\circ\$ | \$64 / 2^{12} \\text{ deg}\$ |

