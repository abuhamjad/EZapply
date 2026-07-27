from pydantic import BaseModel


class ApplicationDataPoint(BaseModel):
    day: str
    sent: int
    responses: int


class PlatformDataPoint(BaseModel):
    platform: str
    applied: int
    responses: int


class AnalyticsResponse(BaseModel):
    application_data: list[ApplicationDataPoint]
    platform_data: list[PlatformDataPoint]
