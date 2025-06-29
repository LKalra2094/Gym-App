import enum

class WeightUnit(enum.Enum):
    KG = "kg"
    LBS = "lbs"

class UserRole(enum.Enum):
    USER = "user"    # Regular user with access to their own data
    ADMIN = "admin"  # Admin with access to all data

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say" 