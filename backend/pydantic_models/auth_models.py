from pydantic import BaseModel

class SignUpRequest(BaseModel):
    name:str
    email:str
    password:str