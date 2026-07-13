from app.schemas.calculation import CalculationType

class CalculationFactory:
    @staticmethod
    def calculate(a: float, b: float, type: CalculationType) -> float:
        if type == CalculationType.add:
            return a + b
        if type == CalculationType.sub:
            return a - b
        if type == CalculationType.multiply:
            return a * b
        if type == CalculationType.divide:
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
        raise ValueError("Invalid calculation type")