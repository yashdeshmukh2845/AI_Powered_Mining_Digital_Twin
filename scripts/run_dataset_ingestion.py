import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database.db import engine, Base, SessionLocal, ensure_schema_migrations
from backend.app.database.models import (
    Mine, Borehole, BoreholeInterval, AssaySample, ProductionRecord,
    WeatherObservation, SatelliteImageRecord, DataProvenance
)
from backend.app.services.ingestion_service import IngestionService

def run():
    print("=== STARTING INGESTION OF DOWNLOADED DATASETS ===")
    Base.metadata.create_all(bind=engine)
    ensure_schema_migrations()
    db = SessionLocal()
    try:
        # Check if mine exists
        mine = db.query(Mine).filter(Mine.id == "MINE-001").first()
        if not mine:
            mine = Mine(
                id="MINE-001",
                name="Dongri Buzurg Manganese Mine",
                code="DBM-01",
                location="Bhandara District, Maharashtra, India",
                latitude=21.5342,
                longitude=79.6915,
                elevation=320.0,
                operational_status="Active"
            )
            db.add(mine)
            db.commit()

        results = IngestionService.ingest_all(db)
        print("Ingestion results:")
        for k, v in results.items():
            print(f"  {k}: {v}")

        # Summary of records in DB
        prod_cnt = db.query(ProductionRecord).count()
        wth_cnt = db.query(WeatherObservation).count()
        bh_cnt = db.query(Borehole).count()
        int_cnt = db.query(BoreholeInterval).count()
        ass_cnt = db.query(AssaySample).count()
        sat_cnt = db.query(SatelliteImageRecord).count()
        prov_cnt = db.query(DataProvenance).count()

        print("\n=== CURRENT DATABASE TOTALS ===")
        print(f"Production Records: {prod_cnt}")
        print(f"Weather Records: {wth_cnt}")
        print(f"Boreholes: {bh_cnt}")
        print(f"Borehole Intervals: {int_cnt}")
        print(f"Assay Samples: {ass_cnt}")
        print(f"Satellite Sample Previews: {sat_cnt}")
        print(f"Data Provenance Entries: {prov_cnt}")

        # Check sample production record with weather joined
        sample_prod = db.query(ProductionRecord).filter(ProductionRecord.rainfall_mm > 0).first()
        if sample_prod:
            print(f"\nSample Production Record with Joined Weather:")
            print(f"  Date: {sample_prod.date}, Actual: {sample_prod.actual_production_tonnes}t, Target: {sample_prod.planned_target_tonnes}t, Downtime: {sample_prod.downtime_hours}h, Joined Rainfall: {sample_prod.rainfall_mm}mm, Synthetic: {sample_prod.is_synthetic}")
        
        # Check sample borehole
        sample_bh = db.query(Borehole).first()
        if sample_bh:
            print(f"\nSample Borehole Record:")
            print(f"  ID: {sample_bh.borehole_id}, Total Depth: {sample_bh.total_depth}m, Coordinates: ({sample_bh.latitude}, {sample_bh.longitude}), CRS: {sample_bh.crs}, Commodity: {sample_bh.commodity}")

        # Check provenance records
        print("\n=== DATA PROVENANCE ENTRIES ===")
        provs = db.query(DataProvenance).all()
        for p in provs:
            print(f"  [{p.dataset_key}] File: {p.file_name} | Type: {p.dataset_type} | Commodity: {p.commodity} | Rows: {p.accepted_rows}/{p.total_rows} | Origin: {p.data_origin} | Status: {p.status}")

    finally:
        db.close()

if __name__ == "__main__":
    run()
