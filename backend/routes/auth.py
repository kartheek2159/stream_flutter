from helper.auth_helper import get_secret_hash
from secret_keys import SecretKeys
from fastapi import APIRouter
from pydantic_models.auth_models import SignUpRequest
import boto3

router=APIRouter()

secret_keys=SecretKeys()
COGNITO_CLIENT_ID=secret_keys.COGNITO_CLIENT_ID
COGNITO_CLIENT_SECRET=secret_keys.COGNITO_CLIENT_SECRET
REGION_NAME=secret_keys.REGION_NAME

cognito_client=boto3.client("cognito-idp",region_name=REGION_NAME)

@router.post("/signup")
def signup_user(data: SignUpRequest):
    secret_hash=get_secret_hash(username=data.email,client_id=COGNITO_CLIENT_ID,client_secret=COGNITO_CLIENT_SECRET)
    cognito_response= cognito_client.sign_up(
        ClientId=COGNITO_CLIENT_ID,
        Username=data.email,
        Password=data.password,
        SecretHash=secret_hash,
        UserAttributes=[
            {"Name":"email","Value":data.email},
            {"Name":"name","Value":data.name},
        ]
    )
    # return cognito_response
    return {"msg":"Signup Successful. Please verify your email"}