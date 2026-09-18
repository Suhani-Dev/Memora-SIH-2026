import bcrypt
from fastapi import APIRouter
from app.database import get_connection
from app.schemas.auth import SignupRequest, LoginRequest

router = APIRouter()


@router.post("/auth/signup")
def signup(user: SignupRequest):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        password_hash = bcrypt.hashpw(
            user.password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cursor.execute("""
            INSERT INTO accounts (email, password_hash, role)
            VALUES (%s, %s, %s)
            RETURNING account_id, email, role;
        """, (
            user.email,
            password_hash,
            user.role
        ))

        account = cursor.fetchone()
        account_id = account[0]

        if user.role == "patient":

            cursor.execute("""
                INSERT INTO patients
                    (preferred_language, age_group, difficulty_level, account_id)
                VALUES
                    ('English', '60-69', 1, %s);
            """, (account_id,))

        elif user.role == "caregiver":

            cursor.execute("""
                INSERT INTO caregivers
                    (account_id)
                VALUES
                    (%s);
            """, (account_id,))

        connection.commit()

        return {
            "message": "Account created successfully!",
            "account_id": str(account[0]),
            "email": account[1],
            "role": account[2]
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


@router.post("/auth/login")
def login(user: LoginRequest):

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT account_id, email, password_hash, role
            FROM accounts
            WHERE email = %s;
        """, (user.email,))

        account = cursor.fetchone()

        if account is None:
            return {
                "message": "Invalid email or password"
            }

        if not bcrypt.checkpw(
            user.password.encode("utf-8"),
            account[2].encode("utf-8")
        ):
            return {
                "message": "Invalid email or password"
            }

        return {
            "message": "Login successful!",
            "account_id": str(account[0]),
            "email": account[1],
            "role": account[3]
        }

    finally:
        cursor.close()
        connection.close()