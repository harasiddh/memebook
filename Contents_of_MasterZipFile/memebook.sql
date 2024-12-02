CREATE TABLE "user" (
	"id"	INTEGER,
	"email"	TEXT UNIQUE,
	"first_name"	TEXT,
	"last_name"	TEXT,
	"username"	TEXT UNIQUE,
	"password"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "meme" (
	"id"	INTEGER,
	"title"	TEXT,
	"caption"	TEXT,
	"creator_username"	TEXT,
	"extension"	TEXT,
	"likes"	INTEGER,
	FOREIGN KEY("creator_username") REFERENCES "user"("username"),
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "followers" (
	"user_username"	TEXT,
	"follower_username"	TEXT,
	PRIMARY KEY("user_username","follower_username"),
	FOREIGN KEY("user_username") REFERENCES "user"("username"),
	FOREIGN KEY("follower_username") REFERENCES "user"("username")
);

CREATE TABLE "likes" (
	"user_id"	INTEGER,
	"meme_id"	INTEGER,
	PRIMARY KEY("user_id","meme_id"),
	FOREIGN KEY("meme_id") REFERENCES "meme"("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);

CREATE TABLE "meme_creators" (
	"user_id"	INTEGER,
	"meme_id"	INTEGER,
	FOREIGN KEY("user_id") REFERENCES "user"("id"),
	PRIMARY KEY("user_id","meme_id"),
	FOREIGN KEY("meme_id") REFERENCES "meme"("id")
)