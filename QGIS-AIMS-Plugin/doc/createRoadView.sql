DROP VIEW IF EXISTS reference.aimsroads ;

CREATE VIEW reference.aimsroads AS
SELECT 	rp.roadprefixname,
	rn.roadname,
	rs.roadsuffixname,
	rt.roadtypename,
	rn.roadnameid,
	rcl.roadcentrelineid,
	rcl.roadcentrelinealtid,
	rn.roadnametype,
	rcl.noncadastralroad,
	
	rn.roadnamestatus,
	rn.unoffocial,
	rn.sufi,
	rcl.shape,
	rcl.organisationid
FROM reference.roadcentreline rcl JOIN reference.roadnameassociation rna 
ON rcl.roadcentrelineid = rna.roadcentrelineid 
JOIN reference.roadname rn ON rn.roadnameid =  rna.roadnameid 
LEFT JOIN reference.roadtype rt ON rn.roadtypeid = rt.roadtypeid
LEFT JOIN reference.roadsuffix rs ON rn.roadsuffixid = rs.roadsuffixid
LEFT JOIN reference.roadprefix rp ON rn.roadprefixid = rp.roadprefixid
WHERE rcl.roadcentrelinestatus = 'CURR' AND rna.rnapriority = 1 AND rn.roadnamestatus = 'CURR';

ALTER TABLE reference.aimsroads
OWNER TO aims_sa;

GRANT ALL ON TABLE reference.aimsroads TO aims_sa;
GRANT SELECT ON TABLE reference.aimsroads TO aims_user;
