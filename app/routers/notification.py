from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.schemas.notification import NotificationCreate

router = APIRouter()


@router.post("/notifications")
def create_notification(notification: NotificationCreate):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT account_id
            FROM accounts
            WHERE account_id = %s;
        """, (notification.recipient_account_id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Recipient account not found"
            )

        cursor.execute("""
            INSERT INTO notifications
                (
                    recipient_account_id,
                    title,
                    message,
                    notification_type
                )
            VALUES
                (%s, %s, %s, %s)
            RETURNING
                notification_id,
                recipient_account_id,
                title,
                message,
                notification_type,
                is_read,
                created_at;
        """, (
            notification.recipient_account_id,
            notification.title,
            notification.message,
            notification.notification_type
        ))

        result = cursor.fetchone()

        connection.commit()

        return {
            "message": "Notification created successfully!",
            "notification_id": str(result[0]),
            "recipient_account_id": str(result[1]),
            "title": result[2],
            "notification_message": result[3],
            "notification_type": result[4],
            "is_read": result[5],
            "created_at": result[6]
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

@router.get("/accounts/{account_id}/notifications")
def get_notifications(account_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT account_id
            FROM accounts
            WHERE account_id = %s;
        """, (account_id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        cursor.execute("""
            SELECT
                notification_id,
                title,
                message,
                notification_type,
                is_read,
                created_at
            FROM notifications
            WHERE recipient_account_id = %s
            ORDER BY created_at DESC;
        """, (account_id,))

        notifications = cursor.fetchall()

        return {
            "account_id": account_id,
            "notifications": [
                {
                    "notification_id": str(row[0]),
                    "title": row[1],
                    "notification_message": row[2],
                    "notification_type": row[3],
                    "is_read": row[4],
                    "created_at": row[5]
                }
                for row in notifications
            ]
        }

    finally:
        cursor.close()
        connection.close()

@router.put("/notifications/{notification_id}/read")
def mark_notification_as_read(notification_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE notifications
            SET is_read = TRUE
            WHERE notification_id = %s
            RETURNING
                notification_id,
                recipient_account_id,
                title,
                message,
                notification_type,
                is_read,
                created_at;
        """, (notification_id,))

        result = cursor.fetchone()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Notification not found"
            )

        connection.commit()

        return {
            "message": "Notification marked as read!",
            "notification_id": str(result[0]),
            "recipient_account_id": str(result[1]),
            "title": result[2],
            "notification_message": result[3],
            "notification_type": result[4],
            "is_read": result[5],
            "created_at": result[6]
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()