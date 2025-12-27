CREATE TABLE IF NOT EXISTS `${PROJECT_ID}.${BQ_DATASET}.${BQ_TABLE_DIM}` 
(
  shipment_batch_ID   STRING,
  dispatch_date        TIMESTAMP,
  dispatch_time        STRING,
  completion_date      TIMESTAMP,
  completion_time      STRING,
  origin_facility_ID   STRING,
  shipment_category    STRING,
  handling_class       STRING,
  remarks              STRING,
  creation_data        TIMESTAMP
)
PARTITION BY DATE(creation_data);