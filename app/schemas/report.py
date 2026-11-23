from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DISCLAIMER = "요약은 AI가 작성해 사실과 다를 수 있습니다. 습관 점검용이며 투자 조언이 아닙니다."


class ReportCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    market: Literal["KR", "US"]
    date_from: date = Field(alias="from")
    date_to: date = Field(alias="to")

    @model_validator(mode="after")
    def check_period(self):
        if self.date_to < self.date_from:
            raise ValueError("종료일은 시작일 이후여야 합니다.")
        return self


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    market: str
    period_start: date
    period_end: date
    stats: dict[str, Any]
    summary: str | None
    created_at: datetime
    disclaimer: str = DISCLAIMER