#!/bin/sh

echo >&2 ""
echo >&2 "######################################"
echo >&2 "# Loading database testing test data #"
echo >&2 "######################################"
echo >&2 ""

echo >&2 "Loading database_test.sql"
# docker exec --privileged simple_db /bin/sh -c "cd / && ls -l"
# docker exec --privileged simple_db /bin/sh -c "cd /simple_db_test && ls -l -R"
# docker exec -u postgres simple_db psql -q -c "CREATE DATABASE simple_db;"
# docker exec -u postgres simple_db psql -q -c "\c simple_db"
# docker exec -u postgres simple_db psql -q -c "CREATE SCHEMA simple_schema;"
docker exec -u postgres db psql -q -f /test/db/database_test.sql