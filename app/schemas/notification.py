from pydantic import BaseModel


class NotificationCreate(BaseModel):
    recipient_account_id: str
    title: str
    message: str
    notification_type: str | None = None