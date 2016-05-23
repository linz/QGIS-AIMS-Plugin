-- ################################################################################
-- #
-- # Copyright 2015 Crown copyright (c)
-- # Land Information New Zealand and the New Zealand Government.
-- # All rights reserved
-- #
-- # This program is released under the terms of the 3 clause BSD license. See the 
-- # LICENSE file for more information.
-- #
-- ################################################################################


--select admin_bdys_import.import_admin_boundary('meshblock')
create or replace function admin_bdys_import.import_admin_boundary(name varchar) 
returns void as $$
declare
	primary_schema text := 'admin_bdys';
	import_schema text := 'admin_bdys_import';
	import_prefix text := 'i_';
	map_prefix text := 'm_';
	snap_prefix text := 's_';
	--copy_prefix text := 'c_';
	qstr text;
	perm_table text := primary_schema || '.' || name;
	--import_table text := import_schema || '.' || import_prefix || name;
	import_table text := import_schema || '.' || 'temp_' || name;
	map_table text := import_schema || '.' || map_prefix || name; --column mapped import table
	snap_table text := import_schema || '.' || snap_prefix || name; --snapshot of perm table
	--copy_table text := import_schema || '.' || copy_prefix || name;
	
	--first entry must be the pk column
	mb  text[][] := array[['mb_code','code'],['wkt','geom']];
	mbc text[][] := array[['mb_code','code'],['wkt','geom'],['previous','new']];
	nzl text[][] := array[['nzl_code','code'],['shape','geom']];
	ta  text[][] := array[['ta_code','code'],['wkt','geom']];
	selection text[][];
	rep text[];
	--result text;
	
	-- array_position function doesn't exist in this version of postgresql
	-- map_index int := array_position(map_name,name::text);
	
begin
	-- 1. create a new table to map imports to final table format 
	qstr := 'create table ' || map_table || ' as select * from ' || import_table;
	raise notice '1 %',qstr;
	execute qstr;-- into result;
	
	case name
		when 'meshblock' then
			selection := mb;
		when 'meshblock_concordance' then
			selection := mbc;
		when 'nz_localities' then
			selection := nzl;
		when 'territorial_authority' then
			selection := ta;
	end case;

	foreach rep slice 1 in array selection[1:array_upper(selection,1)]
	loop 
		qstr := 'alter table ' || map_table || ' rename column ' || rep[1] || ' to ' || rep[2];
		raise notice '2 %',qstr;
		execute qstr;-- into result;
	end loop;

	qstr := 'alter table ' || map_table || ' add primary key (' || selection[1][2] || ')';
	raise notice '4 %',qstr;	
	execute qstr;-- into result;


	--2. apply differences to perm table
	--<temp>
	qstr := 'create table ' || snap_table || ' as select * from ' || perm_table;
	raise notice '5 %',qstr;	
	execute qstr;-- into result;

	qstr := 'alter table ' || snap_table || ' add primary key (' || selection[1][2] || ')';
	raise notice '6 %',qstr;	
	execute qstr;-- into result;
	--</temp>
	qstr := 'select table_version.ver_apply_table_differences(' || quote_literal(snap_table) || ',' || quote_literal(map_table) || ',' || quote_literal(selection[1][2]) || ')';
	raise notice '7 %',qstr;	
	execute qstr;-- into result;
	
	-- ALTERNATIVE/ORIGINAL METHOD
	
-- 	-- 2. copy perm table to local schema
-- 	qstr := 'create temporary table' || snap_table || ' as select * from ' || perm_table;
-- 	qstr := 'alter table ' || snap_table || ' add primary key ( ' || selection[1][2] || ')';
-- 
-- 
-- 	-- 3. revision snap table
-- 	qstr := "select table_version.ver_enable_versioning('" || import_schema || "','" || snap_prefix || name "')";
-- 	qstr := "select table_version.ver_create_revision('first revision for " || snap_table || "')";
-- 
-- 	-- 4. populate the mapped table with the imported data
-- 	qstr := 'truncate ' || snap_table;
-- 	qstr := 'insert into ' || snap_table || ' select * from ' || map_table;
-- 
-- 	-- 5. complete revision
-- 	qstr := "select table_version.ver_complete_revision('second revision for " || snap_table || "')";
-- 	
-- 	
-- 	-- 6. get differences and apply to permanent table
-- 	qstr := "create temporary table " || change_table || " as select table_version.ver_get_table_differences('" || admin_bdys.meshblock || "','" || admin_bdys_import.meshblock_compare || "','" || code "')";
	
	-- copy final table from permanent then revision it with the new changes
	
	--apply changeset to permanent table
 
end;
$$ language plpgsql;

--create table admin_bdys_import.del_mb as select * from admin_bdys_import.temp_meshblock


