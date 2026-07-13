from enum import Enum
from pydantic import BaseModel, ConfigDict, model_validator

class CalculationType(str, Enum):
    add = "Add"
    sub = "Sub"
    multiply = "Multiply"
    divide = "Divide"

class CalculationCreate(BaseModel):
    a: float
    b: float
    type: CalculationType

    @model_validator(mode="after")
    def validate_division(self):
        if self.type == CalculationType.divide and self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self

class CalculationRead(BaseModel):
    id: int
    a: float
    b: float
    type: CalculationType
    result: float

    model_config = ConfigDict(from_attributes=True)