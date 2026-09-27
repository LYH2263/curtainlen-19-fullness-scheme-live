from pydantic import BaseModel, Field

class SettingsUpdate(BaseModel):
    default_fullness: float = Field(gt=0, allow_inf_nan=False)
