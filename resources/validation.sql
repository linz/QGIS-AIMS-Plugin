create function validation_meshblock/nzlocalities() returns integer as 
$$
declare
begin
end;
$$ 
language plpgsql VOLATILE;

-- -------------------------------------------------------------------

create function validation_meshblock_numcodechar() returns integer as 
$$
declare
	maxlen int := 7
begin
select count(*) from meshblock where len(col)>7 
	
begin
end;
$$ 
language plpgsql VOLATILE;