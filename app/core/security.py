from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
# bcrypt defines list of allowed algorithms, Industry Standard
# deprecated is for marking old password as outdated in case of adding stronger algorithm in schemes
# adding parameters for each schema would contain name__parameter = value


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password[:72])      # Limitation for safety, bcrypt password limit is 72 chars


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password[:72], hashed_password)
