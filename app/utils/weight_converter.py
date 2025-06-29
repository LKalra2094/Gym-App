from app.models.enums import WeightUnit

def convert_weight(weight: float, from_unit: WeightUnit, to_unit: WeightUnit) -> float:
    """
    Convert weight from one unit to another, handling both Enum members and string values.

    :param weight: The weight value to convert.
    :param from_unit: The starting unit (e.g., WeightUnit.KG or "kg").
    :param to_unit: The target unit (e.g., WeightUnit.LBS or "lbs").
    :return: The converted weight.
    """
    # Unwrap enum members to their string values if necessary
    from_val = from_unit.value if isinstance(from_unit, WeightUnit) else from_unit
    to_val = to_unit.value if isinstance(to_unit, WeightUnit) else to_unit

    # If units are the same, no conversion is needed
    if from_val == to_val:
        return weight

    # Perform conversion for supported pairs
    if from_val == "kg" and to_val == "lbs":
        return weight * 2.20462
    elif from_val == "lbs" and to_val == "kg":
        return weight / 2.20462
    
    # Raise an error for any other combination
    raise ValueError(f"Unsupported unit conversion: {from_val} to {to_val}") 