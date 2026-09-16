"""SQLite state: runs, win rates, cache, memory."""
import hashlib, os, sqlite3, time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DB_PATH = Path(os.environ.get("FORGE_DB", str(Path.home() / ".forge" / "state.db")))


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(DB_PATH))
    con.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL, model TEXT, prompt TEXT, strategy TEXT,
            response TEXT, score INTEGER, elapsed REAL
        )""")
    con.execute("""
        CREATE TABLE IF NOT EXISTS strategy_stats (
            model TEXT, strategy TEXT,
            wins INTEGER DEFAULT 0,
            plays INTEGER DEFAULT 0,
            best_score INTEGER DEFAULT 0,
            PRIMARY KEY (model, strategy)
        )""")
    con.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            prompt_hash TEXT, model TEXT, response TEXT, ts REAL,
            PRIMARY KEY (prompt_hash, model)
        )""")
    con.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT, role TEXT, content TEXT, ts REAL
        )""")
    return con


def record_run(model: str, prompt: str, strategy: str,
               response: str, score: int, elapsed: float) -> None:
    con = _connect()
    con.execute(
        "INSERT INTO runs (ts, model, prompt, strategy, response, score, elapsed) "
        "VALUES (?,?,?,?,?,?,?)",
        (time.time(), model, prompt, strategy, response, score, elapsed))
    con.execute("""
        INSERT INTO strategy_stats (model, strategy, wins, plays, best_score)
        VALUES (?,?,?,?,?)
        ON CONFLICT(model, strategy) DO UPDATE SET
            plays = plays + 1,
            wins = wins + (CASE WHEN ? >= 50 THEN 1 ELSE 0 END),
            best_score = MAX(best_score, ?)
    """, (model, strategy, 1 if score >= 50 else 0, 1, score, score, score))
    con.commit()
    con.close()


def strategy_weights(model: str) -> Dict[str, Tuple[float, int]]:
    con = _connect()
    rows = con.execute(
        "SELECT strategy, wins, plays, best_score FROM strategy_stats WHERE model=?",
        (model,)).fetchall()
    con.close()
    return {r[0]: (r[1] / max(1, r[2]), r[3]) for r in rows}


def cache_get(prompt: str, model: str) -> Optional[str]:
    h = hashlib.sha256(prompt.encode()).hexdigest()
    con = _connect()
    row = con.execute(
        "SELECT response FROM cache WHERE prompt_hash=? AND model=?",
        (h, model)).fetchone()
    con.close()
    return row[0] if row else None


def cache_put(prompt: str, model: str, response: str) -> None:
    h = hashlib.sha256(prompt.encode()).hexdigest()
    con = _connect()
    con.execute(
        "INSERT OR REPLACE INTO cache (prompt_hash, model, response, ts) "
        "VALUES (?,?,?,?)",
        (h, model, response, time.time()))
    con.commit()
    con.close()


def memory_append(session_id: str, role: str, content: str) -> None:
    con = _connect()
    con.execute(
        "INSERT INTO memory (session_id, role, content, ts) VALUES (?,?,?,?)",
        (session_id, role, content, time.time()))
    con.commit()
    con.close()


def memory_read(session_id: str, limit: int = 20) -> List[Dict[str, str]]:
    con = _connect()
    rows = con.execute(
        "SELECT role, content FROM memory WHERE session_id=? "
        "ORDER BY id DESC LIMIT ?", (session_id, limit)).fetchall()
    con.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


def stats_table() -> List[Tuple]:
    con = _connect()
    rows = con.execute(
        "SELECT model, strategy, wins, plays, best_score "
        "FROM strategy_stats ORDER BY model, wins DESC").fetchall()
    con.close()
    return rows


def history(n: int = 20) -> List[Tuple]:
    con = _connect()
    rows = con.execute(
        "SELECT ts, model, strategy, score, substr(prompt,1,60) "
        "FROM runs ORDER BY id DESC LIMIT ?", (n,)).fetchall()
    con.close()
    return rows


def reset() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
