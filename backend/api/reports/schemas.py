from pydantic import BaseModel
import uuid
from datetime import date

class WeeklyReportResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    week_start_date: date
    summary_md: str

    class Config:
        from_attributes = True
