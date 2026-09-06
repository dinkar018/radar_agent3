"""
Unit tests for TI IWR1843BOOST synthetic SAR data generator.
"""
import os
import numpy as np
import pytest
from generate_synthetic_data import generate_sar_data

def test_generate_sar_data_shape():
    """Verify generated SAR data has the expected 3D shape (range, cross-range, 256 ADC)."""
    num_range = 16
    num_cross = 8
    num_adc = 256
    data = generate_sar_data(
        num_range_bins=num_range,
        num_cross_range=num_cross,
        num_adc_samples=num_adc,
        num_targets=2,
        seed=42,
    )
    assert data.shape == (num_range, num_cross, num_adc)
    assert np.iscomplexobj(data)
    assert data.dtype == np.complex64

def test_generate_sar_data_content():
    """Verify generated data has non-zero signal and SNR."""
    data = generate_sar_data(
        num_range_bins=8,
        num_cross_range=4,
        num_adc_samples=256,
        num_targets=1,
        snr_db=30,
        seed=1,
    )
    # Ensure signal contains energy
    power = np.mean(np.abs(data)**2)
    assert power > 0.0
    assert not np.isnan(power)
    assert not np.isinf(power)

def test_generated_files_exist():
    """Verify default synthetic files exist on disk."""
    sar_file = os.path.join(os.path.dirname(__file__), "..", "data", "radar_data", "sar_data_iwr1843.npy")
    test_file = os.path.join(os.path.dirname(__file__), "..", "data", "radar_data", "sar_data_test.npy")
    
    assert os.path.exists(sar_file), "Main SAR data file missing"
    assert os.path.exists(test_file), "Test SAR data file missing"
    
    loaded_data = np.load(test_file)
    assert loaded_data.shape == (32, 16, 256)
