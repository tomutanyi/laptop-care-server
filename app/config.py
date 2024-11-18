import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URI"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]


    #Flask mail configurations
    MAIL_SERVER = 'smtp.elasticemail.com'  #SMTP server
    MAIL_PORT = 2525  
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ["SENDER_EMAIL"] 
    MAIL_PASSWORD = os.environ["SENDER_PASSWORD"] 
    MAIL_DEFAULT_SENDER = os.environ["SENDER_EMAIL"] 
