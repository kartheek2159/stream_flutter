from db.models.user import User
from db.database import get_db
from helper.auth_helper import get_secret_hash
from secret_keys import SecretKeys
from fastapi import APIRouter, Depends,HTTPException,Response,Cookie
from pydantic_models.auth_models import SignUpRequest,LoginRequest,VerifySignUpRequest
import boto3
from sqlalchemy.orm import Session
router=APIRouter()

secret_keys=SecretKeys()
COGNITO_CLIENT_ID=secret_keys.COGNITO_CLIENT_ID
COGNITO_CLIENT_SECRET=secret_keys.COGNITO_CLIENT_SECRET
REGION_NAME=secret_keys.REGION_NAME
cognito_client=boto3.client("cognito-idp",region_name=REGION_NAME)

@router.post("/signup")
def signup_user(data: SignUpRequest,db:Session=Depends(get_db)):
    try:
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
        cognito_sub=cognito_response.get("UserSub")
        if not cognito_sub:
            raise HTTPException()
        new_user=User(
            name=data.name,
            email=data.email,
            cognito_sub=cognito_sub,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"msg":"Signup Successful. Please verify your email"}
    except Exception as e:
        raise HTTPException(400,f'Cognito Signup Exception:{e}')
         
@router.post("/login")
def login_user(data: LoginRequest,response:Response):
    try:
        secret_hash=get_secret_hash(username=data.email,client_id=COGNITO_CLIENT_ID,client_secret=COGNITO_CLIENT_SECRET)
        cognito_response= cognito_client.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                'USERNAME':data.email,
                'PASSWORD':data.password,
                'SECRET_HASH':secret_hash,
            },
        )
        auth_result=cognito_response.get("AuthenticationResult")
        if not auth_result:
            raise HTTPException(400,"Incorrect Cognito Response")
        access_token=auth_result.get("AccessToken")
        refresh_token=auth_result.get("RefreshToken")
        response.set_cookie(key="access_token",value=access_token,httponly=True,secure=True)
        response.set_cookie(key="refresh_token",value=refresh_token,httponly=True,secure=True)

        return {"message":"User Logged in Successfully"}
    except Exception as e:
        raise HTTPException(400,f'Cognito Login Exception:{e}')
         
@router.post("/verify_signup")
def verfiy_signup(data: VerifySignUpRequest,db:Session=Depends(get_db)):
    try:
        secret_hash=get_secret_hash(username=data.email,client_id=COGNITO_CLIENT_ID,client_secret=COGNITO_CLIENT_SECRET,)
        cognito_response= cognito_client.confirm_sign_up(
            ClientId=COGNITO_CLIENT_ID,
            Username=data.email,
            ConfirmationCode=data.otp,
            SecretHash=secret_hash, 
        )
        return {"msg":"User Verfication Success"}
    except Exception as e:
        raise HTTPException(400,f'Cognito User Verification Exception:{e}')

@router.post("/refresh")
def refresh_token(refresh_token:str=Cookie(None),user_cognito_sub:str=Cookie(None), response:Response=None):
    try:
        secret_hash=get_secret_hash(user_cognito_sub,client_id=COGNITO_CLIENT_ID,client_secret=COGNITO_CLIENT_SECRET)
        cognito_response = cognito_client.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN":refresh_token,"SECRET_HASH":secret_hash,}, 
        )
        auth_result=cognito_response.get("AuthenticationResult")
        if not auth_result:
            raise HTTPException(400,"Incorrect Cognito Response")
        access_token=auth_result.get("AccessToken")
        response.set_cookie(key="access_token",value=access_token,httponly=True,secure=True)
        return {"message":"Access Token Refreshed"}
    except Exception as e:
        raise HTTPException(400,f"Cognito token refresh Exception: {e}")