# Texas Instruments IWR1843 Single-Chip 76-to-81-GHz mmWave Sensor Datasheet

## 1. Device Overview
The IWR1843 is an integrated single-chip mmWave sensor based on FMCW radar technology capable of operation in the 76- to 81-GHz band with up to 4 GHz continuous chirp bandwidth. The device is built with TI's low-power 45-nm RFCMOS process and enables unprecedented levels of analog and digital integration.

## 2. RF and Analog Subsystem
- **Transmitter (TX)**: 3 transmit channels with 6-bit phase shifters (supports beamforming and MIMO SAR). Output power: 12 dBm typical.
- **Receiver (RX)**: 4 receive channels with internal low-noise mixers and baseband amplifiers. Noise figure: 12 dB typical.
- **Synthesizer**: Ultra-low phase noise VCO operating from 76 to 81 GHz. Linear frequency modulation (chirp) with programmable slope.
- **ADC Converters**: 4 dedicated high-speed 16-bit ADCs, sampling rate up to 12.5 Msps (complex 1x) or 25 Msps (real).
- **ADC Samples per Chirp**: Typically 256 or 512 samples.

## 3. Antenna and Virtual Array Configuration
- 3 TX antennas and 4 RX antennas provide a virtual uniform linear array (ULA) of 12 virtual antenna elements via Time-Division Multiplexed (TDM) MIMO.
- Virtual antenna array spacing: $\lambda/2$ across azimuth for cross-range synthetic aperture and angle-of-arrival (AoA) estimation.

## 4. Signal Characteristics and Chirp Parameters
- **Center Frequency ($f_c$)**: 77 GHz to 79 GHz (nominal 79 GHz).
- **Chirp Bandwidth ($B$)**: 4.0 GHz.
- **Chirp Duration ($T_c$)**: $25.6\ \mu\text{s}$ to $64\ \mu\text{s}$.
- **ADC Samples**: 256 complex samples per chirp ($I + jQ$).
- **Range Resolution ($\Delta R$)**:
  $$\Delta R = \frac{c}{2B} = \frac{3 \times 10^8}{2 \times 4 \times 10^9} = 0.0375\ \text{m} = 3.75\ \text{cm}$$
- **Maximum Unambiguous Range ($R_{\max}$)**:
  $$R_{\max} = \frac{f_s \cdot c}{2 \cdot S} = \frac{f_s \cdot c \cdot T_c}{2 \cdot B}$$

## 5. Raw Data Organization
The DCA1000EVM capture card collects raw ADC samples formatted as 16-bit signed integers in interleaved IQ order:
$$\text{Data Matrix Shape}: (N_{\text{chirps}}, N_{\text{rx}}, N_{\text{adc}}) \quad \text{or for SAR scans}: (N_{\text{range\_bins}}, N_{\text{cross\_range}}, 256)$$
Each sample represents the dechirped intermediate frequency (IF) signal:
$$s_{IF}(t) = A \exp\left(j \left[ 2\pi f_b t + \phi_0 \right]\right)$$
where $f_b = \frac{2 S R}{c}$ is the beat frequency proportional to target range $R$.
