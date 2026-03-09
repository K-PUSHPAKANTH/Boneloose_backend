from fastapi_mail import ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="srik29924@gmail.com",
    MAIL_PASSWORD="qfbpmkzxdwkwfqus",
    MAIL_FROM="srik29924@gmail.com",
    MAIL_FROM_NAME="BoneLoss",
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False
)