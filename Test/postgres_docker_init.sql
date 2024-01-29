USE aims_ci_test;

CREATE SCHEMA aims;

CREATE TABLE aims.aims_test_table(id int, name varchar(32));

INSERT INTO aims.aims_test_table VALUES (
    1, 'aims_test_data'
);

SELECT * FROM aims.aims_test_table;