import pytest

from app.models.calculation import Calculation
from app.operations.calculation_factory import CalculationFactory
from app.schemas.calculation import CalculationCreate

def test_insert_calculation_record(db_session):
    data = CalculationCreate(a=10, b=5, type="Add")
    result = CalculationFactory.calculate(data.a, data.b, data.type)

    calculation = Calculation(
        a=data.a,
        b=data.b,
        type=data.type.value,
        result=result,
    )

    db_session.add(calculation)
    db_session.commit()
    db_session.refresh(calculation)

    assert calculation.id is not None
    assert calculation.a == 10
    assert calculation.b == 5
    assert calculation.type == "Add"
    assert calculation.result == 15

def test_disallowed_division_by_zero():
    with pytest.raises(ValueError):
        CalculationFactory.calculate(10, 0, "Divide")