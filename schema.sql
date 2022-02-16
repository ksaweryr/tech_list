CREATE TABLE app_user(
  uid INTEGER NOT NULL UNIQUE PRIMARY KEY,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  admin INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE technology(
  tid INTEGER NOT NULL UNIQUE PRIMARY KEY,
  uid INTEGER NOT NULL,
  name TEXT UNIQUE,
  description TEXT NOT NULL,
  link TEXT NOT NULL,
  creation_date TEXT NOT NULL DEFAULT '',
  update_date TEXT DEFAULT NULL,
  likes INTEGER NOT NULL DEFAULT 0,

  FOREIGN KEY(uid) REFERENCES app_user(uid) ON DELETE SET NULL
);

-- many to many relation between `app_user` and `technology`
CREATE TABLE liked(
  uid INTEGER NOT NULL,
  tid INTEGER NOT NULL,

  UNIQUE (uid, tid),
  FOREIGN KEY(uid) REFERENCES app_user(uid) ON DELETE CASCADE,
  FOREIGN KEY(tid) REFERENCES technology(tid) ON DELETE CASCADE
);

-- Set the creation date just after a post is created
-- (in SQLite, unlike in PostgreSQL, it's impossible to set default value to function call so this trigger is needed)
CREATE TRIGGER set_creation_date
  AFTER INSERT ON technology
BEGIN
  UPDATE technology SET creation_date = datetime() WHERE tid = NEW.tid;
END;

-- Set the update date after a post is updated
CREATE TRIGGER set_update_date
  AFTER UPDATE ON technology
BEGIN
  UPDATE technology SET update_date = datetime() WHERE tid = NEW.tid;
END;

-- Increment like counter in post after a row is inserted into `liked` (ie. user likes a post)
CREATE TRIGGER add_like
  AFTER INSERT ON liked
BEGIN
  UPDATE technology SET likes = likes + 1 WHERE tid = NEW.tid;
END;

-- Decrement like counter in post after a row is deleted from `liked` (ie. user deletes a like on a post)
CREATE TRIGGER remove_like
  AFTER DELETE ON liked
BEGIN
  UPDATE technology SET likes = likes - 1 WHERE tid = OLD.tid;
END;
