from fastapi import APIRouter
from app.database import get_connection
from app.schemas.game_result import GameResultCreate

router = APIRouter()


@router.post("/game-results")
def submit_game_result(result: GameResultCreate):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Save the game result
        cursor.execute("""
            INSERT INTO game_results
                (
                    session_id,
                    score,
                    accuracy,
                    correct_answers,
                    total_questions,
                    mistakes,
                    response_time_avg,
                    completion_time
                )
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING result_id;
        """, (
            result.session_id,
            result.score,
            result.accuracy,
            result.correct_answers,
            result.total_questions,
            result.mistakes,
            result.response_time_avg,
            result.completion_time
        ))

        result_id = cursor.fetchone()[0]

        # Mark the game session as completed
        cursor.execute("""
            UPDATE game_sessions
            SET completed_at = CURRENT_TIMESTAMP
            WHERE session_id = %s;
        """, (result.session_id,))

        connection.commit()

        return {
            "message": "Game result saved successfully!",
            "result_id": str(result_id),
            "session_id": result.session_id,
            "score": result.score,
            "accuracy": result.accuracy,
            "correct_answers": result.correct_answers,
            "total_questions": result.total_questions,
            "mistakes": result.mistakes,
            "response_time_avg": result.response_time_avg,
            "completion_time": result.completion_time
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()