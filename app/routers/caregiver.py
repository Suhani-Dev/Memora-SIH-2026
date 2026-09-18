from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.schemas.caregiver import CaregiverPatientCreate

router = APIRouter()


@router.post("/caregiver/assign")
def assign_patient(data: CaregiverPatientCreate):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT caregiver_id
            FROM caregivers
            WHERE caregiver_id = %s;
        """, (data.caregiver_id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Caregiver not found"
            )

        cursor.execute("""
            SELECT patient_id
            FROM patients
            WHERE patient_id = %s;
        """, (data.patient_id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )

        cursor.execute("""
            INSERT INTO caregiver_patients
                (caregiver_id, patient_id)
            VALUES
                (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (
            data.caregiver_id,
            data.patient_id
        ))

        connection.commit()

        return {
            "message": "Patient assigned successfully!"
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


@router.get("/caregiver/{caregiver_id}/patients")
def get_caregiver_patients(caregiver_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            SELECT
                p.patient_id,
                p.age_group,
                p.preferred_language
            FROM caregiver_patients cp
            JOIN patients p
                ON cp.patient_id = p.patient_id
            WHERE cp.caregiver_id = %s
            ORDER BY cp.assigned_at;
        """, (caregiver_id,))

        patients = cursor.fetchall()

        return {
            "patients": [
                {
                    "patient_id": str(row[0]),
                    "age_group": row[1],
                    "preferred_language": row[2]
                }
                for row in patients
            ]
        }

    finally:
        cursor.close()
        connection.close()
@router.get("/caregiver/{caregiver_id}/patient/{patient_id}/games")
def get_patient_game_history(caregiver_id: str, patient_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check that this caregiver is assigned to this patient
        cursor.execute("""
            SELECT 1
            FROM caregiver_patients
            WHERE caregiver_id = %s
              AND patient_id = %s;
        """, (caregiver_id, patient_id))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=403,
                detail="This patient is not assigned to this caregiver."
            )

        # Get completed game history
        cursor.execute("""
            SELECT
                gs.session_id,
                g.game_name,
                gs.difficulty_level,
                gs.started_at,
                gs.completed_at,
                gr.score,
                gr.accuracy,
                gr.correct_answers,
                gr.total_questions,
                gr.mistakes,
                gr.response_time_avg,
                gr.completion_time
            FROM game_sessions gs
            JOIN games g
                ON gs.game_id = g.game_id
            LEFT JOIN game_results gr
                ON gs.session_id = gr.session_id
            WHERE gs.patient_id = %s
              AND gs.completed_at IS NOT NULL
            ORDER BY gs.completed_at DESC;
        """, (patient_id,))

        games = cursor.fetchall()

        return {
            "patient_id": patient_id,
            "games": [
                {
                    "session_id": str(row[0]),
                    "game_name": row[1],
                    "difficulty_level": row[2],
                    "started_at": row[3],
                    "completed_at": row[4],
                    "score": row[5],
                    "accuracy": float(row[6]) if row[6] is not None else None,
                    "correct_answers": row[7],
                    "total_questions": row[8],
                    "mistakes": row[9],
                    "response_time_avg": float(row[10]) if row[10] is not None else None,
                    "completion_time": float(row[11]) if row[11] is not None else None
                }
                for row in games
            ]
        }

    finally:
        cursor.close()
        connection.close()

@router.get("/caregiver/{caregiver_id}/patient/{patient_id}/summary")
def get_patient_summary(caregiver_id: str, patient_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check that this caregiver is assigned to this patient
        cursor.execute("""
            SELECT 1
            FROM caregiver_patients
            WHERE caregiver_id = %s
              AND patient_id = %s;
        """, (caregiver_id, patient_id))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=403,
                detail="This patient is not assigned to this caregiver."
            )

        # Get patient information
        cursor.execute("""
            SELECT age_group, preferred_language, difficulty_level
            FROM patients
            WHERE patient_id = %s;
        """, (patient_id,))

        patient = cursor.fetchone()

        if patient is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )

        # Get game performance summary
        cursor.execute("""
            SELECT
                COUNT(gr.result_id),
                AVG(gr.score),
                AVG(gr.accuracy),
                AVG(gr.response_time_avg),
                SUM(gr.mistakes)
            FROM game_sessions gs
            JOIN game_results gr
                ON gs.session_id = gr.session_id
            WHERE gs.patient_id = %s
              AND gs.completed_at IS NOT NULL;
        """, (patient_id,))

        summary = cursor.fetchone()

        return {
            "patient_id": patient_id,
            "age_group": patient[0],
            "preferred_language": patient[1],
            "current_difficulty_level": patient[2],
            "games_completed": summary[0],
            "average_score": float(summary[1]) if summary[1] is not None else 0,
            "average_accuracy": float(summary[2]) if summary[2] is not None else 0,
            "average_response_time": float(summary[3]) if summary[3] is not None else 0,
            "total_mistakes": summary[4] if summary[4] is not None else 0
        }

    finally:
        cursor.close()
        connection.close()