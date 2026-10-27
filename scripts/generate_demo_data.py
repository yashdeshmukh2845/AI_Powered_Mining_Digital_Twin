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

# 6. Equipment & Equipment Telemetry
equipment = [
    {
        "id": "EQ-01", "mine_id": "MINE-001", "name": "Excavator CAT 390F #1", "equipment_type": "Excavator",
        "status": "Operational", "capacity_tph": 350.0, "engine_hours": 6840.0, "hours_since_last_maintenance": 185.0,
        "past_failure_count_90d": 2, "average_load_pct": 86.0, "health_score": 88.0,
        "failure_risk_24h": 0.09, "failure_risk_48h": 0.16, "failure_risk_72h": 0.24, "critical_component": "Hydraulic Pump"
    },
    {
        "id": "EQ-02", "mine_id": "MINE-001", "name": "Excavator Komatsu PC1250 #2", "equipment_type": "Excavator",
        "status": "Warning", "capacity_tph": 400.0, "engine_hours": 8920.0, "hours_since_last_maintenance": 242.0,
        "past_failure_count_90d": 4, "average_load_pct": 92.0, "health_score": 68.0,
        "failure_risk_24h": 0.28, "failure_risk_48h": 0.42, "failure_risk_72h": 0.58, "critical_component": "Swing Motor & Hydraulics"
    },
    {
        "id": "EQ-03", "mine_id": "MINE-001", "name": "Haul Truck Volvo A45G #1", "equipment_type": "Haul Truck",
        "status": "Operational", "capacity_tph": 180.0, "engine_hours": 4200.0, "hours_since_last_maintenance": 95.0,
        "past_failure_count_90d": 1, "average_load_pct": 80.0, "health_score": 94.0,
        "failure_risk_24h": 0.04, "failure_risk_48h": 0.08, "failure_risk_72h": 0.12, "critical_component": "Transmission"
    },
    {
        "id": "EQ-04", "mine_id": "MINE-001", "name": "Haul Truck Volvo A45G #2", "equipment_type": "Haul Truck",
        "status": "Operational", "capacity_tph": 180.0, "engine_hours": 5150.0, "hours_since_last_maintenance": 140.0,
        "past_failure_count_90d": 2, "average_load_pct": 84.0, "health_score": 89.0,
        "failure_risk_24h": 0.07, "failure_risk_48h": 0.13, "failure_risk_72h": 0.20, "critical_component": "Suspension Struts"
    },
    {
        "id": "EQ-05", "mine_id": "MINE-001", "name": "Haul Truck CAT 775G #3", "equipment_type": "Haul Truck",
        "status": "Operational", "capacity_tph": 220.0, "engine_hours": 3800.0, "hours_since_last_maintenance": 70.0,
        "past_failure_count_90d": 0, "average_load_pct": 78.0, "health_score": 96.0,
        "failure_risk_24h": 0.03, "failure_risk_48h": 0.06, "failure_risk_72h": 0.09, "critical_component": "Braking System"
    },
    {
        "id": "EQ-06", "mine_id": "MINE-001", "name": "Drill Rig Sandvik DR412i #1", "equipment_type": "Drill Rig",
        "status": "Operational", "capacity_tph": 120.0, "engine_hours": 3100.0, "hours_since_last_maintenance": 110.0,
        "past_failure_count_90d": 1, "average_load_pct": 75.0, "health_score": 92.0,
        "failure_risk_24h": 0.05, "failure_risk_48h": 0.10, "failure_risk_72h": 0.15, "critical_component": "Compressor Unit"
    },
    {
        "id": "EQ-07", "mine_id": "MINE-001", "name": "Primary Jaw Crusher #1", "equipment_type": "Crusher",
        "status": "Operational", "capacity_tph": 600.0, "engine_hours": 9400.0, "hours_since_last_maintenance": 160.0,
        "past_failure_count_90d": 2, "average_load_pct": 88.0, "health_score": 85.0,
        "failure_risk_24h": 0.08, "failure_risk_48h": 0.15, "failure_risk_72h": 0.22, "critical_component": "Jaw Toggle Plate"
    }
]
df_eq = pd.DataFrame(equipment)
df_eq.to_csv(os.path.join(DATA_DEMO_DIR, 'equipment.csv'), index=False)
df_eq.head(0).to_csv(os.path.join(DATA_TEMPLATE_DIR, 'equipment_template.csv'), index=False)

# 7. Operational & Environmental Daily Records (365 days of real weather + causal production)
prod_records = []
env_records = []
blasting_events = []
downtimes = []

# Check if real environmental observations already exist (from fetch_satellite_context)
env_path = os.path.join(DATA_DEMO_DIR, 'environmental_observations.csv')
real_env_map = {}
if os.path.exists(env_path):
    try:
        df_real_env = pd.read_csv(env_path)
        for _, row in df_real_env.iterrows():
            real_env_map[str(row['date'])] = row
    except Exception as e:
        print(f"Notice: Using calibrated meteorological generator ({e})")

start_prod_date = datetime(2024, 10, 1)

downtime_id_cnt = 1
blast_id_cnt = 1

for d in range(365):
    curr_d = start_prod_date + timedelta(days=d)
    d_str = curr_d.strftime("%Y-%m-%d")
    
    # Real environmental observation if available, otherwise calibrated monsoon pattern
    if d_str in real_env_map:
        erow = real_env_map[d_str]
        rainfall = float(erow.get('rainfall_mm', 0.0))
        temp_c = float(erow.get('temp_mean_c', 28.0))
        soil_m = float(erow.get('soil_moisture', 0.28))
        ndvi = float(erow.get('ndvi', 0.50))
        lst_c = float(erow.get('land_surface_temp_c', temp_c))
        sar_coh = float(erow.get('sar_coherence', 0.75))
    else:
        month = curr_d.month
        is_monsoon = month in [6, 7, 8, 9]
        rainfall = round(max(0.0, np.random.exponential(24.0) if is_monsoon and np.random.rand() > 0.3 else 0.0), 1)
        temp_c = round(32.0 + 8.0 * math.sin((d - 80) / 58.0) + np.random.uniform(-2.0, 2.0), 1)
        soil_m = round(min(1.0, max(0.1, 0.2 + (rainfall / 50.0) + np.random.uniform(-0.05, 0.05))), 3)
        ndvi = round(min(0.85, max(0.15, 0.45 + 0.2 * math.sin(d / 58.0) + np.random.uniform(-0.03, 0.03))), 3)
        lst_c = temp_c
        sar_coh = round(max(0.1, min(0.95, 0.8 - (rainfall / 80.0) + np.random.uniform(-0.05, 0.05))), 3)
        
    env_records.append({
        "id": f"ENV-{d+1:04d}",
        "mine_id": "MINE-001",
        "date": d_str,
        "rainfall_mm": rainfall,
        "soil_moisture": soil_m,
        "ndvi": ndvi,
        "land_surface_temp_c": lst_c,
        "sar_coherence": sar_coh,
        "data_source": "public_real" if d_str in real_env_map else "synthetic"
    })
    
    # Target Production: Illustrative benchmark (2,500 t/day)
    target_tonnes = 2500.0
    
    # Equipment breakdowns & telemetry evolution
    eq_avail_pct = round(np.random.uniform(84.0, 98.0), 1)
    if np.random.rand() < 0.14: # Failure event
        eq_avail_pct -= np.random.uniform(14.0, 32.0)
        eq_avail_pct = round(max(42.0, eq_avail_pct), 1)
        
        eq_affected = random.choice(equipment)
        dt_hrs = round(np.random.uniform(2.5, 8.5), 1)
        downtimes.append({
            "id": f"DT-{downtime_id_cnt:04d}",
            "equipment_id": eq_affected["id"],
            "start_time": f"{d_str} 08:30:00",
            "end_time": f"{d_str} {int(8.5+dt_hrs):02d}:00:00",
            "downtime_hours": dt_hrs,
            "reason": np.random.choice(["Hydraulic Hose Burst", "Engine Overheating", "Track Chain Wear", "Electrical Sensor Fault", "Conveyor Belt Tear"]),
            "category": "Unplanned Maintenance",
            "failure_component": eq_affected.get("critical_component", "Hydraulics"),
            "engine_hours_at_failure": eq_affected.get("engine_hours", 4500.0) + d * 12.0,
            "hours_since_last_maintenance": round(150.0 + dt_hrs * 10, 1),
            "ambient_temp": temp_c,
            "rainfall_3d_sum": rainfall
        })
        downtime_id_cnt += 1
        
    downtime_hours = round(max(0.0, (100.0 - eq_avail_pct) * 0.16), 1)
    
    # Blasting delay every 3 days
    blasting_delay = 0.0
    if d % 3 == 0:
        blasting_delay = round(np.random.uniform(0.5, 1.8), 1)
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
        
    # DOCUMENTED CAUSAL PHYSICS RULES:
    # 1. Rainfall above 10 mm causes slippery haul roads and speed reduction
    rain_speed_penalty = max(0.0, min(0.50, (rainfall - 10.0) * 0.015)) if rainfall > 10.0 else 0.0
    
    # 2. Net operating hours reduced by downtime, blasting delays, and rain dewatering
    rain_operating_delay = min(4.0, (rainfall / 20.0) * 1.5) if rainfall > 15.0 else 0.0
    operating_hours = max(4.0, round(16.0 - downtime_hours - blasting_delay - rain_operating_delay, 1))
    
    # 3. Fleet throughput rate adjusted for haul road friction penalty
    base_throughput = 160.0 # Nominal t/hr
    effective_throughput = base_throughput * (1.0 - rain_speed_penalty)
    
    # 4. Actual production tonnage
    actual_tonnes = round(operating_hours * effective_throughput * (eq_avail_pct / 95.0) + np.random.normal(0, 45), 1)
    actual_tonnes = max(300.0, min(target_tonnes * 1.15, actual_tonnes))
    
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
        "blasting_delay_hours": blasting_delay,
        "manpower": 25,
        "energy_consumption_kwh": round(2200.0 + operating_hours * 80.0, 1),
        "is_synthetic": True,
        "provenance_source": "causal_synthetic_with_real_weather"
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

# 9. Surface Exploration Priority GeoJSON Grid (15x15 exploration planning blocks)
# NON-NEGOTIABLE DESIGN RULE:
# This grid does NOT detect subterranean manganese ore bodies.
# It ranks surface exploration priority to guide WHERE TO DRILL NEXT based on structural fault proximity
# and borehole coverage gaps.
exploration_features = []
grid_n = 15

# Collect all borehole coordinates to compute exact coverage gaps
bh_coords = [(b["latitude"], b["longitude"]) for b in boreholes]

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
        dist_to_fault_km = round(dist_to_fault * 111.0, 2)
        
        # Compute exact drill coverage gap (distance in meters to nearest borehole)
        cos_lat = math.cos(math.radians(cy))
        min_gap_m = min(
            math.sqrt(((cx - blon) * 111320.0 * cos_lat)**2 + ((cy - blat) * 110540.0)**2)
            for blat, blon in bh_coords
        )
        drill_gap_m = round(min_gap_m, 1)
        
        # Prioritization: High when close to structural lineament AND has a large drill gap (untested zone)
        struct_weight = max(0.05, min(0.98, 1.0 - (dist_to_fault / 0.018)))
        gap_weight = min(1.0, drill_gap_m / 400.0)
        priority_score = round(0.55 * struct_weight + 0.45 * gap_weight, 3)
        
        if drill_gap_m > 300.0:
            gap_cat = "High Gap (>300m - Priority Info Gain)"
        elif drill_gap_m > 150.0:
            gap_cat = "Moderate Gap (150-300m)"
        else:
            gap_cat = "Well Drilled (<150m)"
            
        if priority_score >= 0.70:
            p_cat = "High Priority Drilling"
            is_pos = 1
        elif priority_score >= 0.45:
            p_cat = "Medium Priority"
            is_pos = 1 if priority_score > 0.55 else 0
        elif priority_score >= 0.25:
            p_cat = "Low Priority"
            is_pos = 0
        else:
            p_cat = "Adequately Explored"
            is_pos = 0
            
        exploration_features.append({
            "type": "Feature",
            "properties": {
                "block_id": f"PBLK-{gx:02d}-{gy:02d}",
                "mine_id": "MINE-001",
                "center_lat": cy,
                "center_lon": cx,
                "dist_to_fault_km": dist_to_fault_km,
                "drill_coverage_gap_m": drill_gap_m,
                "drill_gap_category": gap_cat,
                "exploration_priority_score": priority_score,
                "exploration_priority_category": p_cat,
                "prospectivity_score": priority_score, # Backwards compatibility alias
                "prospectivity_category": p_cat,       # Backwards compatibility alias
                "accessibility_score": round(0.85 + 0.1 * np.random.rand(), 2),
                "data_source": "synthetic",
                "disclaimer": "Guides where to drill next. Does not indicate ore at depth. Subsurface reserves require borehole drilling and assay geostatistics."
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

exploration_geojson = {
    "type": "FeatureCollection",
    "disclaimer": "Surface Exploration Priority Map: Guides where to drill next based on structural fault proximity and borehole coverage gaps. Does not indicate ore at depth.",
    "features": exploration_features
}
with open(os.path.join(DATA_DEMO_DIR, 'prospectivity_grid.geojson'), 'w') as f:
    json.dump(exploration_geojson, f, indent=2)

print("Surface exploration priority grid generated successfully with drillhole coverage gaps.")

