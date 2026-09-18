from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.schemas.game_session import GameSessionCreate

router = APIRouter()


@router.post("/game-sessions")
def start_game_session(session: GameSessionCreate):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check patient exists
        cursor.execute("""
            SELECT patient_id
            FROM patients
            WHERE patient_id = %s;
        """, (session.patient_id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )

        # Check game exists
        cursor.execute("""
            SELECT game_id
            FROM games
            WHERE game_id = %s
              AND is_active = TRUE;
        """, (session.game_id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Game not found"
            )

        # Count completed Easy games
        cursor.execute("""
            SELECT COUNT(*)
            FROM game_sessions
            WHERE patient_id = %s
              AND difficulty_level = 1
              AND completed_at IS NOT NULL;
        """, (session.patient_id,))

        easy_completed = cursor.fetchone()[0]

        # Count completed Medium games
        cursor.execute("""
            SELECT COUNT(*)
            FROM game_sessions
            WHERE patient_id = %s
              AND difficulty_level = 2
              AND completed_at IS NOT NULL;
        """, (session.patient_id,))

        medium_completed = cursor.fetchone()[0]

        # Determine unlocked difficulty
        if medium_completed >= 6:
            max_difficulty = 3

        elif easy_completed >= 4:
            max_difficulty = 2

        else:
            max_difficulty = 1

        # Prevent locked difficulty
        if session.difficulty_level > max_difficulty:
            raise HTTPException(
                status_code=403,
                detail=f"Difficulty level {session.difficulty_level} is not unlocked yet."
            )

        # Create game session
        cursor.execute("""
            INSERT INTO game_sessions
                (patient_id, game_id, difficulty_level)
            VALUES
                (%s, %s, %s)
            RETURNING session_id, patient_id, game_id, difficulty_level;
        """, (
            session.patient_id,
            session.game_id,
            session.difficulty_level
        ))

        result = cursor.fetchone()

        connection.commit()

        return {
            "message": "Game session started!",
            "session_id": str(result[0]),
            "patient_id": str(result[1]),
            "game_id": result[2],
            "difficulty_level": result[3]
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

@router.get("/patients/{patient_id}/progress")
def get_patient_progress(patient_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT COUNT(*)
            FROM game_sessions
            WHERE patient_id = %s
              AND difficulty_level = 1
              AND completed_at IS NOT NULL;
        """, (patient_id,))

        easy_completed = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM game_sessions
            WHERE patient_id = %s
              AND difficulty_level = 2
              AND completed_at IS NOT NULL;
        """, (patient_id,))

        medium_completed = cursor.fetchone()[0]

        if medium_completed >= 6:
            current_max_difficulty = 3

        elif easy_completed >= 4:
            current_max_difficulty = 2

        else:
            current_max_difficulty = 1

        return {
            "patient_id": patient_id,
            "easy_completed": easy_completed,
            "medium_completed": medium_completed,
            "easy_unlocked": True,
            "medium_unlocked": easy_completed >= 4,
            "hard_unlocked": medium_completed >= 6,
            "current_max_difficulty": current_max_difficulty
        }

    finally:
        cursor.close()
        connection.close()