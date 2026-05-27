DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS alert;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE stock (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  symbol STRING NOT NULL,
  link STRING NOT NULL,
  priority INT NOT NULL,
  user_id INTEGER NOT NULL,
  percentage_up INT,
  percentage_down INT,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE alert (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  stock_id INTEGER NOT NULL,
  percentage_up INT,
  percentage_down INT,
  FOREIGN KEY (stock_id) REFERENCES stock (id)
)
