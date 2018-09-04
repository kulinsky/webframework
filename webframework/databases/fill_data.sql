BEGIN TRANSACTION;
CREATE TABLE "users" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`last_name`	TEXT NOT NULL,
	`first_name`	TEXT NOT NULL,
	`midle_name`	TEXT,
	`phone`	TEXT,
	`email`	TEXT,
	`city_id`	INTEGER,
	`deleted`	INTEGER DEFAULT 0,
	FOREIGN KEY(`city_id`) REFERENCES `cities`(`id`)
);
CREATE TABLE "regions" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`name`	TEXT NOT NULL,
	`deleted`	INTEGER DEFAULT 0
);
INSERT INTO `regions` (id,name,deleted) VALUES (1,'Краснодарский край',0),
 (2,'Ростовская область',0),
 (3,'Ставропольский край',0);
CREATE TABLE "comments" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`text`	TEXT NOT NULL,
	`user_id`	INTEGER,
	`deleted`	INTEGER DEFAULT 0,
	FOREIGN KEY(`user_id`) REFERENCES `users`(`id`)
);
CREATE TABLE "cities" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`name`	TEXT NOT NULL,
	`region_id`	INTEGER,
	`deleted`	INTEGER DEFAULT 0,
	FOREIGN KEY(`region_id`) REFERENCES `regions`(`id`)
);
INSERT INTO `cities` (id,name,region_id,deleted) VALUES (1,'Краснодар',1,0),
 (2,'Кропоткин',1,0),
 (3,'Славянск',1,0),
 (4,'Ростов',2,0),
 (5,'Шахты',2,0),
 (6,'Батайск',2,0),
 (7,'Ставрополь',3,0),
 (8,'Пятигорск',3,0),
 (9,'Кисловодск',3,0);
COMMIT;
