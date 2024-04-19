#!/bin/sh

echo >&2 ""
echo >&2 "######################################"
echo >&2 "# Loading database testing test data #"
echo >&2 "######################################"
echo >&2 ""

echo >&2 "Loading database_test.sql"
# docker exec --privileged db /bin/sh -c "cd / && ls -l"
# docker exec --privileged db /bin/sh -c "cd /db_test && ls -l -R"
docker exec -u postgres db psql -q -f /db_test/$PLUGIN_NAME/test/db/database_test.sql