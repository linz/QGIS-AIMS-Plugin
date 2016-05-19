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


CREATE TABLE admin_bdys_import.temp_meshblock
(
  objectid integer,
  mb_code character varying NOT NULL,
  wkt geometry,
  CONSTRAINT meshblock_pkey PRIMARY KEY (mb_code)
);

CREATE TABLE admin_bdys_import.temp_meshblock_concordance
(
  objectid integer,
  mb_code character varying NOT NULL,
  ta_code character varying,
  ta_label character varying,
  ward_code character varying,
  ward_label character varying,
  cb_code character varying,
  cb_label character varying,
  tasub_code character varying,
  tasub_label character varying,
  mward_code character varying,
  mward_label character varying,
  regc_code character varying,
  regc_label character varying,
  con_code character varying,
  con_label character varying,
  mcon_code character varying,
  mcon_label character varying,
  dhb_code character varying,
  dhb_label character varying,
  dhbcon_code character varying,
  dhbcon_label character varying,
  ged2007_code character varying,
  ged2007_label character varying,
  med2007_code character varying,
  med2007_label character varying,
  hc_code character varying,
  hc_label character varying,
  dc_code character varying,
  dc_label character varying,
  ged_code character varying,
  ged_label character varying,
  med_code character varying,
  med_label character varying,
  ltward_code character varying,
  ltward_label character varying,
  CONSTRAINT meshblock_concordance_pkey PRIMARY KEY (mb_code)
);

CREATE TABLE admin_bdys_import.temp_nz_localities
(
  ogc_fid serial NOT NULL,
  geom geometry(MultiPolygon,900914),
  CONSTRAINT nz_localities_pkey PRIMARY KEY (ogc_fid)
);

CREATE TABLE admin_bdys_import.temp_meshblock_concordance
(
  objectid integer,
  mb_code character varying NOT NULL,
  ta_code character varying,
  ta_label character varying,
  ward_code character varying,
  ward_label character varying,
  cb_code character varying,
  cb_label character varying,
  tasub_code character varying,
  tasub_label character varying,
  mward_code character varying,
  mward_label character varying,
  regc_code character varying,
  regc_label character varying,
  con_code character varying,
  con_label character varying,
  mcon_code character varying,
  mcon_label character varying,
  dhb_code character varying,
  dhb_label character varying,
  dhbcon_code character varying,
  dhbcon_label character varying,
  ged2007_code character varying,
  ged2007_label character varying,
  med2007_code character varying,
  med2007_label character varying,
  hc_code character varying,
  hc_label character varying,
  dc_code character varying,
  dc_label character varying,
  ged_code character varying,
  ged_label character varying,
  med_code character varying,
  med_label character varying,
  ltward_code character varying,
  ltward_label character varying,
  CONSTRAINT meshblock_concordance_pkey PRIMARY KEY (mb_code)
);

