from pydantic import BaseModel, Field

class PaperUpdate(BaseModel):
    roll_width: float = Field(..., gt=0)
    stock_len: float = Field(..., gt=0)
