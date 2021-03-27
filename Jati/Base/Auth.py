# import jwt

# Auth has user
class Auth:
    def __init__(self, user=None): 
        self.user = user # this is user model

    def generateToken(self):
        return True


class AuthHandler:
    def __init__(self, secretKey):
        self.userModel = None
        self.secretKey = secretKey

    def setUserModel(self):
        self.userModel = userModel

    def authenticate(self, type, token):
        auth = Auth
        id = 1
        auth.user = self.userModel(id)
        return auth