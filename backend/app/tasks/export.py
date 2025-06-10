import pandas as pd
from app.models.transactions import Transaction
from app.db.config import settings, celery_app
import uuid
import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.models.auth import User
from app.db.database import SyncSessionLocal

EXPORT_FOLDER = "app/static/exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

MAIL_CONFIG = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD, # type: ignore
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
)


@celery_app.task
def export_transactions_to_csv(user_id: int) -> str:
    with SyncSessionLocal() as session:
        # Получение транзакций
        transactions = session.query(Transaction).filter(Transaction.user_id == user_id).all()

        # Формирование CSV
        data = [{
            "id": t.id,
            "cash": t.cash,
            "type": t.type.value,
            "created_at": t.created_at.strftime('%Y-%m-%d'),
            "category_id": t.category_id,
        } for t in transactions]

        df = pd.DataFrame(data)
        filename = f"{user_id}_{uuid.uuid4().hex}.csv"
        filepath = os.path.join(EXPORT_FOLDER, filename)
        df.to_csv(filepath, index=False)

        # Получение email пользователя
        user = session.get(User, user_id)
        if user and user.email:
            message = MessageSchema(
                subject="Ваш экспорт готов",
                recipients=[user.email],
                body=f"Ваш файл экспорта доступен по ссылке: https://yourdomain.com/static/exports/{filename}",
                subtype="plain",
            )
            fm = FastMail(MAIL_CONFIG)
            # Отправка письма синхронно
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(fm.send_message(message))
            loop.close()

        return f"/static/exports/{filename}"