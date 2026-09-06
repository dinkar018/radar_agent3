# Range Migration Algorithm (RMA) for Millimeter-Wave FMCW SAR Imaging

**Authors**: Signal Processing Research Laboratory  
**Subject**: Synthetic Aperture Radar (SAR), FMCW Radar, Point Target Imaging, 77-81 GHz  

## Abstract
This paper describes a high-resolution 2D Synthetic Aperture Radar (SAR) image reconstruction algorithm tailored for 77-81 GHz millimeter-wave FMCW radars. Using the Range Migration Algorithm ($\omega$-$k$ algorithm), the phase errors induced by spherical wavefronts at near-range are accurately focused without small-aperture approximations.

## 1. Introduction & Signal Model
Millimeter-wave FMCW radar emits linear frequency-modulated continuous waves with bandwidth $B = 4\ \text{GHz}$ and center frequency $f_c = 79\ \text{GHz}$. At each synthetic aperture position $y_n$ along the cross-range rail, the received baseband dechirped signal is:
$$s(x, y, t) = \sum_{k=1}^K \sigma_k \exp\left( -j \frac{4\pi}{c} (f_c + \alpha t) R_k(y) \right)$$
where $R_k(y) = \sqrt{(x - x_k)^2 + (y - y_k)^2}$, $\alpha = B / T_c$ is chirp rate, and $t \in [0, T_c]$ is fast-time sampled at $N_{\text{adc}} = 256$ points.

## 2. Proposed Processing Pipeline
The methodology implements the following sequential steps:
1. **Range Processing (Fast-Time FFT)**:
   Apply a Hann window along the ADC dimension (Axis 2, length 256) and perform a 1D Fast Fourier Transform (FFT) along Axis 2 to obtain the Range Profile:
   $$S(x, y, f_b) = \mathcal{F}_{\text{fast-time}}\{ s(x, y, t) \cdot w_{\text{hann}}(t) \}$$
2. **Azimuth Spatial Processing (Cross-Range FFT)**:
   Apply a 1D FFT along the cross-range axis (Axis 1) to transform the spatial data into the wavenumber domain $k_y$:
   $$S(x, k_y, f_b) = \mathcal{F}_{\text{cross-range}}\{ S(x, y, f_b) \}$$
3. **Reference Function Multiplication (RFM)**:
   Multiply by the conjugate reference phase response evaluated at scene center range $R_0$:
   $$H_{\text{ref}}^*(k_y, f_b) = \exp\left( j \sqrt{k_r^2 - k_y^2} \cdot R_0 \right)$$
   where $k_r = \frac{4\pi}{c} (f_c + \frac{B}{f_s} f_b)$.
4. **2D Reconstruction & Image Formation**:
   Perform 2D Inverse FFT (or Stolt interpolation followed by 2D IFFT) to convert from $(k_x, k_y)$ back to the spatial image domain $(x, y)$:
   $$I(x, y) = |\mathcal{F}^{-1}_{2D}\{ S_{\text{focused}}(k_x, k_y) \}|$$
5. **Output Visualization**:
   - Compute the intensity map in dB: $I_{\text{dB}} = 20 \log_{10}(|I| / \max(|I|))$.
   - Plot the 2D SAR reflectivity heat map with range (m) on the x-axis and cross-range (m) on the y-axis.
   - Print detected target coordinates and peak SNR values.
