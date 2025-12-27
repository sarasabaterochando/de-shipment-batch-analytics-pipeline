# Power BI Analytics Overview

This Power BI report analyzes shipment batch data processed through a Google Cloud–based data pipeline. The data is ingested from batch .ini files, transformed using PySpark on Dataproc, stored in BigQuery, and consumed in Power BI for analytical reporting.

The report is built on a well-structured analytical data model, designed to support scalable analysis and efficient querying.

## Data Modeling Approach

The initial dataset consisted of two main tables:

* factShipment

* dimShipment

![DimShipment table](https://github.com/sarasabaterochando/de-shipment-batch-analytics-pipeline/blob/main/PowerBI/images/dim-shipment-table.png)

To improve analytical performance and follow best practices, the original dimShipment table was decomposed into multiple dimension tables. The data model was redesigned into a star schema, with:

* factShipment as the central fact table

* Multiple dimension tables surrounding the fact table

* Proper one-to-many relationships defined between fact and dimensions

This modeling approach improves readability, performance, and flexibility for analytical use cases.

![Star schema](https://github.com/sarasabaterochando/de-shipment-batch-analytics-pipeline/blob/main/PowerBI/images/star-schema.png)

## Calendar Table

A dedicated **Calendar (Date) table** was created and integrated into the model.
```
Calendar = 
ADDCOLUMNS(
    CALENDAR(
        DATE(YEAR(MIN(FactShipment[dispatch_datetime])), 1, 1),
        DATE(YEAR(MAX(FactShipment[completion_datetime])), 12, 31)
    ),
    "Year", YEAR([Date]),
    "Month_num", MONTH([Date]),
    "Day", DAY([Date]),
    "Month_txt", FORMAT([Date], "mmm", "en-US")
)
```

This enables:

* Time intelligence analysis

* Consistent filtering across all visuals

* Support for date-based aggregations and trends

## Slicers and Interactivity

* All report slicers are synchronized across pages, ensuring consistent filtering and a cohesive user experience

* The model supports slicing and dicing by multiple shipment attributes and time dimensions

![Slicers](https://github.com/sarasabaterochando/de-shipment-batch-analytics-pipeline/blob/main/PowerBI/images/slicers.png)

## Analytical Capabilities

* Batch-level and shipment-level analysis

* Aggregated shipment volumes and distributions

* Time-based trend analysis using the calendar dimension

* High-level KPIs for operational monitoring

## Example Power BI Measures (DAX) 
Measures are centralized in a dedicated measures table to improve model organization and maintainability.

```
Same Day Completion % = 
DIVIDE(
    CALCULATE(
        DISTINCTCOUNT(FactShipment[shipment_batch_ID]),
        DATEVALUE(FactShipment[dispatch_datetime]) = DATEVALUE(FactShipment[completion_datetime])
    ),
    DISTINCTCOUNT(FactShipment[shipment_batch_ID])
)
```
```
Average Load Per Batch = 
AVERAGEX(
    VALUES(FactShipment[shipment_batch_ID]),
    CALCULATE(
        SUM(FactShipment[total_weight_kg]))
)
```

```
Total Packages = 
CALCULATE(
    SUM(FactShipment[package_count]),
    FactShipment[Id_FactShipment])
```

```
Overloaded Shipments % = 
VAR _totalPackages =
    DISTINCTCOUNT(FactShipment[shipment_batch_ID])

VAR _overloadedShipment =
    CALCULATE(
        DISTINCTCOUNT(FactShipment[shipment_batch_ID]),
        FILTER(
            VALUES(FactShipment[shipment_batch_ID]),
            [Overload Shipment Flag] = 1
        )
    )
RETURN 
DIVIDE(_overloadedShipment,_totalPackages)
```













