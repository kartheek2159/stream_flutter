from pydantic import BaseModel

class SignUpRequest(BaseModel):
    name:str
    email:str
    password:str

class LoginRequest(BaseModel):
    email:str
    password:str

class VerifySignUpRequest(BaseModel):
    email:str
    otp:str