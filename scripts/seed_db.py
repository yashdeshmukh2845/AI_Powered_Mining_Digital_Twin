import os
import sys
import json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database.db import engine, Base, SessionLocal
from backend.app.database.models import (
    Mine, MineBoundary, GeologicalUnit, Borehole, BoreholeInterval,
    AssaySample, OreBlock, ProductionRecord, ProductionTarget, Equipment,
    EquipmentDowntime, BlastingEvent, EnvironmentalObservation
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DEMO_DIR = os.path.join(BASE_DIR, 'data', 'demo')

def init_and_seed_db():
    print("Initializing database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Mines
        mines_file = os.path.join(DATA_DEMO_DIR, 'mines.csv')
        if os.path.exists(mines_file):
            df = pd.read_csv(mines_file)
            for _, row in df.iterrows():
                db.add(Mine(**row.to_dict()))
                
        # 2. Mine Boundaries
        boundary_file = os.path.join(DATA_DEMO_DIR, 'mine_boundaries.geojson')
        if os.path.exists(boundary_file):
            with open(boundary_file, 'r') as f:
                geojson_content = f.read()
            db.add(MineBoundary(mine_id="MINE-001", boundary_geojson=geojson_content))
            
        # 3. Geological Units
        geo_file = os.path.join(DATA_DEMO_DIR, 'geological_units.csv')
        if os.path.exists(geo_file):
            df = pd.read_csv(geo_file)
            for _, row in df.iterrows():
                db.add(GeologicalUnit(**row.to_dict()))
                
        # 4. Boreholes
        bh_file = os.path.join(DATA_DEMO_DIR, 'boreholes.csv')
        if os.path.exists(bh_file):
            df = pd.read_csv(bh_file)
            for _, row in df.iterrows():
                db.add(Borehole(**row.to_dict()))
                
        # 5. Borehole Intervals
        int_file = os.path.join(DATA_DEMO_DIR, 'borehole_intervals.csv')
        if os.path.exists(int_file):
            df = pd.read_csv(int_file)
            for _, row in df.iterrows():
                db.add(BoreholeInterval(**row.to_dict()))
                
        # 6. Assay Samples
        ass_file = os.path.join(DATA_DEMO_DIR, 'assay_samples.csv')
        if os.path.exists(ass_file):
            df = pd.read_csv(ass_file)
            for _, row in df.iterrows():
                db.add(AssaySample(**row.to_dict()))
                
        # 7. Ore Blocks
        blk_file = os.path.join(DATA_DEMO_DIR, 'ore_blocks.csv')
        if os.path.exists(blk_file):
            df = pd.read_csv(blk_file)
            for _, row in df.iterrows():
                db.add(OreBlock(**row.to_dict()))
                
        # 8. Equipment
        eq_file = os.path.join(DATA_DEMO_DIR, 'equipment.csv')
        if os.path.exists(eq_file):
            df = pd.read_csv(eq_file)
            for _, row in df.iterrows():
                db.add(Equipment(**row.to_dict()))
                
        # 9. Production Records
        prod_file = os.path.join(DATA_DEMO_DIR, 'production_records.csv')
        if os.path.exists(prod_file):
            df = pd.read_csv(prod_file)
            for _, row in df.iterrows():
                db.add(ProductionRecord(**row.to_dict()))
                
        # 10. Environmental Observations
        env_file = os.path.join(DATA_DEMO_DIR, 'environmental_observations.csv')
        if os.path.exists(env_file):
            df = pd.read_csv(env_file)
            for _, row in df.iterrows():
                db.add(EnvironmentalObservation(**row.to_dict()))
                
        # 11. Equipment Downtime
        dt_file = os.path.join(DATA_DEMO_DIR, 'equipment_downtime.csv')
        if os.path.exists(dt_file):
            df = pd.read_csv(dt_file)
            for _, row in df.iterrows():
                db.add(EquipmentDowntime(**row.to_dict()))
                
        # 12. Blasting Events
        blst_file = os.path.join(DATA_DEMO_DIR, 'blasting_events.csv')
        if os.path.exists(blst_file):
            df = pd.read_csv(blst_file)
            for _, row in df.iterrows():
                db.add(BlastingEvent(**row.to_dict()))
                
        # 13. Production Targets
        tgt_file = os.path.join(DATA_DEMO_DIR, 'production_targets.csv')
        if os.path.exists(tgt_file):
            df = pd.read_csv(tgt_file)
            for _, row in df.iterrows():
                db.add(ProductionTarget(**row.to_dict()))
                
        db.commit()
        print("Database seeded successfully with all synthetic demo records!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    init_and_seed_db()
