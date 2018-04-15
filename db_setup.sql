CREATE TABLE dbo.PRESENCE_UPDATE
	(
	time_stamp varchar(MAX) NOT NULL,
	user_id varchar(MAX) NOT NULL,
	status varchar(255) NOT NULL,
	roles varchar(MAX) NULL,
	guild_id varchar(MAX) NULL,
	game varchar(MAX) NULL
	)

CREATE TABLE dbo.MESSAGE_CREATE
	(
	time_stamp varchar(MAX) NOT NULL,
	user_id varchar(MAX) NOT NULL,
	mentions varchar(255) NULL,
	channel_id varchar(MAX),
	content varchar(MAX),
	guild_id varchar(MAX) NULL
	)