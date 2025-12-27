CREATE TABLE `${PROJECT_ID}.${BQ_DATASET}.${BQ_TABLE_FACT}`
(
  shipment_batch_ID   STRING,
  package_class       STRING,
  total_weight_kg     FLOAT64,
  load_percentage_bp  INT64,
  package_count       INT64,
  routing_rules       STRING,
  destination_hubs    STRING
)
CLUSTER BY shipment_batch_ID, package_class;