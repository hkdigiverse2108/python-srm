from pydantic import BaseModel, ConfigDict
from beanie import PydanticObjectId

class MongoBaseSchema(BaseModel):
    """
    Base schema for all Pydantic models in the FastAPI app.
    Ensures compatibility with MongoDB's _id and Beanie's PydanticObjectId.
    """
    model_config = ConfigDict(
        populate_by_name=True,        # Allows using standard 'id' instead of forcing '_id'
        from_attributes=True,         # Replaces V1's orm_mode=True
        arbitrary_types_allowed=True, # Required for PydanticObjectId
        json_encoders={
            PydanticObjectId: str     # Automatically converts ObjectIDs to strings for the frontend
        }
    )