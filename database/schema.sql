PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS videos;
DROP TABLE IF EXISTS radio_messages;
DROP TABLE IF EXISTS telemetry;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS stages;
DROP TABLE IF EXISTS crews;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
        CHECK (role IN ('guest', 'user', 'marshal', 'admin')),
    is_blocked INTEGER NOT NULL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_users_email ON users(email);

CREATE TABLE crews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number INTEGER UNIQUE NOT NULL,
    pilot_name TEXT NOT NULL,
    navigator_name TEXT NOT NULL,
    car_model TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_crews_number ON crews(number);

CREATE TABLE stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL,
    location TEXT,
    latitude REAL,
    longitude REAL,
    distance_km REAL,
    weather_temp INTEGER,
    weather_desc TEXT,
    wind_speed INTEGER,
    surface_type TEXT
        CHECK (surface_type IN ('dry', 'wet', 'snow', 'gravel', 'asphalt')),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_stages_date ON stages(date);

CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage_id INTEGER NOT NULL REFERENCES stages(id) ON DELETE CASCADE,
    crew_id INTEGER NOT NULL REFERENCES crews(id) ON DELETE CASCADE,
    time_seconds INTEGER NOT NULL,
    penalty_seconds INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stage_id, crew_id)
);
CREATE INDEX idx_results_stage_crew ON results(stage_id, crew_id);

CREATE TABLE telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage_id INTEGER NOT NULL REFERENCES stages(id) ON DELETE CASCADE,
    crew_id INTEGER NOT NULL REFERENCES crews(id) ON DELETE CASCADE,
    timestamp TEXT NOT NULL,
    speed_kmh INTEGER,
    rpm INTEGER,
    gear TEXT,
    position_desc TEXT
);
CREATE INDEX idx_telemetry_stage ON telemetry(stage_id);

CREATE TABLE radio_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage_id INTEGER NOT NULL REFERENCES stages(id) ON DELETE CASCADE,
    crew_id INTEGER NOT NULL REFERENCES crews(id) ON DELETE CASCADE,
    message_text TEXT NOT NULL,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_radio_stage ON radio_messages(stage_id);

CREATE TABLE videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stage_id INTEGER NOT NULL REFERENCES stages(id) ON DELETE CASCADE,
    crew_id INTEGER NOT NULL REFERENCES crews(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    video_url TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_videos_stage ON videos(stage_id);