import os
import json
import pandas as pd
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.database.models import DataImport, Mine, Borehole, BoreholeInterval, AssaySample, OreBlock, ProductionRecord, Equipment, EnvironmentalObservation

class IngestionService:
    REQUIRED_COLUMNS = {
        "mines": ["id", "name", "code", "latitude", "longitude"],
        "boreholes": ["id", "mine_id", "borehole_id", "latitude", "longitude", "elevation", "total_depth"],
        "borehole_intervals": ["id", "borehole_id", "from_depth", "to_depth", "lithology"],
        "assay_samples": ["id", "interval_id", "sample_id", "mn_grade"],
        "ore_blocks": ["id", "mine_id", "block_code", "min_x", "max_x", "min_y", "max_y", "volume_m3", "tonnage", "est_mn_grade"],
        "production_records": ["id", "mine_id", "date", "actual_production_tonnes", "planned_target_tonnes"],
        "equipment": ["id", "mine_id", "name", "equipment_type"],
        "environmental_observations": ["id", "mine_id", "date", "rainfall_mm"]
    }

    @staticmethod
    def preview_dataset(file_path: str, dataset_type: str) -> Dict[str, Any]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
        elif ext == '.geojson':
            with open(file_path, 'r') as f:
                geo_data = json.load(f)
            features = geo_data.get('features', [])
            return {
                "dataset_type": dataset_type,
                "file_type": "GeoJSON",
                "feature_count": len(features),
                "sample_properties": [f.get('properties', {}) for f in features[:5]]
            }
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        columns = list(df.columns)
        req_cols = IngestionService.REQUIRED_COLUMNS.get(dataset_type, [])
        missing_cols = [c for c in req_cols if c not in columns]
        
        preview_records = df.head(5).to_dict(orient='records')
        
        return {
            "dataset_type": dataset_type,
            "total_rows": len(df),
            "columns": columns,
            "missing_required_columns": missing_cols,
            "is_valid": len(missing_cols) == 0,
            "preview_rows": preview_records
        }

    @staticmethod
    def import_csv_dataset(db: Session, file_path: str, dataset_type: str, file_name: str) -> Dict[str, Any]:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(file_path)
        elif ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        req_cols = IngestionService.REQUIRED_COLUMNS.get(dataset_type, [])
        missing_cols = [c for c in req_cols if c not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns for {dataset_type}: {missing_cols}")
            
        total_rows = len(df)
        imported_rows = 0
        rejected_rows = 0
        error_logs = []
        
        model_class_map = {
            "mines": Mine,
            "boreholes": Borehole,
            "borehole_intervals": BoreholeInterval,
            "assay_samples": AssaySample,
            "ore_blocks": OreBlock,
            "production_records": ProductionRecord,
            "equipment": Equipment,
            "environmental_observations": EnvironmentalObservation
        }
        
        TargetModel = model_class_map.get(dataset_type)
        if not TargetModel:
            raise ValueError(f"Unknown dataset type: {dataset_type}")
            
        for idx, row in df.iterrows():
            row_dict = row.to_dict()
            # Basic data sanitation & type parsing validation
            has_nan = any(pd.isna(v) for k, v in row_dict.items() if k in req_cols)
            if has_nan:
                rejected_rows += 1
                error_logs.append(f"Row {idx+1}: Missing required values in essential columns.")
                continue
                
            try:
                # Replace NaNs in optional fields with defaults
                clean_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
                obj = TargetModel(**clean_dict)
                db.merge(obj)
                imported_rows += 1
            except Exception as e:
                rejected_rows += 1
                error_logs.append(f"Row {idx+1}: Parsing/Merge error ({str(e)})")
                
        db.commit()
        
        # Log to data_imports audit table
        import_record = DataImport(
            file_name=file_name,
            dataset_type=dataset_type,
            status="Success" if rejected_rows == 0 else ("Partial" if imported_rows > 0 else "Failed"),
            total_rows=total_rows,
            imported_rows=imported_rows,
            rejected_rows=rejected_rows,
            error_log=json.dumps(error_logs[:50])
        )
        db.add(import_record)
        db.commit()
        
        return {
            "import_id": import_record.id,
            "file_name": file_name,
            "dataset_type": dataset_type,
            "total_rows": total_rows,
            "imported_rows": imported_rows,
            "rejected_rows": rejected_rows,
            "status": import_record.status,
            "errors": error_logs[:10]
        }
