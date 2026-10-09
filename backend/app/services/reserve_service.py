import math
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.models import Borehole, BoreholeInterval, AssaySample, OreBlock

class ReserveService:
    @staticmethod
    def estimate_reserves(db: Session, mine_id: str = "MINE-001", bulk_density: float = 3.4, cutoff_grade: float = 15.0) -> Dict[str, Any]:
        blocks = db.query(OreBlock).filter(OreBlock.mine_id == mine_id).all()
        
        total_volume_m3 = 0.0
        total_tonnage = 0.0
        total_contained_mn = 0.0
        
        categories_breakdown = {
            "Measured": {"tonnage": 0.0, "contained_mn": 0.0, "avg_grade": 0.0, "count": 0},
            "Indicated": {"tonnage": 0.0, "contained_mn": 0.0, "avg_grade": 0.0, "count": 0},
            "Inferred": {"tonnage": 0.0, "contained_mn": 0.0, "avg_grade": 0.0, "count": 0},
            "Exploration Target": {"tonnage": 0.0, "contained_mn": 0.0, "avg_grade": 0.0, "count": 0}
        }
        
        block_details = []
        for b in blocks:
            vol = b.volume_m3
            tonnes = vol * bulk_density
            grade = b.est_mn_grade
            # Calculation: Contained manganese tonnes = Ore tonnage * Grade percentage / 100
            contained_mn = (tonnes * grade / 100.0) if grade >= cutoff_grade else 0.0
            
            total_volume_m3 += vol
            total_tonnage += tonnes
            total_contained_mn += contained_mn
            
            cat = b.category if b.category in categories_breakdown else "Inferred"
            categories_breakdown[cat]["tonnage"] += tonnes
            categories_breakdown[cat]["contained_mn"] += contained_mn
            categories_breakdown[cat]["count"] += 1
            
            block_details.append({
                "block_id": b.id,
                "block_code": b.block_code,
                "volume_m3": vol,
                "bulk_density": bulk_density,
                "tonnage_tonnes": round(tonnes, 2),
                "est_mn_grade_pct": round(grade, 2),
                "contained_mn_tonnes": round(contained_mn, 2),
                "category": cat
            })
            
        for cat in categories_breakdown:
            t = categories_breakdown[cat]["tonnage"]
            mn = categories_breakdown[cat]["contained_mn"]
            categories_breakdown[cat]["avg_grade"] = round((mn / t * 100.0), 2) if t > 0 else 0.0
            categories_breakdown[cat]["tonnage"] = round(t, 2)
            categories_breakdown[cat]["contained_mn"] = round(mn, 2)
            
        avg_grade = round((total_contained_mn / total_tonnage * 100.0), 2) if total_tonnage > 0 else 0.0
        
        return {
            "mine_id": mine_id,
            "cutoff_grade_pct": cutoff_grade,
            "bulk_density_t_per_m3": bulk_density,
            "total_volume_m3": round(total_volume_m3, 2),
            "total_ore_tonnage": round(total_tonnage, 2),
            "total_contained_mn_tonnes": round(total_contained_mn, 2),
            "average_mn_grade_pct": avg_grade,
            "categories": categories_breakdown,
            "blocks_count": len(blocks),
            "block_samples": block_details[:10]
        }
