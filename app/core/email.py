from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from jinja2 import Environment, select_autoescape, PackageLoader
from app.core import settings
from datetime import datetime

email_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

fastmail = FastMail(email_conf)

env = Environment(
    loader=PackageLoader("app", "templates/email"),
    autoescape=select_autoescape(["html", "xml"]),
)


async def send_email(email_to: EmailStr, subject: str, template_name: str, data: dict):
    template = env.get_template(f"{template_name}.html")
    html = template.render(**data)

    message = MessageSchema(
        subject=subject, recipients=[email_to], body=html, subtype="html"
    )

    await fastmail.send_message(message)


async def send_payment_confirmation_email(
    email_to, username, order_number, amount, plan_name, expiry_date
):
    template = env.get_template("payment_confirmation.html")
    html = template.render(
        username=username,
        order_number=order_number,
        amount=amount,
        plan_name=plan_name,
        expiry_date=expiry_date,
    )
    subject = "Success Payment Confirmation"
    message = MessageSchema(
        subject=subject, recipients=[email_to], body=html, subtype="html"
    )
    await fastmail.send_message(message)


async def send_membership_expiry_reminder(
    email_to: EmailStr, username: str, days_left: int, expiry_date: datetime
):
    """
    Send membership expiry reminder email
    """
    await send_email(
        email_to=email_to,
        subject="Membership expiry reminder",
        template_name="membership_expiry",
        data={"username": username, "days_left": days_left, "expiry_date": expiry_date},
    )
