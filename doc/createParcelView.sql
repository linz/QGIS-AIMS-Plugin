
-- View with standarised geomerty types to allow loading to Qgis

DROP VIEW IF EXISTS data.all_parcel_multipoly; 

CREATE VIEW data.all_parcel_multipoly AS 
 SELECT row_number() OVER () AS gid,
 	id,
	appellation,
	affected_surveys, 
	parcel_intent, 
	topology_type, 
	status, 
	statutory_actions, 
	land_district, 
	titles, 
	survey_area, 
	calc_area, 
	ST_Multi(shape) AS shape-- Cast all to MultiPolygon
  FROM lds.all_parcels;

ALTER TABLE data.all_parcel_multipoly OWNER TO aims_dba;
GRANT SELECT ON TABLE data.all_parcel_multipoly TO aims_user;
