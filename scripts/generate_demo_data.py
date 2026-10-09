import os
import json
import random
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set fixed seeds for reproducibility
random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DEMO_DIR = os.path.join(BASE_DIR, 'data', 'demo')
DATA_TEMPLATE_DIR = os.path.join(BASE_DIR, 'data', 'templates')

os.makedirs(DATA_DEMO_DIR, exist_ok=True)
os.makedirs(DATA_TEMPLATE_DIR, exist_ok=True)

print(f"Generating synthetic demonstration data in {DATA_DEMO_DIR}...")

# 1. Mines
mines = [
    {
        "id": "MINE-001",
        "name": "Dongri Buzurg Manganese Mine",
        "code": "DBM-01",
        "location": "Bhandara District, Maharashtra, India",
        "latitude": 21.5342,
        "longitude": 79.6915,
        "elevation": 320.0,
        "operational_status": "Active"
    },
    {
        "id": "MINE-002",
        "name": "Mansar Manganese Mine",
        "code": "MSM-02",
        "location": "Nagpur District, Maharashtra, India",
        "latitude": 21.3912,
        "longitude": 79.2568,
        "elevation": 305.0,
        "operational_status": "Active"
    },
    {
        "id": "MINE-003",
        "name": "Balaghat Manganese Mine",
        "code": "BGM-03",
        "location": "Balaghat District, Madhya Pradesh, India",
        "latitude": 21.8134,
        "longitude": 80.1843,
        "elevation": 345.0,
        "operational_status": "Active"
    }
]
df_mines = pd.DataFrame(mines)
df_mines.to_csv(os.path.join(DATA_DEMO_DIR, 'mines.csv'), index=False)
df_mines.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'mines_template.csv'), index=False)

# 2. Mine Boundary GeoJSON (Dongri Buzurg Mine)
mine_lat, mine_lon = 21.5342, 79.6915
dlat = 0.02
dlon = 0.02

mine_boundary = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {
                "mine_id": "MINE-001",
                "name": "Dongri Buzurg Mine Perimeter",
                "area_sqkm": 8.45
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [mine_lon - dlon, mine_lat - dlat],
                    [mine_lon + dlon, mine_lat - dlat],
                    [mine_lon + dlon, mine_lat + dlat],
                    [mine_lon - dlon, mine_lat + dlat],
                    [mine_lon - dlon, mine_lat - dlat]
                ]]
            }
        }
    ]
}
with open(os.path.join(DATA_DEMO_DIR, 'mine_boundaries.geojson'), 'w') as f:
    json.dump(mine_boundary, f, indent=2)

# 3. Geological Units
geo_units = [
    {"id": "GEO-01", "mine_id": "MINE-001", "name": "Manganese Ore Belt", "code": "MN-ORE", "description": "High-grade gondite manganese ore body", "rock_type": "Manganese Gondite", "color": "#8B5CF6"},
    {"id": "GEO-02", "mine_id": "MINE-001", "name": "Quartzite Footwall", "code": "QTZ-FW", "description": "Massive pink and white quartzite", "rock_type": "Quartzite", "color": "#F59E0B"},
    {"id": "GEO-03", "mine_id": "MINE-001", "name": "Mica Schist Hangingwall", "code": "SCH-HW", "description": "Foliated quartz-muscovite mica schist", "rock_type": "Schist", "color": "#10B981"},
    {"id": "GEO-04", "mine_id": "MINE-001", "name": "Pegmatite Intrusion", "code": "PEG-INT", "description": "Coarse-grained pegmatite dyke", "rock_type": "Pegmatite", "color": "#EC4899"}
]
df_geology = pd.DataFrame(geo_units)
df_geology.to_csv(os.path.join(DATA_DEMO_DIR, 'geological_units.csv'), index=False)
df_geology.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'geological_units_template.csv'), index=False)

# 4. Boreholes & Intervals & Assays
boreholes = []
intervals = []
assays = []

num_boreholes = 30
borehole_id_cnt = 1
interval_id_cnt = 1
assay_id_cnt = 1

start_date = datetime(2025, 1, 1)

for i in range(num_boreholes):
    b_id = f"BH-{borehole_id_cnt:03d}"
    # Generate within mine boundary
    offset_x = np.random.uniform(-0.015, 0.015)
    offset_y = np.random.uniform(-0.015, 0.015)
    blat = round(mine_lat + offset_y, 6)
    blon = round(mine_lon + offset_x, 6)
    elev = round(320.0 + np.random.uniform(-10, 15), 2)
    depth = round(np.random.uniform(80, 220), 2)
    b_date = start_date + timedelta(days=int(np.random.uniform(0, 180)))
    
    boreholes.append({
        "id": b_id,
        "mine_id": "MINE-001",
        "borehole_id": b_id,
        "latitude": blat,
        "longitude": blon,
        "elevation": elev,
        "total_depth": depth,
        "start_date": b_date.strftime("%Y-%m-%d"),
        "end_date": (b_date + timedelta(days=5)).strftime("%Y-%m-%d")
    })
    
    # Generate intervals
    curr_depth = 0.0
    # Determine if borehole hits main mineralization zone (higher probability near central strike)
    dist_from_center = math.sqrt((offset_x/0.015)**2 + (offset_y/0.015)**2)
    is_mineralized_zone = dist_from_center < 0.65
    
    while curr_depth < depth:
        int_len = round(np.random.uniform(2.0, 8.0), 2)
        to_depth = min(depth, round(curr_depth + int_len, 2))
        
        if is_mineralized_zone and (curr_depth > 30 and curr_depth < 120) and np.random.rand() > 0.3:
            lith = "Manganese Gondite"
            mn_grade = round(np.random.uniform(28.0, 48.5), 2)
            fe_grade = round(np.random.uniform(4.0, 9.5), 2)
            sio2_grade = round(np.random.uniform(6.0, 16.0), 2)
        else:
            lith = np.random.choice(["Quartzite", "Schist", "Pegmatite"])
            mn_grade = round(np.random.uniform(0.2, 4.5), 2)
            fe_grade = round(np.random.uniform(2.0, 14.0), 2)
            sio2_grade = round(np.random.uniform(45.0, 75.0), 2)
            
        int_id = f"INT-{interval_id_cnt:04d}"
        intervals.append({
            "id": int_id,
            "borehole_id": b_id,
            "from_depth": curr_depth,
            "to_depth": to_depth,
            "lithology": lith,
            "mn_grade": mn_grade
        })
        
        sample_id = f"SMP-{assay_id_cnt:04d}"
        assays.append({
            "id": sample_id,
            "interval_id": int_id,
            "sample_id": sample_id,
            "mn_grade": mn_grade,
            "fe_grade": fe_grade,
            "sio2_grade": sio2_grade,
            "sample_date": (b_date + timedelta(days=3)).strftime("%Y-%m-%d"),
            "assay_source": "MOIL Central Geology Lab"
        })
        
        interval_id_cnt += 1
        assay_id_cnt += 1
        curr_depth = to_depth
        
    borehole_id_cnt += 1

df_bh = pd.DataFrame(boreholes)
df_bh.to_csv(os.path.join(DATA_DEMO_DIR, 'boreholes.csv'), index=False)
df_bh.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'boreholes_template.csv'), index=False)

df_int = pd.DataFrame(intervals)
df_int.to_csv(os.path.join(DATA_DEMO_DIR, 'borehole_intervals.csv'), index=False)
df_int.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'borehole_intervals_template.csv'), index=False)

df_ass = pd.DataFrame(assays)
df_ass.to_csv(os.path.join(DATA_DEMO_DIR, 'assay_samples.csv'), index=False)
df_ass.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'assay_samples_template.csv'), index=False)

# 5. Ore Blocks Grid
blocks = []
grid_size = 5
block_code_cnt = 1

min_x_base = 79.675
min_y_base = 21.518
step = 0.005

for gx in range(grid_size):
    for gy in range(grid_size):
        bx_min = round(min_x_base + gx * step, 4)
        bx_max = round(bx_min + step, 4)
        by_min = round(min_y_base + gy * step, 4)
        by_max = round(by_min + step, 4)
        
        center_x = (bx_min + bx_max) / 2
        center_y = (by_min + by_max) / 2
        
        dist_c = math.sqrt(((center_x - mine_lon)/0.015)**2 + ((center_y - mine_lat)/0.015)**2)
        
        volume = 250000.0  # 50m x 50m x 100m equivalent block
        bulk_density = 3.4  # tonnes/m3 for manganese ore body
        tonnage = volume * bulk_density
        
        if dist_c < 0.5:
            est_mn = round(np.random.uniform(32.0, 44.0), 2)
            category = "Measured"
        elif dist_c < 0.8:
            est_mn = round(np.random.uniform(22.0, 33.0), 2)
            category = "Indicated"
        elif dist_c < 1.1:
            est_mn = round(np.random.uniform(12.0, 22.0), 2)
            category = "Inferred"
        else:
            est_mn = round(np.random.uniform(2.0, 11.0), 2)
            category = "Exploration Target"
            
        contained_mn = round(tonnage * est_mn / 100.0, 2)
        
        blocks.append({
            "id": f"BLK-{block_code_cnt:03d}",
            "mine_id": "MINE-001",
            "block_code": f"BLK-DBM-{block_code_cnt:03d}",
            "min_x": bx_min,
            "max_x": bx_max,
            "min_y": by_min,
            "max_y": by_max,
            "min_z": 100.0,
            "max_z": 250.0,
            "volume_m3": volume,
            "bulk_density": bulk_density,
            "tonnage": tonnage,
            "est_mn_grade": est_mn,
            "contained_mn_tonnes": contained_mn,
            "category": category
        })
        block_code_cnt += 1

df_blocks = pd.DataFrame(blocks)
df_blocks.to_csv(os.path.join(DATA_DEMO_DIR, 'ore_blocks.csv'), index=False)
df_blocks.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'ore_blocks_template.csv'), index=False)

# 6. Equipment & Equipment Downtime
equipment = [
    {"id": "EQ-01", "mine_id": "MINE-001", "name": "Excavator CAT 390F #1", "equipment_type": "Excavator", "status": "Operational", "capacity_tph": 350.0},
    {"id": "EQ-02", "mine_id": "MINE-001", "name": "Excavator Komatsu PC1250 #2", "equipment_type": "Excavator", "status": "Operational", "capacity_tph": 400.0},
    {"id": "EQ-03", "mine_id": "MINE-001", "name": "Haul Truck Volvo A45G #1", "equipment_type": "Haul Truck", "status": "Operational", "capacity_tph": 180.0},
    {"id": "EQ-04", "mine_id": "MINE-001", "name": "Haul Truck Volvo A45G #2", "equipment_type": "Haul Truck", "status": "Operational", "capacity_tph": 180.0},
    {"id": "EQ-05", "mine_id": "MINE-001", "name": "Haul Truck CAT 775G #3", "equipment_type": "Haul Truck", "status": "Operational", "capacity_tph": 220.0},
    {"id": "EQ-06", "mine_id": "MINE-001", "name": "Drill Rig Sandvik DR412i #1", "equipment_type": "Drill Rig", "status": "Operational", "capacity_tph": 120.0},
    {"id": "EQ-07", "mine_id": "MINE-001", "name": "Primary Jaw Crusher #1", "equipment_type": "Crusher", "status": "Operational", "capacity_tph": 600.0}
]
df_eq = pd.DataFrame(equipment)
df_eq.to_csv(os.path.join(DATA_DEMO_DIR, 'equipment.csv'), index=False)
df_eq.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'equipment_template.csv'), index=False)

# 7. Operational & Environmental Daily Records (365 days of realistic time-series)
prod_records = []
env_records = []
blasting_events = []
downtimes = []

start_prod_date = datetime(2025, 10, 1) # 1 year of data ending Sep 2026

downtime_id_cnt = 1
blast_id_cnt = 1

for d in range(365):
    curr_d = start_prod_date + timedelta(days=d)
    d_str = curr_d.strftime("%Y-%m-%d")
    
    # Seasonal rainfall pattern (Monsoon: June to September)
    month = curr_d.month
    if month in [6, 7, 8, 9]:
        rainfall = round(max(0.0, np.random.exponential(24.0) if np.random.rand() > 0.3 else 0.0), 1)
    else:
        rainfall = round(max(0.0, np.random.exponential(3.0) if np.random.rand() > 0.8 else 0.0), 1)
        
    soil_m = round(min(1.0, max(0.1, 0.2 + (rainfall / 50.0) + np.random.uniform(-0.05, 0.05))), 3)
    ndvi = round(min(0.85, max(0.15, 0.45 + 0.2 * math.sin(d / 58.0) + np.random.uniform(-0.03, 0.03))), 3)
    lst_c = round(32.0 + 8.0 * math.sin((d - 80) / 58.0) + np.random.uniform(-2.0, 2.0), 1)
    sar_coh = round(max(0.1, min(0.95, 0.8 - (rainfall / 80.0) + np.random.uniform(-0.05, 0.05))), 3)
    
    env_records.append({
        "id": f"ENV-{d+1:04d}",
        "mine_id": "MINE-001",
        "date": d_str,
        "rainfall_mm": rainfall,
        "soil_moisture": soil_m,
        "ndvi": ndvi,
        "land_surface_temp_c": lst_c,
        "sar_coherence": sar_coh
    })
    
    # Production calculation baseline
    target_tonnes = 2500.0  # Daily target for Dongri Buzurg
    
    # Breakdown events impact
    eq_avail_pct = round(np.random.uniform(82.0, 98.0), 1)
    if np.random.rand() < 0.15: # Random breakdown day
        eq_avail_pct -= np.random.uniform(15.0, 35.0)
        eq_avail_pct = round(max(40.0, eq_avail_pct), 1)
        
        # Log downtime record
        eq_affected = random.choice(equipment)
        dt_hrs = round(np.random.uniform(2.5, 9.0), 1)
        downtimes.append({
            "id": f"DT-{downtime_id_cnt:04d}",
            "equipment_id": eq_affected["id"],
            "start_time": f"{d_str} 08:30:00",
            "end_time": f"{d_str} {int(8.5+dt_hrs):02d}:00:00",
            "downtime_hours": dt_hrs,
            "reason": np.random.choice(["Hydraulic Hose Burst", "Engine Overheating", "Track Chain Wear", "Electrical Sensor Fault", "Conveyor Belt Tear"]),
            "category": "Unplanned Maintenance"
        })
        downtime_id_cnt += 1
        
    downtime_hours = round(max(0.0, (100.0 - eq_avail_pct) * 0.16), 1)
    
    # Rain impact on production (flooding, slippery haul roads)
    rain_delay_factor = max(0.0, (rainfall - 15.0) * 0.02)
    
    # Blasting delay
    blasting_delay = 0.0
    if d % 3 == 0: # Blast every 3 days
        blasting_delay = round(np.random.uniform(0.5, 2.0), 1)
        blasting_events.append({
            "id": f"BLST-{blast_id_cnt:04d}",
            "mine_id": "MINE-001",
            "date": d_str,
            "blast_id": f"BLST-DBM-{blast_id_cnt:03d}",
            "location": f"Bench {np.random.choice([100, 120, 140])}m North",
            "powder_factor": round(np.random.uniform(0.42, 0.58), 2),
            "delay_hours": blasting_delay,
            "status": "Completed Successfully"
        })
        blast_id_cnt += 1
        
    operating_hours = max(4.0, round(16.0 - downtime_hours - rain_delay_factor * 8.0 - blasting_delay, 1))
    
    # Actual production derived with realistic correlation
    capacity_rate = 160.0 # Tonnes per operating hour
    actual_tonnes = round(min(target_tonnes * 1.15, operating_hours * capacity_rate * (eq_avail_pct / 95.0) + np.random.normal(0, 75)), 1)
    actual_tonnes = max(200.0, actual_tonnes)
    
    prod_records.append({
        "id": f"PROD-{d+1:04d}",
        "mine_id": "MINE-001",
        "date": d_str,
        "actual_production_tonnes": actual_tonnes,
        "planned_target_tonnes": target_tonnes,
        "operating_hours": operating_hours,
        "downtime_hours": downtime_hours,
        "equipment_availability_pct": eq_avail_pct,
        "rainfall_mm": rainfall,
        "blasting_delay_hours": blasting_delay
    })

df_prod = pd.DataFrame(prod_records)
df_prod.to_csv(os.path.join(DATA_DEMO_DIR, 'production_records.csv'), index=False)
df_prod.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'production_records_template.csv'), index=False)

df_env = pd.DataFrame(env_records)
df_env.to_csv(os.path.join(DATA_DEMO_DIR, 'environmental_observations.csv'), index=False)
df_env.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'environmental_observations_template.csv'), index=False)

df_dt = pd.DataFrame(downtimes)
df_dt.to_csv(os.path.join(DATA_DEMO_DIR, 'equipment_downtime.csv'), index=False)
df_dt.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'equipment_downtime_template.csv'), index=False)

df_blst = pd.DataFrame(blasting_events)
df_blst.to_csv(os.path.join(DATA_DEMO_DIR, 'blasting_events.csv'), index=False)
df_blst.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'blasting_events_template.csv'), index=False)

# 8. Monthly Production Targets
monthly_targets = []
for m in range(12):
    m_date = datetime(2025, 10, 1) + timedelta(days=m*30)
    monthly_targets.append({
        "id": f"TGT-{m+1:02d}",
        "mine_id": "MINE-001",
        "period_start": m_date.strftime("%Y-%m-01"),
        "period_end": (m_date + timedelta(days=28)).strftime("%Y-%m-28"),
        "target_tonnes": 75000.0
    })
df_targets = pd.DataFrame(monthly_targets)
df_targets.to_csv(os.path.join(DATA_DEMO_DIR, 'production_targets.csv'), index=False)

# 9. Mineral Prospectivity GeoJSON Grid (20x20 fine blocks)
prospectivity_features = []
grid_n = 15

for gx in range(grid_n):
    for gy in range(grid_n):
        bx_min = round(mine_lon - dlon + gx * (2*dlon/grid_n), 5)
        bx_max = round(bx_min + (2*dlon/grid_n), 5)
        by_min = round(mine_lat - dlat + gy * (2*dlat/grid_n), 5)
        by_max = round(by_min + (2*dlat/grid_n), 5)
        
        cx = (bx_min + bx_max) / 2
        cy = (by_min + by_max) / 2
        
        # Spatial physics: distance to central manganese strike belt line
        dist_to_fault = abs(cy - (mine_lat + 0.8*(cx - mine_lon)))
        
        # Prospectivity score calculation
        score = max(0.02, min(0.98, 1.0 - (dist_to_fault / 0.015) + np.random.normal(0, 0.08)))
        score = round(score, 3)
        
        if score > 0.70:
            category = "High"
            is_pos_label = 1
        elif score > 0.40:
            category = "Medium"
            is_pos_label = 1 if np.random.rand() > 0.5 else 0
        elif score > 0.20:
            category = "Low"
            is_pos_label = 0
        else:
            category = "Insufficient evidence"
            is_pos_label = 0
            
        prospectivity_features.append({
            "type": "Feature",
            "properties": {
                "block_id": f"PBLK-{gx:02d}-{gy:02d}",
                "mine_id": "MINE-001",
                "center_lat": cy,
                "center_lon": cx,
                "dist_to_fault_km": round(dist_to_fault * 111.0, 2),
                "ndvi": round(0.4 + 0.2 * np.random.rand(), 2),
                "lst_c": round(30.0 + 5.0 * np.random.rand(), 1),
                "sar_coherence": round(0.6 + 0.3 * np.random.rand(), 2),
                "prospectivity_score": score,
                "prospectivity_category": category,
                "synthetic_training_label": is_pos_label
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [bx_min, by_min],
                    [bx_max, by_min],
                    [bx_max, by_max],
                    [bx_min, by_max],
                    [bx_min, by_min]
                ]]
            }
        })

prospectivity_geojson = {
    "type": "FeatureCollection",
    "features": prospectivity_features
}
with open(os.path.join(DATA_DEMO_DIR, 'prospectivity_grid.geojson'), 'w') as f:
    json.dump(prospectivity_geojson, f, indent=2)

print("Demo data generation complete! All CSV and GeoJSON files written successfully.")
