import hmac
import hashlib
import base64

def get_secret_hash(username:str, client_id:str,client_secret:str):
    message=username+client_id
    digest= hmac.new(
        client_secret.encode(),
        msg=message.encode(),
        digestmod=hashlib.sha256,
    ).digest()
    
    return base64.b64encode(digest).decode()