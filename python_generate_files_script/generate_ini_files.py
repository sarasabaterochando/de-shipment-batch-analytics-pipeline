import random
from datetime import datetime, timedelta
import os

# Configuración de datos para generar variedad
FACILITIES = ['HUB_N01', 'HUB_E03', 'HUB_S02', 'HUB_W05', 'HUB_C04', 'HUB_N06', 'HUB_E07', 'HUB_S08']
CATEGORIES = ['STANDARD', 'EXPRESS', 'BULK', 'INTERNATIONAL']
HANDLING_CLASSES = ['REGULAR', 'PRIORITY', 'HEAVY', 'CUSTOMS', 'FRAGILE']

PACKAGE_CLASSES = {
    'STANDARD': [
        ('light parcels', (100, 500), (100000, 200000), (300, 600)),
        ('medium parcels', (500, 1500), (400000, 600000), (800, 1500)),
        ('heavy parcels', (1500, 4000), (1000000, 1500000), (1800, 2800)),
        ('oversized', (4000, 8000), (500000, 800000), (600, 1000)),
        ('bulk items', (8000, 15000), (800000, 1200000), (200, 400))
    ],
    'EXPRESS': [
        ('documents', (0.1, 2), (70000, 100000), (1800, 2400)),
        ('small parcels', (2, 20), (200000, 300000), (1200, 1800)),
        ('fragile goods', (5, 50), (300000, 450000), (700, 1200)),
        ('secure cargo', (50, 500), (800000, 1100000), (350, 550)),
        ('premium delivery', (20, 200), (350000, 500000), (400, 700))
    ],
    'BULK': [
        ('palletized goods', (800, 2000), (1500000, 2200000), (500, 800)),
        ('industrial parts', (2000, 6000), (2000000, 2800000), (900, 1400)),
        ('machinery', (6000, 15000), (2800000, 3500000), (250, 400)),
        ('oversized freight', (15000, 30000), (1200000, 1700000), (150, 250)),
        ('heavy equipment', (30000, 50000), (1500000, 2000000), (50, 120))
    ],
    'INTERNATIONAL': [
        ('customs_docs', (0.05, 1), (25000, 40000), (1600, 2100)),
        ('export_goods', (10, 1000), (1100000, 1500000), (2000, 2800)),
        ('restricted_items', (1, 100), (400000, 550000), (500, 800)),
        ('container_loads', (1000, 25000), (2500000, 3200000), (100, 180)),
        ('air_freight', (50, 5000), (600000, 900000), (300, 600))
    ]
}


def generate_shipment_id(date, sequence):
    """Genera un ID de envío único"""
    date_str = date.strftime('%d%m%Y')
    letter = chr(65 + sequence)  # A, B, C, etc.
    return f"SHX{date_str}{letter}"


def format_time(dt):
    """Formatea hora como HHMMSS"""
    return dt.strftime('%H%M%S')


def format_date(dt):
    """Formatea fecha como DD/MM/YYYY"""
    return dt.strftime('%d/%m/%Y')


def generate_routing_rules(package_class, weight_range):
    """Genera reglas de enrutamiento basadas en la clase de paquete"""
    min_w, max_w = weight_range
    rules = f"Weight|{package_class}|{min_w:.2f}|{max_w:.2f}"

    # Añadir reglas adicionales según la clase
    if 'fragile' in package_class.lower():
        rules += f"|Fragility|{package_class}|1|3"
    elif 'oversized' in package_class.lower():
        rules += f"|Length|{package_class}|120.00|200.00"
    elif 'restricted' in package_class.lower():
        rules += f"|Clearance|{package_class}|Y|Y"
    elif 'freight' in package_class.lower():
        rules += f"|Height|{package_class}|180.00|300.00"

    return rules


def calculate_load_percentage(weight, total_capacity=280000000):
    """Calcula el porcentaje de carga en basis points (1bp = 0.01%)"""
    percentage = (weight / total_capacity) * 10000
    return int(percentage)


def generate_destination_hubs(num_hubs):
    """Genera lista de hubs de destino"""
    available_hubs = list(range(1, 15))
    selected = random.sample(available_hubs, min(num_hubs, len(available_hubs)))
    return '|'.join(map(str, sorted(selected)))


def generate_batch_file(sequence, base_date):
    """Genera un archivo de lote de envío"""

    # Usar la fecha base directamente (ya es aleatoria)
    dispatch_date = base_date
    dispatch_time = dispatch_date.replace(
        hour=random.randint(6, 20),
        minute=random.randint(0, 59),
        second=random.randint(0, 59)
    )

    # Fecha de completación (6-12 horas después)
    completion_time = dispatch_time + timedelta(hours=random.randint(6, 12))

    # Seleccionar categoría y clase de manejo
    category = random.choice(CATEGORIES)
    handling_class = random.choice(HANDLING_CLASSES)
    facility = random.choice(FACILITIES)

    # Generar ID de envío
    shipment_id = generate_shipment_id(dispatch_date, sequence)

    # Timestamp para nombre de archivo
    timestamp = int(datetime.now().timestamp() * 1000) + sequence
    filename = f"{timestamp}_shipment_batch_{sequence:03d}.txt"

    # Seleccionar tipos de paquete según la categoría
    package_types = PACKAGE_CLASSES[category]

    # Generar contenido del archivo
    content = f"""[SHIPMENT_BATCH]
ShipmentBatchID={shipment_id}
DispatchDate={format_date(dispatch_date)}
DispatchTime={format_time(dispatch_time)}
CompletionDate={format_date(completion_time)}
CompletionTime={format_time(completion_time)}
OriginFacilityID={facility}
ShipmentCategory={category}
HandlingClass={handling_class}
BatchNotes=Generated shipment batch for {category.lower()} distribution
"""

    # Añadir cada tipo de paquete
    for idx, (pkg_class, weight_range, weight_total_range, count_range) in enumerate(package_types, 1):
        # Generar valores aleatorios dentro de los rangos
        total_weight = random.randint(weight_total_range[0], weight_total_range[1])
        load_pct = calculate_load_percentage(total_weight)
        package_count = random.randint(count_range[0], count_range[1])

        # Generar reglas de enrutamiento
        routing = generate_routing_rules(pkg_class, weight_range)

        # Generar hubs de destino (1-3 hubs)
        num_hubs = random.randint(1, 3)
        dest_hubs = generate_destination_hubs(num_hubs)

        content += f"""
[PACKAGE_TYPE_{idx}]
package_class={pkg_class}
total_weight_kg={total_weight:08d}
load_percentage_bp={load_pct:05d}
package_count={package_count:06d}
routing_rules={routing}
destination_hubs={dest_hubs}
"""

    return filename, content


def main():
    """Función principal para generar los archivos"""
    output_dir = "generated_shipment_batches"
    os.makedirs(output_dir, exist_ok=True)

    # Año completo 2025: desde 1 enero hasta 31 diciembre
    year_start = datetime(2025, 1, 1)
    year_end = datetime(2025, 12, 31)
    total_days = (year_end - year_start).days

    num_files = 200
    print(f"🚀 Generando {num_files} archivos de lotes de envío...\n")
    print(f"📅 Fechas distribuidas en todo 2025 (365 días)\n")

    for i in range(num_files):
        # Fecha aleatoria en cualquier día del año
        random_days = random.randint(0, total_days)
        random_date = year_start + timedelta(days=random_days)

        filename, content = generate_batch_file(i, random_date)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        if (i + 1) % 20 == 0:
            print(f"✅ Progreso: {i + 1}/{num_files} archivos generados")

    print(f"\n📁 Todos los archivos guardados en: {output_dir}/")
    print(f"📊 Total de archivos generados: {num_files}")


if __name__ == "__main__":
    main()