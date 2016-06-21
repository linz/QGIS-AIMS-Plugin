-- Materialized View: lds.all_parcel_multipoly

-- DROP MATERIALIZED VIEW lds.all_parcel_multipoly;

CREATE MATERIALIZED VIEW lds.all_parcel_multipoly AS 
 SELECT row_number() OVER () AS gid,
    all_parcels.id,
    all_parcels.appellation,
    all_parcels.affected_surveys,
    all_parcels.parcel_intent,
    all_parcels.topology_type,
    all_parcels.status,
    all_parcels.statutory_actions,
    all_parcels.land_district,
    all_parcels.titles,
    all_parcels.survey_area,
    all_parcels.calc_area,
    ST_SetSRID(st_multi(all_parcels.shape),4167) AS shape
   FROM lds.all_parcels
    WHERE (ST_GeometryType(shape) = 'ST_MultiPolygon'
  OR  ST_GeometryType(shape) = 'ST_Polygon')
  AND status = 'Current'
WITH DATA;

ALTER TABLE lds.all_parcel_multipoly
  OWNER TO aims_dba;
GRANT ALL ON TABLE lds.all_parcel_multipoly TO aims_dba;
GRANT SELECT ON TABLE lds.all_parcel_multipoly TO aims_user;
