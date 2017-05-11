from itsdangerous import URLSafeTimedSerializer as utsr
import base64

class Token():
    def __init__(self):
        self.security_key = "nafgh3uo9a9vhw9eh93f"
        self.salt = base64.encodebytes(self.security_key.encode(encoding='utf-8'))

    def generate_validate_token(self, key):
        serializer = utsr(self.security_key)
        return serializer.dumps(key, self.salt)

    def confirm_validate_token(self, token, expiration=3600):
        serializer = utsr(self.security_key)
        return serializer.loads(token, salt=self.salt, max_age=expiration)