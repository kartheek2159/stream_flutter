import redis
from secret_keys import SecretKeys
secret_keys=SecretKeys()
redis_client=redis.Redis(host=secret_keys.REDIS_URL,port=6379)