import pytest
from pydantic import BaseModel


@pytest.fixture
def provide_google_api_response():
    def _setup(pages: list[list[dict]], model: BaseModel):
        async def _run():
            for page in pages:
                yield [model.model_validate(item) for item in page]

        return lambda *args, **kwargs: _run()

    return _setup
