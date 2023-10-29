CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    password TEXT CHECK(LENGTH(password) >= 255),
    created_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', '+6 hours')) --GMT + 6
);


CREATE TABLE friends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    friend_one_id INTEGER REFERENCES users(user_id),
    friend_two_id INTEGER REFERENCES users(user_id),
    CHECK (friend_one_id != friend_two_id)
);


CREATE TABLE playlist (
    playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(user_id),
    playlist_name VARCHAR(100),
    is_public INTEGER CHECK (is_public IN (0, 1)),
    created_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', '+6 hours'))
);


CREATE TABLE artist(
    artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist_name VARCHAR(100)
);


CREATE TABLE genre(
    genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
    genre_name VARCHAR(100)
);

CREATE TABLE music(
    music_id INTEGER PRIMARY KEY AUTOINCREMENT,
    music_name VARCHAR(100),
    cover_img VARCHAR(255), --URL of the cover image.
    created_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', '+6 hours'))
);

CREATE TABLE music_artist(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    music_id INTEGER REFERENCES music(music_id),
    artist_id INTEGER REFERENCES artist(artist_id)
);


CREATE TABLE music_genre(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    music_id INTEGER REFERENCES music(music_id),
    genre_id INTEGER REFERENCES genre(genre_id)
);


CREATE TABLE music_fingerprint(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    music_id INTEGER REFERENCES music(music_id),
    music_hash INTEGER,
    music_hash_with_previous_sec INTEGER,
    curr_sec INTEGER,
    created_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', '+6 hours')) 
);


CREATE TABLE playlist_music (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id INTEGER REFERENCES playlist(playlist_id),
    song_id INTEGER REFERENCES song(song_id),
    created_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', '+6 hours'))
);






------ annotation schema 

CREATE TABLE annotation(
    ant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    annotation_text TEXT,
    user_id INTEGER REFERENCES users(user_id),
    created_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', '+6 hours'))
);


CREATE TABLE music_annotation(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ant_id INTEGER REFERENCES annotation(ant_id),
    music_id INTEGER REFERENCES music(music_id)
);


CREATE TABLE lyrics_annotation(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ant_id INTEGER REFERENCES annotation(ant_id),
    music_id INTEGER REFERENCES music(music_id),
    line_idx INTEGER
);

CREATE TABLE discovered_list(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(user_id), 
    music_id INTEGER REFERENCES music(music_id),
    discovered_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', '+6 hours'))
);


CREATE TABLE location_charts(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    music_id INTEGER REFERENCES music(music_id),
    discovering_country TEXT,
    no_of_discovery INTEGER,
    discovered_at DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', '+6 hours'))
);