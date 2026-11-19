-- Run in pgAdmin connected to the postgres maintenance database.
-- Create the user first using the same password configured in .env.
-- For local development only; choose a strong password for real deployments.
CREATE USER storebridge WITH PASSWORD 'CHANGE_ME';

-- pgAdmin Query Tool can execute each CREATE DATABASE independently.
CREATE DATABASE walk_liberty OWNER storebridge;
CREATE DATABASE walk_ogf OWNER storebridge;
CREATE DATABASE walk_pettah OWNER storebridge;
CREATE DATABASE storebridge_auth OWNER storebridge;
