
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  username        varchar(50) PRIMARY KEY not null, 
  password        varchar(50) not null, -- Must be 8 characters --
  name            varchar(50) not null
);

DROP TABLE IF EXISTS products;
CREATE TABLE products (
  prodId      INTEGER PRIMARY KEY not null,
  name        varchar(50) not null,
  category    varchar(50) not null,
  price       float(10) not null, -- Check to see if argument is bits or digits -- 
  quantity    INTEGER not null,
  FOREIGN KEY (category) REFERENCES categories(category)
);

DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
  orderID     INTEGER PRIMARY KEY AUTOINCREMENT not null,
  username    varchar(50) not null,
  products    varchar(50) not null,
  FOREIGN KEY (username) REFERENCES users(username)
);

DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
  category    varchar(50) PRIMARY KEY not null
);

PRAGMA foreign_keys=on;

-- users
INSERT INTO users VALUES ('tester', 'password', 'Max Eichholz');
INSERT INTO users VALUES ('testuser', 'testpass', 'Grading User');

-- categories
INSERT INTO categories VALUES ('Fruit');
INSERT INTO categories VALUES ('Vegetable');
INSERT INTO categories VALUES ('Candy');

-- products
INSERT INTO products VALUES (1, 'Apple', 'Fruit', 1.30, 5);
INSERT INTO products VALUES (2, 'Orange', 'Fruit', 1.40, 5);
INSERT INTO products VALUES (10, 'Grapes', 'Fruit', 1.40, 5);

INSERT INTO products VALUES (3, 'Carrot', 'Vegetable', 1.25, 5);
INSERT INTO products VALUES (4, 'Onion', 'Vegetable', 1.15, 5);
INSERT INTO products VALUES (5, 'Radish', 'Vegetable', 1.10, 5);
INSERT INTO products VALUES (6, 'Pepper', 'Vegetable', 1.25, 5);

INSERT INTO products VALUES (7, 'Licorice', 'Candy', 2.25, 5);
INSERT INTO products VALUES (8, 'Caramel', 'Candy', 1.75, 5);
INSERT INTO products VALUES (9, 'Mints', 'Candy', 1.20, 5);

INSERT INTO orders VALUES (1, 'tester', '1,1,4');
-- SELECT * FROM users;
-- SELECT * FROM products;


