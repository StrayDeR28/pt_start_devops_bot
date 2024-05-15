DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'db_pt') THEN
        CREATE DATABASE db_pt;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = 'repl_user') THEN
        CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD 'Qq12345';
    END IF;
END $$;

ALTER USER postgres WITH PASSWORD 'Qq12345';

\c db_pt;

SELECT pg_create_physical_replication_slot('replication_slot');

GRANT pg_read_all_data TO repl_user;
GRANT pg_write_all_data TO repl_user;
GRANT ALL PRIVILEGES ON DATABASE db_pt TO repl_user;
GRANT ALL PRIVILEGES ON DATABASE db_pt TO postgres;

CREATE TABLE IF NOT EXISTS Emails (
    id serial PRIMARY KEY,
    email VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS PhoneNumbers (
    id serial PRIMARY KEY,
    PhoneNumber VARCHAR(255)
);