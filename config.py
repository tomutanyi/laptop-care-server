import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'postgresql://laptop_care_user:fYJzv7sNXgb9hXLNMkM0uFB4IdcEnewF@dpg-cs8altm8ii6s73c748b0-a.oregon-postgres.render.com/laptop_care'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
