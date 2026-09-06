"""
Database Schema Definition for GoalMate
Includes tables for Goals, Milestones, Tasks, Progress Logs, User Memories, and Conversations.
"""

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'General',
    target_date TEXT,
    priority TEXT DEFAULT 'Medium',
    daily_time_minutes INTEGER DEFAULT 60,
    preferred_schedule TEXT DEFAULT 'flexible',
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'paused', 'abandoned')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    order_index INTEGER DEFAULT 1,
    target_date TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed')),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER NOT NULL REFERENCES goals(id) ON DELETE CASCADE,
    milestone_id INTEGER REFERENCES milestones(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    due_date TEXT NOT NULL,
    estimated_minutes INTEGER DEFAULT 45,
    priority TEXT DEFAULT 'Medium' CHECK(priority IN ('Low', 'Medium', 'High', 'Critical')),
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'rescheduled', 'missed')),
    completed_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS progress_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_id INTEGER REFERENCES goals(id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    tasks_completed INTEGER DEFAULT 0,
    total_minutes_spent INTEGER DEFAULT 0,
    streak_count INTEGER DEFAULT 0,
    notes TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    intent TEXT,
    tool_calls TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_goal ON tasks(goal_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
CREATE INDEX IF NOT EXISTS idx_milestones_goal ON milestones(goal_id);
CREATE INDEX IF NOT EXISTS idx_progress_date ON progress_logs(date);
"""
