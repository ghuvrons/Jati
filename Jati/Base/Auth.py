# import jwt

# Auth has user
class Auth:
    def __init__(self, user=None): 
        self.user = user # this is user model
        self.roles = []

    def generateToken(self):
        return True

class AuthHandler:
    def __init__(self, secretKey):
        self.userModel = None
        self.secretKey = secretKey

    def setUserModel(self):
        self.userModel = userModel

    def authenticate(self, authType, token):
        auth = Auth()
        user = None
        if authType == 'Basic':
            user_id, user_key = base64.b64decode(token.encode('UTF8')).decode('UTF8').split(":", 1)
            users = self.userModel.search(id=user_id, key=user_key).limit(1)
            for u in users:
                user = u
        else if authType == 'Bearer':
            pass
        auth.user = user
        return auth