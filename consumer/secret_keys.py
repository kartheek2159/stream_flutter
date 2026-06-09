from pydantic_settings import BaseSettings  
from dotenv import load_dotenv

load_dotenv()

class SecretKeys(BaseSettings):
    REGION_NAME:str=""
    AWS_SQS_VIDEO_PROCESSING:str=""
    AWS_TRANSCODER_CLUSTER:str=""
    AWS_TRANSCODER_TASK_DEF:str=""
    AWS_TASK_LAUNCH_TYPE:str=""