from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

Priority = Literal["LOW", "MEDIUM", "HIGH"]
Status = Literal["OPEN", "IN_PROGRESS", "RESOLVED"]
Role = Literal["admin", "analyst"]

class Login(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username", mode="before")
    @classmethod
    def clean_username(cls, value):
        return value.strip() if isinstance(value, str) else value

class NewUser(Login):
    password: str = Field(min_length=12, max_length=128)
    role: Role = "analyst"

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    role: Role

class NewCase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(default="", max_length=4000)
    owner_id: int = Field(gt=0)
    priority: Priority = "MEDIUM"

class ChangeStatus(BaseModel):
    status: Status
    version: int = Field(gt=0)

class CaseOut(NewCase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: Status
    version: int
    created_at: datetime
    updated_at: datetime

class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    actor_id: int
    action: str
    detail: str
    created_at: datetime
