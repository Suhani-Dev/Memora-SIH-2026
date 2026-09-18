from fastapi import APIRouter, HTTPException
from app.database import get_connection
from app.schemas.daily_task import DailyTaskCreate

router = APIRouter()


@router.post("/daily-tasks")
def create_daily_task(task: DailyTaskCreate):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check patient exists
        cursor.execute("""
            SELECT patient_id
            FROM patients
            WHERE patient_id = %s;
        """, (task.patient_id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )

        # Create task
        cursor.execute("""
            INSERT INTO daily_tasks
                (
                    patient_id,
                    task_type,
                    task_description,
                    scheduled_time
                )
            VALUES
                (%s, %s, %s, %s)
            RETURNING task_id, patient_id, task_type,
                      task_description, scheduled_time, completed;
        """, (
            task.patient_id,
            task.task_type,
            task.task_description,
            task.scheduled_time
        ))

        result = cursor.fetchone()

        connection.commit()

        return {
            "message": "Daily task created successfully!",
            "task_id": str(result[0]),
            "patient_id": str(result[1]),
            "task_type": result[2],
            "task_description": result[3],
            "scheduled_time": str(result[4]) if result[4] else None,
            "completed": result[5]
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

@router.get("/patients/{patient_id}/daily-tasks")
def get_daily_tasks(patient_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check patient exists
        cursor.execute("""
            SELECT patient_id
            FROM patients
            WHERE patient_id = %s;
        """, (patient_id,))

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found"
            )

        cursor.execute("""
            SELECT
                task_id,
                task_type,
                task_description,
                scheduled_time,
                completed,
                created_at
            FROM daily_tasks
            WHERE patient_id = %s
            ORDER BY scheduled_time NULLS LAST, created_at;
        """, (patient_id,))

        tasks = cursor.fetchall()

        return {
            "patient_id": patient_id,
            "tasks": [
                {
                    "task_id": str(row[0]),
                    "task_type": row[1],
                    "task_description": row[2],
                    "scheduled_time": str(row[3]) if row[3] else None,
                    "completed": row[4],
                    "created_at": row[5]
                }
                for row in tasks
            ]
        }

    finally:
        cursor.close()
        connection.close()

@router.put("/daily-tasks/{task_id}/complete")
def complete_daily_task(task_id: str):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            UPDATE daily_tasks
            SET completed = TRUE
            WHERE task_id = %s
            RETURNING task_id, patient_id, task_type,
                      task_description, scheduled_time, completed;
        """, (task_id,))

        result = cursor.fetchone()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        connection.commit()

        return {
            "message": "Daily task marked as completed!",
            "task_id": str(result[0]),
            "patient_id": str(result[1]),
            "task_type": result[2],
            "task_description": result[3],
            "scheduled_time": str(result[4]) if result[4] else None,
            "completed": result[5]
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