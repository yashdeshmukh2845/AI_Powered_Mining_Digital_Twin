import math
import numpy as np
from typing import Dict, Any

class SimulatorService:
    @staticmethod
    def run_simulation(
        available_excavators: int,
        available_trucks: int,
        equipment_downtime_hours: float,
        blasting_delay_hours: float,
        rainfall_scenario_mm: float,
        planned_operating_hours: float = 16.0,
        production_target_tonnes: float = 2500.0
    ) -> Dict[str, Any]:
        # Capacity physics formulas:
        # Excavator baseline capacity: 350 TPH per excavator
        # Truck baseline capacity: 180 TPH per truck
        # Fleet matching ratio: 1 excavator requires ~1.5 trucks to maintain continuous loading cycle
        
        effective_excavator_cap = available_excavators * 350.0
        effective_truck_cap = available_trucks * 180.0
        
        # Fleet bottleneck bottlenecked by min of digging or haulage capacity
        fleet_capacity_tph = min(effective_excavator_cap, effective_truck_cap)
        
        # Rain speed reduction penalty
        rain_speed_penalty = max(0.0, (rainfall_scenario_mm - 10.0) * 0.015)
        fleet_capacity_tph = fleet_capacity_tph * (1.0 - rain_speed_penalty)
        
        # Net operating hours after downtime and blasting delay
        net_operating_hours = max(0.0, planned_operating_hours - equipment_downtime_hours - blasting_delay_hours)
        
        # Scenario production calculation
        scenario_forecast_tonnes = round(net_operating_hours * fleet_capacity_tph, 1)
        
        # Baseline simulation parameters (Standard operating baseline: 2 excavators, 3 trucks, 1.5h downtime, 0.5h blast, 0mm rain)
        baseline_net_hours = max(0.0, planned_operating_hours - 1.5 - 0.5)
        baseline_fleet_tph = min(2 * 350.0, 3 * 180.0)
        baseline_forecast_tonnes = round(baseline_net_hours * baseline_fleet_tph, 1)
        
        diff_tonnes = round(scenario_forecast_tonnes - baseline_forecast_tonnes, 1)
        
        # Revised shortfall calculation
        revised_shortfall = max(0.0, production_target_tonnes - scenario_forecast_tonnes)
        revised_shortfall_pct = round((100.0 * revised_shortfall / production_target_tonnes), 2) if production_target_tonnes > 0 else 0.0
        
        if revised_shortfall_pct >= 10.0:
            revised_risk = "High"
        elif revised_shortfall_pct >= 5.0:
            revised_risk = "Medium"
        else:
            revised_risk = "Low"
            
        # Resource allocation summary
        excavator_utilization = round(min(100.0, (fleet_capacity_tph / max(1.0, effective_excavator_cap)) * 100.0), 1)
        truck_utilization = round(min(100.0, (fleet_capacity_tph / max(1.0, effective_truck_cap)) * 100.0), 1)
        
        # Constraints violated evaluation
        constraints = []
        if available_trucks < math.ceil(available_excavators * 1.5):
            constraints.append("Haul Truck Deficit: Excavators will experience idle queuing waiting for trucks.")
        if net_operating_hours < 8.0:
            constraints.append("Severe Operating Window Reduction: Total effective hours below minimum single shift.")
        if rainfall_scenario_mm > 25.0:
            constraints.append("High Rain Hazard: Haul roads require active dewatering & speed restriction.")
            
        return {
            "baseline_forecast_tonnes": baseline_forecast_tonnes,
            "scenario_forecast_tonnes": scenario_forecast_tonnes,
            "difference_tonnes": diff_tonnes,
            "production_target_tonnes": production_target_tonnes,
            "revised_shortfall_tonnes": round(revised_shortfall, 1),
            "revised_shortfall_pct": revised_shortfall_pct,
            "revised_risk_category": revised_risk,
            "fleet_throughput_tph": round(fleet_capacity_tph, 1),
            "net_operating_hours": round(net_operating_hours, 1),
            "excavator_utilization_pct": excavator_utilization,
            "truck_utilization_pct": truck_utilization,
            "constraints_violated": constraints
        }
