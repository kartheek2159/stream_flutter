from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from secret_keys import SecretKeys
secret_keys=SecretKeys()
create_engine(secret_keys.POSTGRES_DB_URL)
sessionLocal=sessionmaker()