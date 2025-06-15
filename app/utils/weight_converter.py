from ..models import WeightUnit

def convert_weight(weight: float, from_unit: WeightUnit, to_unit: WeightUnit) -> float:
    """
    Convert weight between kg and lbs.
    
    Args:
        weight: The weight value to convert
        from_unit: The source unit (kg or lbs)
        to_unit: The target unit (kg or lbs)
    
    Returns:
        The converted weight value
    """
    if from_unit == to_unit:
        return weight
    
    if from_unit == WeightUnit.KG and to_unit == WeightUnit.LBS:
        return weight * 2.20462
    elif from_unit == WeightUnit.LBS and to_unit == WeightUnit.KG:
        return weight / 2.20462
    else:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}") 