import os
from datetime import timedelta

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

if cors_origins := os.getenv('CORS_ALLOWED_ORIGINS'):
    CORS_ALLOWED_ORIGINS = [
        origin.strip() for origin in cors_origins.split(',')
    ]
else:
    CORS_ALLOWED_ORIGINS = []

CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^http://localhost(:[0-9]+)?',
]

SIMPLE_JWT = {
    'ROTATE_REFRESH_TOKENS': True,
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=600),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('JWT',),
}
