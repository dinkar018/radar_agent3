"""
Generate synthetic SAR radar data for TI IWR1843BOOST.

Simulates a Synthetic Aperture Radar dataset with:
- 3 TX antennas, 4 RX antennas (12 virtual channels)
- 256 ADC samples per chirp
- Configurable range bins and cross-range positions
- Includes simulated point targets with realistic IF signal characteristics

Output: numpy .npy file with shape (num_range_bins, num_cross_range, 256)
"""

import numpy as np
import os


def generate_sar_data(
    num_range_bins: int = 128,
    num_cross_range: int = 64,
    num_adc_samples: int = 256,
    num_targets: int = 5,
    fc: float = 79e9,          # Center frequency (Hz) - IWR1843BOOST
    bw: float = 4e9,           # Bandwidth (Hz)
    fs: float = 10e6,          # ADC sampling rate (Hz)
    snr_db: float = 20,        # Signal-to-noise ratio (dB)
    seed: int = 42,
) -> np.ndarray:
    """
    Generate synthetic SAR radar data mimicking IWR1843BOOST output.

    Args:
        num_range_bins: Number of range bin positions
        num_cross_range: Number of cross-range (azimuth) positions
        num_adc_samples: ADC samples per chirp (256 for IWR1843BOOST)
        num_targets: Number of simulated point targets
        fc: Center frequency in Hz (79 GHz for IWR1843BOOST)
        bw: Chirp bandwidth in Hz
        fs: ADC sampling rate in Hz
        snr_db: Signal-to-noise ratio in dB
        seed: Random seed for reproducibility

    Returns:
        Complex numpy array of shape (num_range_bins, num_cross_range, num_adc_samples)
    """
    np.random.seed(seed)
    c = 3e8  # Speed of light

    # Range resolution
    range_res = c / (2 * bw)
    max_range = (fs * c) / (2 * bw * (bw / (num_adc_samples / fs)))

    # Time axis for ADC samples
    t = np.arange(num_adc_samples) / fs

    # Generate random target positions
    target_ranges = np.random.uniform(1, 10, num_targets)        # meters
    target_cross_range = np.random.uniform(-5, 5, num_targets)   # meters
    target_rcs = np.random.uniform(0.5, 2.0, num_targets)        # RCS amplitude

    print(f"Generating synthetic SAR data for IWR1843BOOST")
    print(f"  Shape: ({num_range_bins}, {num_cross_range}, {num_adc_samples})")
    print(f"  Center freq: {fc/1e9:.1f} GHz")
    print(f"  Bandwidth: {bw/1e9:.1f} GHz")
    print(f"  Range resolution: {range_res*100:.2f} cm")
    print(f"  Number of targets: {num_targets}")
    print(f"  Target ranges: {target_ranges.round(2)} m")

    # Initialize data array
    data = np.zeros(
        (num_range_bins, num_cross_range, num_adc_samples),
        dtype=np.complex64,
    )

    # Chirp slope
    slope = bw / (num_adc_samples / fs)

    # Cross-range positions (synthetic aperture positions)
    cross_range_positions = np.linspace(-3, 3, num_cross_range)

    # Range bin positions
    range_positions = np.linspace(0.5, 15, num_range_bins)

    for tgt_idx in range(num_targets):
        tgt_range = target_ranges[tgt_idx]
        tgt_cross = target_cross_range[tgt_idx]
        tgt_amp = target_rcs[tgt_idx]

        for ri in range(num_range_bins):
            for ci in range(num_cross_range):
                # Distance from current aperture position to target
                dx = cross_range_positions[ci] - tgt_cross
                dy = range_positions[ri] - tgt_range
                distance = np.sqrt(dx**2 + dy**2)

                # Round-trip delay
                tau = 2 * distance / c

                # IF signal: beat frequency from FMCW dechirp
                beat_freq = slope * tau
                phase = 2 * np.pi * fc * tau

                # Generate IF signal for this target
                signal = tgt_amp * np.exp(
                    1j * (2 * np.pi * beat_freq * t + phase)
                )

                # Amplitude falls off with distance squared
                signal *= 1.0 / (distance**2 + 0.1)

                data[ri, ci, :] += signal

    # Add noise
    noise_power = 10 ** (-snr_db / 10)
    noise = np.sqrt(noise_power / 2) * (
        np.random.randn(*data.shape) + 1j * np.random.randn(*data.shape)
    )
    data += noise.astype(np.complex64)

    return data


def main():
    """Generate and save synthetic radar data."""
    output_dir = os.path.join(os.path.dirname(__file__), "data", "radar_data")
    os.makedirs(output_dir, exist_ok=True)

    # Generate main dataset
    print("=" * 60)
    print("Generating SAR dataset...")
    print("=" * 60)
    sar_data = generate_sar_data(
        num_range_bins=128,
        num_cross_range=64,
        num_adc_samples=256,
        num_targets=5,
        snr_db=20,
    )

    output_path = os.path.join(output_dir, "sar_data_iwr1843.npy")
    np.save(output_path, sar_data)
    print(f"\nSaved to: {output_path}")
    print(f"Shape: {sar_data.shape}")
    print(f"Dtype: {sar_data.dtype}")
    print(f"Size: {sar_data.nbytes / 1024 / 1024:.2f} MB")

    # Generate a smaller test dataset
    print("\n" + "=" * 60)
    print("Generating smaller test dataset...")
    print("=" * 60)
    test_data = generate_sar_data(
        num_range_bins=32,
        num_cross_range=16,
        num_adc_samples=256,
        num_targets=3,
        snr_db=15,
        seed=123,
    )

    test_path = os.path.join(output_dir, "sar_data_test.npy")
    np.save(test_path, test_data)
    print(f"\nSaved to: {test_path}")
    print(f"Shape: {test_data.shape}")
    print(f"Dtype: {test_data.dtype}")
    print(f"Size: {test_data.nbytes / 1024 / 1024:.2f} MB")

    print("\n[SUCCESS] Synthetic radar data generation complete!")


if __name__ == "__main__":
    main()
