import pytest
from pydantic import ValidationError

from app.operations.calculation_factory import CalculationFactory
from app.schemas.calculation import CalculationCreate, CalculationType

def test_add():
    assert CalculationFactory.calculate(2, 3, CalculationType.add) == 5

def test_subtract():
    assert CalculationFactory.calculate(5, 3, CalculationType.sub) == 2

def test_multiply():
    assert CalculationFactory.calculate(4, 3, CalculationType.multiply) == 12

def test_divide():
    assert CalculationFactory.calculate(10, 2, CalculationType.divide) == 5

def test_divide_by_zero_validation():
    with pytest.raises(ValidationError):
        CalculationCreate(a=10, b=0, type="Divide")

def test_invalid_type_validation():
    with pytest.raises(ValidationError):
        CalculationCreate(a=1, b=2, type="Power")

def test_invalid_calculation_type():
    """Test that an invalid calculation type raises ValueError"""
    # Bypass Pydantic validation by passing an invalid enum-like object
    with pytest.raises(ValueError, match="Invalid calculation type"):
        CalculationFactory.calculate(5, 3, "InvalidType")