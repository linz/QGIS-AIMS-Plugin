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

-- select validation_meshblock_numcodechar();
create or replace function validation_meshblock_numcodechar() returns integer as 
$$
declare
	max_len int := 7;
	mbq1 varchar := 'select count(*) from admin_bdys.meshblock where char_length(mb_code)<>'||max_len;
	err_count int;
begin

execute mbq1 into err_count;
return err_count;
	
end;
$$ 
language plpgsql VOLATILE;