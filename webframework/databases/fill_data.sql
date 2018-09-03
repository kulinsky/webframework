BEGIN TRANSACTION;
CREATE TABLE "users" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`last_name`	TEXT NOT NULL,
	`first_name`	TEXT NOT NULL,
	`midle_name`	TEXT,
	`phone`	TEXT,
	`email`	TEXT,
	`city_id`	INTEGER,
	FOREIGN KEY(`city_id`) REFERENCES cities(id)
);
CREATE TABLE `regions` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`name`	TEXT NOT NULL
);
INSERT INTO `regions` (id,name) VALUES (1,'Краснодарский край'),
 (2,'Ростовская область'),
 (3,'Ставропольский край');
CREATE TABLE `comments` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`text`	TEXT NOT NULL,
	`user_id`	INTEGER,
	FOREIGN KEY(`user_id`) REFERENCES users(id)
);
CREATE TABLE `cities` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`name`	TEXT NOT NULL,
	`region_id`	INTEGER,
	FOREIGN KEY(`region_id`) REFERENCES regions(id)
);
INSERT INTO `cities` (id,name,region_id) VALUES (1,'Краснодар',1),
 (2,'Кропоткин',1),
 (3,'Славянск',1),
 (4,'Ростов',2),
 (5,'Шахты',2),
 (6,'Батайск',2),
 (7,'Ставрополь',3),
 (8,'Пятигорск',3),
 (9,'Кисловодск',3);
COMMIT;
