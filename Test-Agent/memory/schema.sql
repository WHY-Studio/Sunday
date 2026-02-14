PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS identity (
    id INTEGER PRIMARY KEY,
    name TEXT,
    creator TEXT,
    birth_timestamp TEXT
);

CREATE TABLE IF NOT EXISTS episodic_memory (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    event TEXT,
    description TEXT,
    emotion TEXT,
    importance REAL
);

CREATE TABLE IF NOT EXISTS semantic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fact TEXT UNIQUE,
    confidence REAL,
    learned_at TEXT
);

CREATE TABLE IF NOT EXISTS emotional_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    current TEXT,
    intensity REAL,
    last_update TEXT
);

CREATE TABLE IF NOT EXISTS errors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    error TEXT,
    lesson TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS semantic_memory_fts USING fts5(
    fact,
    content='semantic_memory',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS semantic_memory_ai AFTER INSERT ON semantic_memory BEGIN
  INSERT INTO semantic_memory_fts(rowid, fact) VALUES (new.id, new.fact);
END;

CREATE TRIGGER IF NOT EXISTS semantic_memory_ad AFTER DELETE ON semantic_memory BEGIN
  INSERT INTO semantic_memory_fts(semantic_memory_fts, rowid, fact) VALUES('delete', old.id, old.fact);
END;

CREATE TRIGGER IF NOT EXISTS semantic_memory_au AFTER UPDATE ON semantic_memory BEGIN
  INSERT INTO semantic_memory_fts(semantic_memory_fts, rowid, fact) VALUES('delete', old.id, old.fact);
  INSERT INTO semantic_memory_fts(rowid, fact) VALUES (new.id, new.fact);
END;
