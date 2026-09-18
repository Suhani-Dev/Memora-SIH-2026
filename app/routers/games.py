from fastapi import APIRouter
from app.database import get_connection

router = APIRouter()


@router.get("/games")
def get_games():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT game_id, game_name, cognitive_area, difficulty_levels
            FROM games
            WHERE is_active = TRUE
            ORDER BY game_id;
        """)

        games = cursor.fetchall()

        return {
            "games": [
                {
                    "game_id": game[0],
                    "game_name": game[1],
                    "cognitive_area": game[2],
                    "difficulty_levels": game[3]
                }
                for game in games
            ]
        }

    finally:
        cursor.close()
        connection.close()