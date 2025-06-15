"""
Unit tests for the weight conversion utility functions.
"""
import pytest
from app.models import WeightUnit
from app.utils.weight_converter import convert_weight

def test_convert_weight_same_unit():
    """Test converting weight between same units returns same value"""
    assert convert_weight(100, WeightUnit.KG, WeightUnit.KG) == 100
    assert convert_weight(100, WeightUnit.LBS, WeightUnit.LBS) == 100

def test_convert_kg_to_lbs():
    """Test converting from kilograms to pounds"""
    assert convert_weight(1, WeightUnit.KG, WeightUnit.LBS) == pytest.approx(2.20462, rel=1e-5)
    assert convert_weight(100, WeightUnit.KG, WeightUnit.LBS) == pytest.approx(220.462, rel=1e-5)
    assert convert_weight(0.5, WeightUnit.KG, WeightUnit.LBS) == pytest.approx(1.10231, rel=1e-5)
    assert convert_weight(75.5, WeightUnit.KG, WeightUnit.LBS) == pytest.approx(166.44881, rel=1e-5)

def test_convert_lbs_to_kg():
    """Test converting from pounds to kilograms"""
    assert convert_weight(1, WeightUnit.LBS, WeightUnit.KG) == pytest.approx(0.453592, rel=1e-5)
    assert convert_weight(100, WeightUnit.LBS, WeightUnit.KG) == pytest.approx(45.3592, rel=1e-5)
    assert convert_weight(0.5, WeightUnit.LBS, WeightUnit.KG) == pytest.approx(0.226796, rel=1e-5)
    assert convert_weight(165.5, WeightUnit.LBS, WeightUnit.KG) == pytest.approx(75.0697, rel=1e-5)

def test_convert_weight_zero():
    """Test converting zero weight"""
    assert convert_weight(0, WeightUnit.KG, WeightUnit.LBS) == 0
    assert convert_weight(0, WeightUnit.LBS, WeightUnit.KG) == 0

def test_convert_weight_negative():
    """Test converting negative weight"""
    assert convert_weight(-1, WeightUnit.KG, WeightUnit.LBS) == pytest.approx(-2.20462, rel=1e-5)
    assert convert_weight(-1, WeightUnit.LBS, WeightUnit.KG) == pytest.approx(-0.453592, rel=1e-5) 