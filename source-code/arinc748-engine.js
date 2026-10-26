/**
 * ARINC748Forge Pro — Core Engine
 * Microwave Landing System (MLS) Airborne Receiver & TRSB Signal Processor
 * Standards: ARINC Characteristic 748, RTCA DO-177, ICAO Annex 10 Vol I
 */

class ARINC748Engine {
  constructor() {
    this.systemInfo = {
      model: 'Collins / Honeywell MMR-748 Pro',
      tailNumber: 'G-EUUM',
      flightNumber: 'BAW748',
      aircraftType: 'Airbus A320-200 / Boeing 777-200',
      activeMode: 'FULL_TRSB_GUIDANCE' // STANDBY, AZ_TRACK, EL_TRACK, FULL_TRSB_GUIDANCE
    };

    // C-Band Microwave Channel & Ground Siting (ARINC 748 §3.2)
    this.groundStation = {
      airportId: 'EGLL',
      runwayId: '27R',
      channelNumber: 550, // 5031.0 + (550 - 500) * 0.3 = 5046.0 MHz
      frequencyMhz: 5046.0,
      nominalGlidepathAngleDeg: 3.00,
      azimuthSectorLimitDeg: 40.0,
      elevationSectorMinDeg: 0.9,
      elevationSectorMaxDeg: 20.0,
      auxDataCrcValid: true
    };

    // Aircraft Approach State & TRSB Pulse Timing
    this.state = {
      distanceToThresholdNm: 3.80,
      azimuthAngleDeg: -0.45, // - is Left of centerline, + is Right
      elevationAngleDeg: 3.12, // Actual angle from ground transmitter (nominal 3.00°)
      groundSpeedKt: 140.0,
      radioAltitudeFt: 1180.0,
      rateOfDescentFpm: -680.0
    };

    // Time Reference Scanning Beam (TRSB) Physical Pulse Time Constants
    // Beam scanning velocity: 20,000 deg/s => 0.05 ms/deg (50 us/deg)
    this.trsbPhysics = {
      beamRateDegPerSec: 20000.0,
      scanVelocityUsPerDeg: 50.0,
      azimuthT0Us: 4800.0,   // Azimuth reversal interval
      elevationT0Us: 3350.0, // Elevation reversal interval
      azimuthSignalSnrDb: 38.2,
      elevationSignalSnrDb: 37.8,
      beamLockAzimuth: true,
      beamLockElevation: true
    };

    // Compute initial TRSB pulses and DDM deviations
    this.updateTRSBMath();
  }

  tuneChannel(channelNum) {
    if (channelNum >= 500 && channelNum <= 699) {
      this.groundStation.channelNumber = channelNum;
      // Formula: Freq = 5031.0 + (Channel - 500) * 0.3 MHz
      this.groundStation.frequencyMhz = parseFloat((5031.0 + (channelNum - 500) * 0.3).toFixed(1));
      return true;
    }
    return false;
  }

  setApproachGeometry(azDeg, elDeg, distNm) {
    this.state.azimuthAngleDeg = Math.max(-40.0, Math.min(40.0, azDeg));
    this.state.elevationAngleDeg = Math.max(0.5, Math.min(20.0, elDeg));
    this.state.distanceToThresholdNm = Math.max(0.1, distNm);

    this.updateTRSBMath();

    // Update Radio Altitude based on elevation angle and distance
    const distM = this.state.distanceToThresholdNm * 1852.0;
    this.state.radioAltitudeFt = Math.max(0.0, distM * Math.tan((this.state.elevationAngleDeg * Math.PI) / 180.0) * 3.28084);

    return {
      azimuthDdm: this.state.azimuthDdm,
      elevationDdm: this.state.elevationDdm,
      deltaTAzUs: this.state.deltaTAzUs,
      deltaTElUs: this.state.deltaTElUs
    };
  }

  updateTRSBMath() {
    // 1. Azimuth TRSB Delta-T: theta = (T0 - Delta_t) / (2 * 50 us/deg)
    // => Delta_t = T0 - (2 * 50 * theta) = 4800 - (100 * theta)
    this.state.deltaTAzUs = this.trsbPhysics.azimuthT0Us - (2.0 * this.trsbPhysics.scanVelocityUsPerDeg * this.state.azimuthAngleDeg);

    // 2. Elevation TRSB Delta-T: theta = (T0 - Delta_t) / (2 * 50 us/deg)
    // => Delta_t = 3350 - (100 * theta)
    this.state.deltaTElUs = this.trsbPhysics.elevationT0Us - (2.0 * this.trsbPhysics.scanVelocityUsPerDeg * this.state.elevationAngleDeg);

    // 3. ILS-Lookalike DDM Conversion (ARINC 748 §4.2)
    // Azimuth: ±2.0° full scale corresponds to ±0.155 DDM (±2 dots)
    this.state.azimuthDdm = Math.max(-0.4, Math.min(0.4, (this.state.azimuthAngleDeg / 2.0) * 0.155));

    // Elevation: Elevation deviation from 3.00° glidepath. Full scale ±0.70° corresponds to ±0.175 DDM
    const elDevDeg = this.state.elevationAngleDeg - this.groundStation.nominalGlidepathAngleDeg;
    this.state.elevationDdm = Math.max(-0.4, Math.min(0.4, (elDevDeg / 0.70) * 0.175));
  }

  // --- ARINC 429 Bus Synthesis ---
  encodeBNR(val, labelOctal, numBits, maxRange, res) {
    const labelInt = parseInt(labelOctal, 8);
    let norm = Math.round(val / res);
    const mask = (1 << numBits) - 1;

    if (norm < 0) {
      norm = ((~Math.abs(norm) + 1) & mask);
    } else {
      norm = norm & mask;
    }

    let word = (labelInt & 0xFF) | ((norm & mask) << 10) | (0x03 << 28);
    word = this.applyOddParity(word);
    return word;
  }

  generateARINC429Words() {
    // 1. Label 060 (Octal 060, Hex 0x30): MLS Receiver Status
    const label060 = 0x30;
    let data060 = 0;
    const modeCode = 3; // Full TRSB Autoland Guidance
    const azLockBit = this.trsbPhysics.beamLockAzimuth ? 1 : 0;
    const elLockBit = this.trsbPhysics.beamLockElevation ? 1 : 0;
    const auxValidBit = this.groundStation.auxDataCrcValid ? 1 : 0;

    data060 |= (modeCode & 0x07) << 10;
    data060 |= (azLockBit & 0x01) << 13;
    data060 |= (elLockBit & 0x01) << 14;
    data060 |= (auxValidBit & 0x01) << 15;
    data060 |= 0x03 << 28; // SSM Normal
    let word060 = (data060 & 0x7FFFFF00) | label060;
    word060 = this.applyOddParity(word060);

    // 2. Label 061 (Octal 061, Hex 0x31): MLS Channel Tuning (500-699)
    const label061 = 0x31;
    const chVal = this.groundStation.channelNumber & 0xFFFF;
    let word061 = (label061 & 0xFF) | (chVal << 10) | (0x03 << 28);
    word061 = this.applyOddParity(word061);

    // 3. Label 062 (Octal 062, Hex 0x32): MLS Azimuth Deviation (BNR, ±0.4 DDM, res 0.4/2^11)
    const azDdm = this.state.azimuthDdm;
    const word062 = this.encodeBNR(azDdm, '062', 12, 0.4, 0.4 / (1 << 11));

    // 4. Label 063 (Octal 063, Hex 0x33): MLS Elevation Deviation (BNR, ±0.4 DDM, res 0.4/2^11)
    const elDdm = this.state.elevationDdm;
    const word063 = this.encodeBNR(elDdm, '063', 12, 0.4, 0.4 / (1 << 11));

    // 5. Label 064 (Octal 064, Hex 0x34): DME/P Precision Range (BNR, 0-64 NM, res 64/2^15)
    const distNm = this.state.distanceToThresholdNm;
    const word064 = this.encodeBNR(distNm, '064', 15, 64.0, 64.0 / (1 << 15));

    // 6. Label 273 (Octal 273, Hex 0xBB): MLS Azimuth Coverage Sector Limit (±40.0°, res 64/2^12)
    const azLimit = this.groundStation.azimuthSectorLimitDeg;
    const word273 = this.encodeBNR(azLimit, '273', 12, 64.0, 64.0 / (1 << 12));

    return {
      label060: { octal: '060', hex: '0x' + (word060 >>> 0).toString(16).toUpperCase().padStart(8, '0'), parity: this.verifyOddParity(word060), mode: 'TRSB_AUTOLAND' },
      label061: { octal: '061', hex: '0x' + (word061 >>> 0).toString(16).toUpperCase().padStart(8, '0'), parity: this.verifyOddParity(word061), channel: this.groundStation.channelNumber },
      label062: { octal: '062', hex: '0x' + (word062 >>> 0).toString(16).toUpperCase().padStart(8, '0'), parity: this.verifyOddParity(word062), ddm: azDdm.toFixed(4) },
      label063: { octal: '063', hex: '0x' + (word063 >>> 0).toString(16).toUpperCase().padStart(8, '0'), parity: this.verifyOddParity(word063), ddm: elDdm.toFixed(4) },
      label064: { octal: '064', hex: '0x' + (word064 >>> 0).toString(16).toUpperCase().padStart(8, '0'), parity: this.verifyOddParity(word064), distNm: distNm.toFixed(2) },
      label273: { octal: '273', hex: '0x' + (word273 >>> 0).toString(16).toUpperCase().padStart(8, '0'), parity: this.verifyOddParity(word273), sectorLimit: azLimit.toFixed(1) }
    };
  }

  applyOddParity(word32) {
    let bits = word32 & 0x7FFFFFFF;
    let count = 0;
    for (let i = 0; i < 31; i++) {
      if ((bits >> i) & 1) count++;
    }
    if (count % 2 === 0) {
      bits |= (1 << 31);
    }
    return bits >>> 0;
  }

  verifyOddParity(word32) {
    let count = 0;
    for (let i = 0; i < 32; i++) {
      if ((word32 >>> i) & 1) count++;
    }
    return count % 2 === 1;
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ARINC748Engine };
}
