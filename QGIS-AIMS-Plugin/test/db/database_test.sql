CREATE DATABASE aims_ci_test
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;
    

\connect aims_ci_test;

CREATE SCHEMA aims;

CREATE TABLE aims_test_table(id int, name varchar(32));

INSERT INTO aims_test_table VALUES (1, 'aims_test_data');

SELECT * FROM aims_test_table;