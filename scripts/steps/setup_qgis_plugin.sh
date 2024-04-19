#!/bin/sh

echo >&2 ""
echo >&2 "##########################"
echo >&2 "# Setting up QGIS plugin #"
echo >&2 "##########################"
echo >&2 ""

PROFILE_DIR=/root/.local/share/QGIS/QGIS3/profiles/default

# docker exec --privileged qgis /bin/sh -c "cd / && ls -l"
# docker exec --privileged qgis /bin/sh -c "cd /tests_directory && ls -l -R"

docker exec --privileged qgis mkdir -p $PROFILE_DIR/aims
docker exec --privileged qgis cp /tests_directory/QGIS-AIMS-Plugin/test/aims_test_config.ini $PROFILE_DIR/aims/aimsConfig.ini

docker exec --privileged qgis /bin/sh -c "cd /$PROFILE_DIR && ls -l -R"

docker exec --privileged qgis bash -f /usr/bin/qgis_setup.sh "QGIS-AIMS-Plugin"
