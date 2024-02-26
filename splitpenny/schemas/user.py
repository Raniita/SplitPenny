from tortoise.contrib.pydantic import pydantic_model_creator

from splitpenny.database.models import User

UserInSchema = pydantic_model_creator(
    User, name="UserIn", exclude_readonly=True
)

UserOutSchema = pydantic_model_creator(
    User, name="UserOut", exclude=["created_at"]
)

UserDatabaseSchema = pydantic_model_creator(
    User, name="User"
)