#!/bin/bash

fmt=plain
db=linz_db

#extract functions
#psql -d $db -c 'select roads_lds.populate_lds_roads()'
#psql -d $db -c 'select roads_lds.populate_old_lds_roads()'
psql -d $db -c 'select aims_lds.populate_lds()'
psql -d $db -c 'select aims_lds.populate_old_lds()'

#dump & copy
pg_dump --data-only --format $fmt --schema aims_lol $db | gzip > /mnt/aims/Street\ Addresses/aims_lol.pg_dump.gz
pg_dump --data-only --format $fmt --schema roads_lol $db | gzip > /mnt/aims/Roads/roads_lol.pg_dump.gz

