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
-- drop function admin_bdys_import.import_admin_boundary(character varying);

--select admin_bdys_import.import_admin_boundary('meshblock_concordance')
--select admin_bdys_import.import_admin_boundary('statsnz_meshblock')
--select admin_bdys_import.import_admin_boundary('statsnz_ta')
--select admin_bdys_import.import_admin_boundary('nz_locality')
create or replace function admin_bdys_import.import_admin_boundary(name varchar) 
returns record as $$
declare
	srid text := '4167';
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
	map_tableonly text := map_prefix || name;
	map_table text := import_schema || '.' || map_tableonly; 	--column mapped import table
	snap_table text := import_schema || '.' || snap_prefix || name; --snapshot of perm table
	--copy_table text := import_schema || '.' || copy_prefix || name;
	
	--first entry must be the pk column
	mb  text[][] := array[['mb_code','code'],['geom','shape']];
	mbc text[][] := array[['meshblock','meshblock'],['1','1']];
	nzl text[][] := array[['id','id'],['geom','shape']];
	ta  text[][] := array[['ogc_fid','ogc_fid'],['geom','shape']];
	
	selection text[][];
	rep text[];
	drop_cols text[];
	cast_cols text[][];
	dc text;
	cc text;
	final_table text;
	result record;
	
	-- array_position function doesn't exist in this version of postgresql
	-- map_index int := array_position(map_name,name::text);
	
begin
	-- 1. create a new table to map imports to final table format 
	qstr := 'create table ' || map_table || ' as select * from ' || import_table;
	raise notice '1.1 %',qstr;
	execute qstr;-- into result;

	case name
		when 'statsnz_meshblock' then
			selection := mb;
			final_table := primary_schema || '.meshblock';
		when 'meshblock_concordance' then
			selection := mbc;
			final_table := primary_schema || '.meshblock_concordance';
		when 'nz_locality' then
			selection := nzl;
			drop_cols := array['ogc_fid'];
			cast_cols := array[['id','integer']];
			final_table := primary_schema || '.nz_locality';
		when 'statsnz_ta' then
			selection := ta;
			drop_cols := array['ta_code'];
			final_table := primary_schema || '.territorial_authority';
		else
			raise notice 'Cannot match table %',name;
	end case;

	foreach rep slice 1 in array selection[1:array_upper(selection,1)]
	loop
		if rep[1] != rep[2] then
			qstr := 'alter table ' || map_table || ' rename column ' || rep[1] || ' to ' || rep[2];
			raise notice '1.2 %',qstr;
			execute qstr;-- into result;
		end if;
	end loop;

	-- 2. transform srids

	if selection <> mbc then
		qstr := 'set search_path to admin_bdys,admin_bdys_import,public';
		raise notice '2.1 %',qstr;	
		execute qstr;-- into result;

		qstr := 'select addgeometrycolumn(' || quote_literal(map_tableonly) || ',' || quote_literal('temp') || ',' || srid || ', ' || quote_literal('MULTIPOLYGON') || ', 2)';
		raise notice '2.2 %',qstr;	
		execute qstr;-- into result;
		
		qstr := 'update ' || map_table || ' set temp = st_transform( st_setsrid(shape,4167),4167)';
		raise notice '2.3 %',qstr;	
		execute qstr;-- into result;
		
		qstr := 'alter table ' || map_table || ' drop column shape';
		raise notice '2.4 %',qstr;	
		execute qstr;-- into result;
		
		qstr := 'alter table ' || map_table || ' rename column temp to shape';
		raise notice '2.5 %',qstr;	
		execute qstr;-- into result;
	end if;

	-- 3. reformat maptable
	
	if array_length(drop_cols,1) > 0 then
		foreach dc in array drop_cols
		loop
			qstr := 'alter table ' || map_table ||' drop column '|| dc;
			raise notice '3.1 %',qstr;	
			execute qstr;-- into result;
		end loop;
	end if;

	if array_length(cast_cols,1) > 0 then
		foreach cc in array cast_cols
		loop
			qstr := 'alter table '|| map_table ||' alter column '|| cc ||' set data type '|| cc;
			raise notice '3.2 %',qstr;	
			execute qstr;-- into result;
		end loop;
	end if;

	-- 4. designate primary key
	

	qstr := 'alter table ' || map_table || ' add primary key (' || selection[1][2] || ')';
	raise notice '4.1 %',qstr;	
	execute qstr;-- into result;

	-- 5. apply differences to perm table
	--<temp>
	qstr := 'create table ' || snap_table || ' as select * from ' || final_table;
	raise notice '5.1 %',qstr;	
	execute qstr;-- into result;

	qstr := 'alter table ' || snap_table || ' add primary key (' || selection[1][2] || ')';
	raise notice '5.2 %',qstr;	
	execute qstr;-- into result;
	--</temp>
	--qstr := 'select 1';
	qstr := 'select table_version.ver_apply_table_differences(' || quote_literal(snap_table) || ',' || quote_literal(map_table) || ',' || quote_literal(selection[1][2] ) || ')';
	raise notice '5.3 %',qstr;	

	execute qstr into result;
	
	return result;
 
end;
$$ language plpgsql;

--create table admin_bdys_import.del_mb as select * from admin_bdys_import.temp_meshblock


-- create table admin_bdys_import.x_statsnz_meshblock as select * from admin_bdys_import.temp_statsnz_meshblock;
-- 

/*
update admin_bdys_import.x_statsnz_meshblock set geom = st_transform( st_setsrid(geom,4167),4167);

set search_path to admin_bdys,admin_bdys_import,public;
select addgeometrycolumn('x_statsnz_meshblock','geom2',4167, 'MULTIPOLYGON', 2);
update admin_bdys_import.x_statsnz_meshblock set geom2 = st_transform( st_setsrid(geom,4167),4167);
alter table admin_bdys_import.x_statsnz_meshblock drop column geom;
alter table admin_bdys_import.x_statsnz_meshblock rename column geom2 to geom
*/


