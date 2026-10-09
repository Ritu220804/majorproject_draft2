CREATE TABLE IF NOT EXISTS detection_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_uuid TEXT NOT NULL UNIQUE,
    source_type TEXT NOT NULL,
    source_filename TEXT,
    session_id TEXT,
    detected_at DATETIME NOT NULL,
    verification_status TEXT NOT NULL DEFAULT 'unverified',
    processing_time_ms INTEGER,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_detection_event_source_type ON detection_event(source_type);
CREATE INDEX IF NOT EXISTS idx_detection_event_detected_at ON detection_event(detected_at);
CREATE INDEX IF NOT EXISTS idx_detection_event_verification_status ON detection_event(verification_status);

CREATE TABLE IF NOT EXISTS detection_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    class_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    x1 REAL,
    y1 REAL,
    x2 REAL,
    y2 REAL,
    frame_index INTEGER,
    timestamp_seconds REAL,
    FOREIGN KEY (event_id) REFERENCES detection_event(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_detection_detail_event_id ON detection_detail(event_id);
CREATE INDEX IF NOT EXISTS idx_detection_detail_class_name ON detection_detail(class_name);

CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES detection_event(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_evidence_event_id ON evidence(event_id);
CREATE INDEX IF NOT EXISTS idx_evidence_file_type ON evidence(file_type);
