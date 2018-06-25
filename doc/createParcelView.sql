    DROP VIEW IF EXISTS bde.parcel_appellation_view;
    CREATE OR REPLACE VIEW  bde.parcel_appellation_view AS 
    SELECT bde.bde_get_combined_appellation(crs_parcel.id, 'N') AS appellation,
           crs_parcel.id AS par_id
    FROM   bde.crs_parcel
    WHERE  bde.crs_parcel.status = 'CURR' 
    AND    bde.crs_parcel.toc_code = 'PRIM';
    ALTER TABLE bde.parcel_appellation_view OWNER TO bde_dba;
    GRANT SELECT ON TABLE bde.parcel_appellation_view TO aims_user;