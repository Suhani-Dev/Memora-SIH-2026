CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- =========================
-- 1. ACCOUNTS
-- =========================

CREATE TABLE accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT role_check
        CHECK (role IN ('patient', 'caregiver'))
);


-- =========================
-- 2. PATIENTS
-- =========================

CREATE TABLE patients (
    patient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    preferred_language VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    difficulty_level INTEGER DEFAULT 1,
    age_group VARCHAR(20),
    account_id UUID UNIQUE REFERENCES accounts(account_id),

    CONSTRAINT patient_difficulty_check
        CHECK (difficulty_level BETWEEN 1 AND 3)
);


-- =========================
-- 3. GAMES
-- =========================

CREATE TABLE games (
    game_id SERIAL PRIMARY KEY,
    game_name VARCHAR(100) NOT NULL,
    cognitive_area VARCHAR(50) NOT NULL,
    description TEXT,
    difficulty_levels INTEGER DEFAULT 3,
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT difficulty_levels_check
        CHECK (difficulty_levels BETWEEN 1 AND 3)
);


-- =========================
-- 4. GAME SESSIONS
-- =========================

CREATE TABLE game_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL
        REFERENCES patients(patient_id),
    game_id INTEGER NOT NULL
        REFERENCES games(game_id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    difficulty_level INTEGER NOT NULL,

    CONSTRAINT session_difficulty_check
        CHECK (difficulty_level BETWEEN 1 AND 3)
);


-- =========================
-- 5. GAME RESULTS
-- =========================

CREATE TABLE game_results (
    result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL
        REFERENCES game_sessions(session_id),
    score INTEGER,
    accuracy DECIMAL(5,2),
    correct_answers INTEGER,
    total_questions INTEGER,
    mistakes INTEGER,
    response_time_avg DECIMAL(8,2),
    completion_time DECIMAL(8,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT accuracy_check
        CHECK (accuracy BETWEEN 0 AND 100),

    CONSTRAINT unique_session_result
        UNIQUE (session_id)
);


-- =========================
-- 6. AI ANALYSIS
-- =========================

CREATE TABLE ai_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL
        REFERENCES patients(patient_id),
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    memory_score DECIMAL(5,2),
    attention_score DECIMAL(5,2),
    pattern_score DECIMAL(5,2),
    performance_trend VARCHAR(30),
    recommended_difficulty INTEGER,
    summary TEXT,

    CONSTRAINT recommended_difficulty_check
        CHECK (recommended_difficulty BETWEEN 1 AND 3),

    CONSTRAINT ai_scores_check
        CHECK (
            memory_score BETWEEN 0 AND 100
            AND attention_score BETWEEN 0 AND 100
            AND pattern_score BETWEEN 0 AND 100
        )
);


-- =========================
-- 7. CAREGIVERS
-- =========================

CREATE TABLE caregivers (
    caregiver_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID UNIQUE NOT NULL
        REFERENCES accounts(account_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================
-- 8. CAREGIVER - PATIENT
-- =========================

CREATE TABLE caregiver_patients (
    caregiver_id UUID NOT NULL
        REFERENCES caregivers(caregiver_id)
        ON DELETE CASCADE,

    patient_id UUID NOT NULL
        REFERENCES patients(patient_id)
        ON DELETE CASCADE,

    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (caregiver_id, patient_id)
);


-- =========================
-- 9. DAILY TASKS
-- =========================

CREATE TABLE daily_tasks (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    patient_id UUID NOT NULL
        REFERENCES patients(patient_id)
        ON DELETE CASCADE,

    task_type VARCHAR(50) NOT NULL,
    task_description TEXT NOT NULL,
    scheduled_time TIME,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================
-- 10. NOTIFICATIONS
-- =========================

CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    recipient_account_id UUID NOT NULL
        REFERENCES accounts(account_id)
        ON DELETE CASCADE,

    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);