# TI IWR1843BOOST + DCA1000EVM Hardware Setup & Data Acquisition Guide

## 1. Hardware Architecture
The experimental setup consists of:
1. **Radar Sensor**: Texas Instruments IWR1843BOOST Evaluation Module (EVM).
2. **Raw Data Capture Card**: DCA1000EVM Real-Time Data-Capture Adapter.
3. **Linear Rail / Scanner**: 2D automated positioning rail for Synthetic Aperture Radar (SAR) collection.
4. **Host Computer**: Connected via Gigabit Ethernet (LVDS data streaming) and micro-USB (configuration UART and data UART).

## 2. RF Interface and MIMO Array Geometry
- **TX Antennas**: TX1, TX2 (azimuth spacing $4\lambda$), TX3 (elevation offset).
- **RX Antennas**: RX1, RX2, RX3, RX4 linearly spaced at $\lambda/2 = 1.9\ \text{mm}$ at 79 GHz.
- **TDM-MIMO Virtual Array**: In SAR stripmap or spotlight mode, the platform steps along the cross-range axis ($y$), collecting 256 ADC samples per chirp.

## 3. Data Ingestion Contract for Code Generator
When agent generates signal processing code:
- Raw synthetic/collected radar data is stored as a NumPy `.npy` file.
- **Array Shape**: `(N_range_bins, N_cross_range, 256)` of dtype `complex64` or `float32`.
- Axis 0 corresponds to range indexing ($x$).
- Axis 1 corresponds to cross-range synthetic aperture indexing ($y$).
- Axis 2 corresponds to Fast-Time ADC samples ($256$ samples per chirp).
- Range FFT along Axis 2 yields the range profile.
- Azimuth FFT along Axis 1 yields Doppler / Cross-range migration profiles.
- Image formation (Backprojection, Range Migration Algorithm, or 2D-FFT) reconstructs the spatial reflectivity $\sigma(x, y)$.
