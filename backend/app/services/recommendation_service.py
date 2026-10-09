import os
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.database.models import Recommendation, Forecast

class RecommendationService:
    @staticmethod
    def generate_recommendations(db: Session, shortfall_tonnes: float, eq_avail_pct: float, rainfall_mm: float, blasting_delay_hrs: float) -> List[Dict[str, Any]]:
        recommendations = []
        
        # Recommendation 1: Reallocate excavators/trucks
        if eq_avail_pct < 88.0:
            recommendations.append({
                "id": "REC-001",
                "priority": "High",
                "title": "Deploy Standby Haul Truck Fleet & Rapid Hydraulic Repair",
                "description": "Equipment availability is currently below operational threshold (88%). Deploy standby Volvo A45G truck #2 to Bench 120m to compensate for excavator capacity loss.",
                "rationale": "Restores effective haulage capacity by 180 TPH and mitigates planned shortfall.",
                "affected_block_or_mine": "Dongri Buzurg Mine - Bench 120m",
                "est_production_impact_tonnes": round(min(shortfall_tonnes * 0.45, 320.0), 1),
                "constraints_assumptions": "Requires 1 available certified operator for standby shift.",
                "responsible_team": "Heavy Equipment & Fleet Ops",
                "status": "Pending Review"
            })
            
        # Recommendation 2: Adjust extraction priorities
        if shortfall_tonnes > 150.0:
            recommendations.append({
                "id": "REC-002",
                "priority": "High",
                "title": "Prioritize High-Grade Manganese Gondite Block BLK-004",
                "description": "Shift active excavation focus from low-grade perimeter to High-Grade Gondite Ore Block BLK-004 (41.2% Mn grade).",
                "rationale": "Maximizes contained manganese recovery per excavator hour.",
                "affected_block_or_mine": "Block BLK-004",
                "est_production_impact_tonnes": round(min(shortfall_tonnes * 0.35, 280.0), 1),
                "constraints_assumptions": "Assumes pit access ramp is clear of water accumulation.",
                "responsible_team": "Mine Planning & Geology Team",
                "status": "Pending Review"
            })
            
        # Recommendation 3: Weather contingency plan
        if rainfall_mm > 10.0:
            recommendations.append({
                "id": "REC-003",
                "priority": "Medium",
                "title": "Activate Pit Sump Dewatering & Gravel Haul Road Dressing",
                "description": "Heavy rainfall detected (15+ mm). Activate high-head dewatering pump #2 at lower pit bench and dress slippery haul roads with coarse quartzite aggregate.",
                "rationale": "Prevents haul truck speed reduction from 25 km/h to 10 km/h.",
                "affected_block_or_mine": "Pit South Ramp",
                "est_production_impact_tonnes": round(min(shortfall_tonnes * 0.25, 210.0), 1),
                "constraints_assumptions": "Requires dewatering pump fuel line check.",
                "responsible_team": "Civil & Mine Drainage Ops",
                "status": "Pending Review"
            })
            
        # Recommendation 4: Blasting schedule optimization
        if blasting_delay_hrs > 0.5:
            recommendations.append({
                "id": "REC-004",
                "priority": "Low",
                "title": "Reschedule Shift-Change Blasting to Off-Peak Window",
                "description": "Shift production pit blasting from 12:00 PM peak shift change to 06:30 AM early morning clearance window.",
                "rationale": "Eliminates 1.5 hours of idle excavator wait time during primary shift hours.",
                "affected_block_or_mine": "Bench 140m North",
                "est_production_impact_tonnes": round(min(shortfall_tonnes * 0.20, 150.0), 1),
                "constraints_assumptions": "Must comply with DGMS safety clearance protocol.",
                "responsible_team": "Blasting & Explosives Safety",
                "status": "Pending Review"
            })
            
        if not recommendations: # Default fallback recommendation if shortfall is negligible
            recommendations.append({
                "id": "REC-005",
                "priority": "Low",
                "title": "Maintain Preventive Maintenance Schedule & Ramp Stockpiling",
                "description": "Production target is on track. Maintain standard 250-hour scheduled service for CAT 390F Excavator #1.",
                "rationale": "Sustains equipment availability above 92%.",
                "affected_block_or_mine": "Primary Crusher Feed Stockpile",
                "est_production_impact_tonnes": 50.0,
                "constraints_assumptions": "No immediate bottlenecks identified.",
                "responsible_team": "Maintenance & Engineering",
                "status": "Approved"
            })
            
        return recommendations
