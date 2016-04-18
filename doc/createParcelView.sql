
-- View with standarised geomerty types to allow loading to Qgis

DROP MATERIALIZED VIEW IF EXISTS lds.all_parcel_multipoly; 

CREATE MATERIALIZED VIEW lds.all_parcel_multipoly AS 
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

ALTER TABLE lds.all_parcel_multipoly OWNER TO aims_dba;
GRANT SELECT ON TABLE lds.all_parcel_multipoly TO aims_user;



CREATE INDEX aims_all_par_shape
  ON lds.all_parcel_multipoly
  USING gist
  (shape);