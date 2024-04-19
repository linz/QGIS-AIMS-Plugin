#!/bin/sh

echo >&2 ""
echo >&2 "######################"
echo >&2 "# Running QGIS tests #"
echo >&2 "######################"
echo >&2 ""

# docker exec --privileged qgis /bin/sh -c "cd / && ls -l"
# docker exec --privileged qgis /bin/sh -c "cd /tests_directory && ls -l -R"

docker exec --privileged qgis /bin/sh chmod +x /tests_directory/$PLUGIN_NAME/test/run_tests.sh
docker exec --privileged -w /tests_directory/$PLUGIN_NAME qgis /bin/sh /tests_directory/$PLUGIN_NAME/test/run_tests.sh