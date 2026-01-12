from pydantic import BaseModel

class signupschema(BaseModel):
    name: str
    email: str
    password: str

class signinschema(BaseModel):
    email: str
    password: str

class analysisschema(BaseModel):
    text: str
