from pydantic import BaseModel


class LoginDTO(BaseModel):
    document: str
    password: str