-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS task;

CREATE TABLE task (
  body TEXT NOT NULL,
  selected INTEGER DEFAULT 0,
  finished INTEGER DEFAULT 0);
