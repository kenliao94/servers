from typing import Annotated
from pydantic import BaseModel, Field

class Enqueue(BaseModel):
    message: Annotated[str, Field(description="The message to publish")]
    queue: Annotated[str, Field(description="The name of the queue")]