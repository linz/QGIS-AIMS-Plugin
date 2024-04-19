#!/bin/sh

echo >&2 ""
echo >&2 "##########################"
echo >&2 "# Setting up QGIS plugin #"
echo >&2 "##########################"
echo >&2 ""

PROFILE_DIR=/root/.local/share/QGIS/QGIS3/profiles/default

docker exec --privileged qgis /bin/sh -c "cd / && ls -l"
docker exec --privileged qgis /bin/sh -c "cd /tests_directory && ls -l -R"

docker exec qgis mkdir -p $PROFILE_DIR/QGIS-AIMS-Plugin
docker exec qgis cp /tests_directory/QGIS-AIMS-Plugin/test/aims_test_config.ini $PROFILE_DIR/QGIS-AIMS-Plugin/aims_test_config.ini
docker exec --privileged qgis bash -f /usr/bin/qgis_setup.sh "QGIS-AIMS-Plugin"
