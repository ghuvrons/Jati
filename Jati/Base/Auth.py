import base64, hashlib, binascii, os

# Auth has user
class Auth:

    def __init__(self, secretKey, user=None): 
        self.__secret_key = secretKey
        self.user = user # this is user model

        self.roles = []


    def generateToken(self):
        if self.user is not None:
            return self.user.generateToken()
        return None

class AuthHandler:

    def __init__(self):
        self.userModel = None
        self.secretKey = "Jati-Key"


    def setUserModel(self, userModel):
        self.userModel = userModel


    def setSecretKey(self, secretKey):
        self.secretKey = secretKey


    def authenticate(self, authType, token, auth = None):
        if auth is None:
            auth = Auth(self.secretKey)
        user = None
        if authType == 'Basic':
            user_id, user_key = base64.b64decode(token.encode('UTF8')).decode('UTF8').split(":", 1)
            user = self.userModel.authenticate(user_id, user_key)
        elif authType == 'Bearer':
            user = self.userModel.authenticateByToken(token)
        auth.user = user
        return auth


class AuthModel:
    ACCESS_TOKEN_COL = "access_token"


    @classmethod
    def authenticate(cls, username, password):
        user = cls.one(username=username, password=password)
        return user


    @classmethod
    def authenticateByToken(cls, token):
        return cls.one(**{cls.ACCESS_TOKEN_COL:token})


    def generateToken(self):
        token = getattr(self, self.ACCESS_TOKEN_COL)
        if token is None:
            token = hashlib.sha256(os.urandom(64)).hexdigest()
            setattr(self, self.ACCESS_TOKEN_COL, token)
            self.save()
        return token


    def can(self):
        return True