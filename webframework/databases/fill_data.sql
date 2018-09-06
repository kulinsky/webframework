BEGIN TRANSACTION;
CREATE TABLE "users" (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	`last_name`	TEXT NOT NULL,
	`first_name`	TEXT NOT NULL,
	`middle_name`	TEXT,
	`phone`	TEXT,
	`email`	TEXT,
	`city_id`	INTEGER,
	`deleted`	INTEGER DEFAULT 0,
	FOREIGN KEY(`city_id`) REFERENCES `cities`(`id`)
);
INSERT INTO `users` (id,last_name,first_name,middle_name,phone,email,city_id,deleted) VALUES (7,'Кулинский','Антон',NULL,'(555) 555-55-55','test@email.com',1,0),
 (8,'Иванов','Иван','Иванович',NULL,NULL,5,1),
 (9,'Петров','Вектор',NULL,NULL,NULL,7,1),
 (10,'Иванов','Иван',NULL,NULL,NULL,1,0),
 (11,'Иванов','Иван',NULL,NULL,NULL,1,0),
 (12,'Иванов','Иван',NULL,NULL,NULL,1,0),
 (13,'Иванов','Иван',NULL,NULL,NULL,1,0),
 (14,'Петров','Федр',NULL,NULL,NULL,4,0),
 (15,'Петров','Федр',NULL,NULL,NULL,4,0),
 (16,'Петров','Федр',NULL,NULL,NULL,4,0),
 (17,'Тарасов','Михаил',NULL,NULL,NULL,5,0);
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
	`timestamp`	NUMERIC,
	FOREIGN KEY(`user_id`) REFERENCES `users`(`id`)
);
INSERT INTO `comments` (id,text,user_id,deleted,timestamp) VALUES (9,'Тестовый комментарий',7,0,'2018-09-06 01:20:33.197792'),
 (10,'Комментарий от Ивана',8,1,'2018-09-06 01:24:45.603648'),
 (11,'Комментарий от Вектора',9,1,'2018-09-06 01:58:16.117824'),
 (12,'Комментарий от Ивана из Краснодара',10,0,'2018-09-06 02:00:55.883876'),
 (13,'Комментарий от Ивана из Краснодара',11,0,'2018-09-06 02:01:04.011210'),
 (14,'Комментарий от Ивана из Краснодара',12,0,'2018-09-06 02:01:11.105568'),
 (15,'Комментарий от Ивана из Краснодара',13,0,'2018-09-06 02:01:18.679293'),
 (16,'Комментарий от Федора из Ростова',14,0,'2018-09-06 02:02:19.716404'),
 (17,'Комментарий от Федора из Ростова',15,0,'2018-09-06 02:02:32.732318'),
 (18,'Комментарий от Федора из Ростова',16,0,'2018-09-06 02:02:43.266059'),
 (19,'Комментарий от миши',17,0,'2018-09-06 07:24:24.035500');
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
