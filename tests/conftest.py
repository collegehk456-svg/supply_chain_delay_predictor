"""
Test Configuration and Fixtures
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def sample_shipment_data():
    """Create sample shipment data for testing."""
    return {
        "warehouse_block": "A",
        "mode_of_shipment": "Flight",
        "customer_care_calls": 3,
        "customer_rating": 4.5,
        "cost_of_the_product": 5000,
        "prior_purchases": 2,
        "product_importance": "High",
        "gender": "M",
        "discount_offered": 15,
        "weight_in_gms": 2500,
    }


@pytest.fixture
def sample_batch_data():
    """Create sample batch shipment data."""
    return pd.DataFrame({
        "Warehouse_block": ["A", "B", "C", "D", "E"],
        "Mode_of_Shipment": ["Ship", "Flight", "Road", "Ship", "Flight"],
        "Customer_care_calls": [1, 2, 3, 4, 5],
        "Customer_rating": [5.0, 4.5, 3.0, 2.5, 4.0],
        "Cost_of_the_Product": [1000, 5000, 10000, 2000, 3000],
        "Prior_purchases": [0, 1, 5, 10, 2],
        "Product_importance": ["Low", "Medium", "High", "Low", "Medium"],
        "Gender": ["M", "F", "M", "F", "M"],
        "Discount_offered": [0, 5, 15, 25, 10],
        "Weight_in_gms": [500, 1500, 5000, 2000, 1000],
        "Reached_on_Time_Y_N": [0, 0, 1, 1, 0],
    })


@pytest.fixture
def temp_data_dir():
    """Create temporary directory for test data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_config():
    """Create test configuration."""
    return {
        "model": {
            "type": "xgboost",
            "threshold": 0.5,
        },
        "features": {
            "numerical": [
                "Customer_care_calls",
                "Customer_rating",
                "Cost_of_the_Product",
                "Prior_purchases",
                "Discount_offered",
                "Weight_in_gms",
            ],
            "categorical": [
                "Warehouse_block",
                "Mode_of_Shipment",
                "Product_importance",
                "Gender",
            ],
        },
    }
