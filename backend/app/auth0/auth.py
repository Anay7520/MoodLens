import auth0
from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
from backend.app.config import AUTH0_DOMAIN, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET, AUTH0_AUDIENCE, AUTH0_ALGORITHMS
from jose import jwt
from urllib.request import urlopen
import json

class Auth0Service:
    def __init__(self):
        self.domain = AUTH0_DOMAIN
        self.client_id = AUTH0_CLIENT_ID
        self.client_secret = AUTH0_CLIENT_SECRET
        self.audience = AUTH0_AUDIENCE
        self.algorithms = AUTH0_ALGORITHMS

    def get_token(self, username, password):
        """Get access token using username/password"""
        get_token = GetToken(self.domain)
        token = get_token.login(
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=username,
            password=password,
            realm='Username-Password-Authentication',
            audience=self.audience,
            scope='openid profile email'
        )
        return token

    def verify_token(self, token):
        """Verify JWT token"""
        jsonurl = urlopen(f"https://{self.domain}/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)

        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=self.algorithms,
                    audience=self.audience,
                    issuer=f"https://{self.domain}/"
                )
                return payload
            except jwt.ExpiredSignatureError:
                raise Exception("Token has expired")
            except jwt.JWTClaimsError:
                raise Exception("Incorrect claims, please check the audience and issuer")
            except Exception:
                raise Exception("Unable to parse authentication token")
        else:
            raise Exception("Unable to find appropriate key")

    def get_user_info(self, access_token):
        """Get user info from Auth0"""
        auth0_api = Auth0(self.domain, access_token)
        user_info = auth0_api.users.get('me')
        return user_info

# Global instance
auth0_service = Auth0Service()

