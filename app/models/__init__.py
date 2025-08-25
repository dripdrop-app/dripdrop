from pydantic import BaseModel, ConfigDict, Field, alias_generators


class Response(BaseModel):
    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class Pagination(BaseModel):
    page: int = Field(..., ge=1)
    per_page: int = Field(..., le=50, gt=0)
