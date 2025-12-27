# Shipment Batch Data Generator

A Python script that generates realistic shipment batch data files in INI format for data engineering projects and testing purposes.

## 📋 Overview

This script generates 200 simulated shipment batch files with realistic logistics data ready to be imported in the project.


## 🎯 Features

- **200 unique shipment batch files** with randomized data
- **Random dates** distributed across entire year (2025)
- **4 shipment categories**: STANDARD, EXPRESS, BULK, INTERNATIONAL
- **5 package types per batch** with varying weights and characteristics
- **8 different origin facilities** (distribution hubs)
- **Realistic data patterns** including:
  - Weight ranges by package class
  - Load percentage calculations
  - Package counts
  - Routing rules
  - Destination hubs

## 📦 Generated Data Structure

Each file follows this INI format structure:

```ini
[SHIPMENT_BATCH]
ShipmentBatchID=SHX15012025A
DispatchDate=15/01/2025
DispatchTime=073215
CompletionDate=15/01/2025
CompletionTime=132540
OriginFacilityID=HUB_N01
ShipmentCategory=STANDARD
HandlingClass=REGULAR
BatchNotes=Generated shipment batch for standard distribution

[PACKAGE_TYPE_1]
package_class=light parcels
total_weight_kg=00125400
load_percentage_bp=00110
package_count=000420
routing_rules=Weight|light parcels|100.00|500.00
destination_hubs=2

[PACKAGE_TYPE_2]
...
```

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- No external dependencies required (uses only standard library)

### Usage

1. **Download the script**:
   ```bash
   # Save as generate_shipments.py
   ```

2. **Run the generator**:
   ```bash
   python generate_ini_files.py
   ```

3. **Output**:
   - Creates a `generated_shipment_batches/` directory
   - Generates 200 `.txt` files in INI format
   - Shows progress every 20 files

### Example Output

```
🚀 Generating 200 shipment batch files...

📅 Dates distributed across entire 2025 (365 days)

✅ Progress: 20/200 files generated
✅ Progress: 40/200 files generated
...
✅ Progress: 200/200 files generated

📁 All files saved in: generated_shipment_batches/
📊 Total files generated: 200
```

## 📊 Data Categories

### Shipment Categories

| Category | Handling Class | Typical Use Case |
|----------|---------------|------------------|
| STANDARD | REGULAR | Regional distribution |
| EXPRESS | PRIORITY | High-priority delivery |
| BULK | HEAVY | Large volume shipments |
| INTERNATIONAL | CUSTOMS | Cross-border shipping |

## 🔧 Customization

### Change Number of Files

Edit the `num_files` variable in the `main()` function:

```python
num_files = 200  # Change to desired number
```

### Modify Date Range

Adjust the year range in the `main()` function:

```python
year_start = datetime(2025, 1, 1)
year_end = datetime(2025, 12, 31)
```

### Add Custom Package Types

Extend the `PACKAGE_CLASSES` dictionary with new categories:

```python
PACKAGE_CLASSES = {
    'CUSTOM_CATEGORY': [
        ('package_class', (min_weight, max_weight), (min_total, max_total), (min_count, max_count)),
        # Add more types...
    ]
}
```

## 📁 File Naming Convention

Files are named with timestamp prefix for uniqueness:

```
{timestamp}_shipment_batch_{sequence}.txt
```

Example: `1766769508781_shipment_batch_001.txt`
