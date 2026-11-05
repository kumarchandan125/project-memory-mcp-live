from pydantic import BaseModel, ConfigDict, Field


class DecisionCreate(BaseModel):
    title: str = Field(
        min_length=2,
        max_length=200,
    )

    decision: str = Field(
        min_length=1,
        max_length=10000,
    )

    reasoning: str | None = Field(
        default=None,
        max_length=10000,
    )


class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    title: str
    decision: str
    reasoning: str | None