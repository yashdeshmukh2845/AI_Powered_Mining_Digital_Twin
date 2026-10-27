import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "moil_manganese.db")

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def ensure_schema_migrations():
    """Ensures newly added columns exist in SQLite database without losing data."""
    if not DATABASE_URL.startswith("sqlite"):
        return
    from sqlalchemy import text
    with engine.connect() as conn:
        # Check production_records
        try:
            res = conn.execute(text("PRAGMA table_info(production_records)"))
            existing_cols = {row[1] for row in res.fetchall()}
            prod_additions = [
                ("shift", "TEXT"),
                ("equipment_id", "TEXT"),
                ("manpower", "INTEGER"),
                ("energy_consumption_kwh", "REAL"),
                ("production_efficiency_pct", "REAL"),
                ("is_synthetic", "BOOLEAN DEFAULT 0"),
                ("provenance_source", "TEXT DEFAULT 'imported'")
            ]
            for col_name, col_type in prod_additions:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE production_records ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
        except Exception:
            pass

        # Check boreholes
        try:
            res = conn.execute(text("PRAGMA table_info(boreholes)"))
            existing_cols = {row[1] for row in res.fetchall()}
            bh_additions = [
                ("x_coord", "REAL"),
                ("y_coord", "REAL"),
                ("crs", "TEXT DEFAULT 'UTM'"),
                ("commodity", "TEXT DEFAULT 'Nickel Laterite'"),
                ("is_synthetic", "BOOLEAN DEFAULT 0"),
                ("provenance_source", "TEXT DEFAULT 'orebit-datasets'")
            ]
            for col_name, col_type in bh_additions:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE boreholes ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
        except Exception:
            pass

        # Check borehole_intervals
        try:
            res = conn.execute(text("PRAGMA table_info(borehole_intervals)"))
            existing_cols = {row[1] for row in res.fetchall()}
            bi_additions = [
                ("primary_grade", "REAL DEFAULT 0.0"),
                ("primary_commodity", "TEXT DEFAULT 'Ni'"),
                ("secondary_grade", "REAL DEFAULT 0.0"),
                ("secondary_commodity", "TEXT DEFAULT 'Fe'")
            ]
            for col_name, col_type in bi_additions:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE borehole_intervals ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
        except Exception:
            pass

        # Check assay_samples
        try:
            res = conn.execute(text("PRAGMA table_info(assay_samples)"))
            existing_cols = {row[1] for row in res.fetchall()}
            ass_additions = [
                ("primary_grade", "REAL DEFAULT 0.0"),
                ("primary_element", "TEXT DEFAULT 'Ni'"),
                ("specific_gravity", "REAL DEFAULT 1.6"),
                ("commodity", "TEXT DEFAULT 'Nickel Laterite'"),
                ("provenance_source", "TEXT DEFAULT 'orebit-datasets'")
            ]
            for col_name, col_type in ass_additions:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE assay_samples ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
        except Exception:
            pass

        # Check ore_blocks
        try:
            res = conn.execute(text("PRAGMA table_info(ore_blocks)"))
            existing_cols = {row[1] for row in res.fetchall()}
            if "is_synthetic" not in existing_cols:
                conn.execute(text("ALTER TABLE ore_blocks ADD COLUMN is_synthetic BOOLEAN DEFAULT 0"))
                conn.commit()
        except Exception:
            pass

        # Check equipment
        try:
            res = conn.execute(text("PRAGMA table_info(equipment)"))
            existing_cols = {row[1] for row in res.fetchall()}
            eq_additions = [
                ("engine_hours", "REAL DEFAULT 4500.0"),
                ("hours_since_last_maintenance", "REAL DEFAULT 120.0"),
                ("past_failure_count_90d", "INTEGER DEFAULT 1"),
                ("average_load_pct", "REAL DEFAULT 82.0"),
                ("health_score", "REAL DEFAULT 90.0"),
                ("failure_risk_24h", "REAL DEFAULT 0.08"),
                ("failure_risk_48h", "REAL DEFAULT 0.14"),
                ("failure_risk_72h", "REAL DEFAULT 0.22"),
                ("critical_component", "TEXT DEFAULT 'Hydraulic System'")
            ]
            for col_name, col_type in eq_additions:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE equipment ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
        except Exception:
            pass

        # Check equipment_downtime
        try:
            res = conn.execute(text("PRAGMA table_info(equipment_downtime)"))
            existing_cols = {row[1] for row in res.fetchall()}
            dt_additions = [
                ("failure_component", "TEXT DEFAULT 'Hydraulic Hose'"),
                ("engine_hours_at_failure", "REAL DEFAULT 4200.0"),
                ("hours_since_last_maintenance", "REAL DEFAULT 240.0"),
                ("ambient_temp", "REAL DEFAULT 32.0"),
                ("rainfall_3d_sum", "REAL DEFAULT 15.0")
            ]
            for col_name, col_type in dt_additions:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE equipment_downtime ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
        except Exception:
            pass

        # Check environmental_observations
        try:

            res = conn.execute(text("PRAGMA table_info(environmental_observations)"))
            existing_cols = {row[1] for row in res.fetchall()}
            if "data_source" not in existing_cols:
                conn.execute(text("ALTER TABLE environmental_observations ADD COLUMN data_source TEXT DEFAULT 'public_real'"))
                conn.commit()
        except Exception:
            pass



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
