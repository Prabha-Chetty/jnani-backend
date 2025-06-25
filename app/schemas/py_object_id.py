from typing import Annotated
from pydantic import BeforeValidator
from bson import ObjectId

# This custom type will be used for all MongoDB '_id' fields.
# It tells Pydantic to expect any value, but to convert it to a string
# before performing any other validation. This correctly handles
# the BSON ObjectId from the database.
PyObjectId = Annotated[str, BeforeValidator(str)] 