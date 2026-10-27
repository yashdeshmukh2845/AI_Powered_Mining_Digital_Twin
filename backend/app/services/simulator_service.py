import math
import numpy as np
from typing import Dict, Any, List, Optional

class SimulatorService:
    """
    Mining Digital Twin Simulator & Supply Chain Logistics Engine.
    
    Simulates:
    1. Open-Pit Fleet Interaction (Excavators & Haul Trucks) with rain road friction derating.
    2. Cyclic Truck Queueing & Shovel Match Ratios.
    3. Primary Crusher Circuit Throughput & Choke Bottlenecks.
    4. Bench Blended Stockpile Levels (High Grade >35%, Medium Grade 28-35%, Low Grade <28%).
    5. Indian Railways (BOXN Rake) Rail Logistics Dispatch to Domestic Smelters.
    """

    @staticmethod
    def run_simulation(
        available_excavators: int,
        available_trucks: int,
        equipment_downtime_hours: float,
        blasting_delay_hours: float,
        rainfall_scenario_mm: float,
        planned_operating_hours: float = 16.0,
        production_target_tonnes: float = 2500.0,
        crusher_capacity_tph: float = 450.0,
        rail_rakes_available: int = 1
    ) -> Dict[str, Any]:
        # Capacity physics formulas:
        # Excavator baseline capacity: 350 TPH per excavator
        # Truck baseline capacity: 180 TPH per truck
        effective_excavator_cap = available_excavators * 350.0
        effective_truck_cap = available_trucks * 180.0
        
        # Fleet bottleneck bottlenecked by min of digging or haulage capacity
        fleet_capacity_tph = min(effective_excavator_cap, effective_truck_cap)
        
        # Rain speed reduction penalty
        rain_speed_penalty = max(0.0, (rainfall_scenario_mm - 10.0) * 0.015) if rainfall_scenario_mm > 10.0 else 0.0
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
        
        # Cyclic Queueing Analysis
        ideal_trucks = available_excavators * 2.2
        if available_trucks < ideal_trucks:
            shovel_queue_wait_min = round((ideal_trucks - available_trucks) * 3.4, 1)
            truck_queue_wait_min = 0.5
            queue_bottleneck = "Shovel Starvation (Excavators idle waiting for haul trucks)"
        elif available_trucks > (ideal_trucks * 1.3):
            shovel_queue_wait_min = 0.0
            truck_queue_wait_min = round((available_trucks - ideal_trucks) * 2.8, 1)
            queue_bottleneck = "Truck Bunching (Dumpers queueing at loading face)"
        else:
            shovel_queue_wait_min = 0.8
            truck_queue_wait_min = 1.2
            queue_bottleneck = "Optimal Match (Equilibrium Cycle Flow)"

        # Primary Crusher Feed Circuit
        crusher_operating_hours = net_operating_hours * 0.95
        max_crusher_intake_tonnes = round(crusher_capacity_tph * crusher_operating_hours, 1)
        crushed_ore_tonnes = min(scenario_forecast_tonnes, max_crusher_intake_tonnes)
        crusher_utilization_pct = round((crushed_ore_tonnes / max(1.0, max_crusher_intake_tonnes)) * 100.0, 1)
        crusher_choked = scenario_forecast_tonnes > max_crusher_intake_tonnes

        # Stockpile Inventory Dynamics (Dongri Buzurg ROM & Sized Stockyards)
        # Total daily ROM addition partitioned into grades:
        hi_mn_tonnes = round(crushed_ore_tonnes * 0.35, 1)    # > 35% Mn (Ferro-Alloy grade)
        med_mn_tonnes = round(crushed_ore_tonnes * 0.45, 1)   # 28-35% Mn (Silico-Manganese grade)
        low_mn_tonnes = round(crushed_ore_tonnes * 0.20, 1)   # < 28% Mn (Blast Furnace grade)

        # Rail Dispatch Logistics (Indian Railways BOXN Rakes: ~3,800 tonnes / rake)
        rake_capacity_tonnes = 3800.0
        dispatched_tonnes = round(rail_rakes_available * rake_capacity_tonnes, 1)
        dispatch_deficit_surplus = round(dispatched_tonnes - crushed_ore_tonnes, 1)

        stockpiles = {
            "high_grade_stockpile": {
                "grade_spec": "Mn > 35% (Ferro-Manganese Grade)",
                "current_level_tonnes": round(28400.0 + hi_mn_tonnes - (dispatched_tonnes * 0.4), 1),
                "capacity_tonnes": 50000.0,
                "utilization_pct": round(min(100.0, ((28400.0 + hi_mn_tonnes) / 50000.0) * 100.0), 1),
                "status": "Nominal"
            },
            "medium_grade_stockpile": {
                "grade_spec": "Mn 28% - 35% (Silico-Manganese Grade)",
                "current_level_tonnes": round(41200.0 + med_mn_tonnes - (dispatched_tonnes * 0.45), 1),
                "capacity_tonnes": 65000.0,
                "utilization_pct": round(min(100.0, ((41200.0 + med_mn_tonnes) / 65000.0) * 100.0), 1),
                "status": "Nominal"
            },
            "low_grade_stockpile": {
                "grade_spec": "Mn < 28% (Blast Furnace / Blend Grade)",
                "current_level_tonnes": round(19800.0 + low_mn_tonnes - (dispatched_tonnes * 0.15), 1),
                "capacity_tonnes": 40000.0,
                "utilization_pct": round(min(100.0, ((19800.0 + low_mn_tonnes) / 40000.0) * 100.0), 1),
                "status": "Healthy Buffer"
            }
        }

        # Constraints violated evaluation
        constraints = []
        if available_trucks < math.ceil(available_excavators * 1.5):
            constraints.append("Haul Truck Deficit: Excavators will experience idle queuing waiting for trucks.")
        if net_operating_hours < 8.0:
            constraints.append("Severe Operating Window Reduction: Total effective hours below minimum single shift.")
        if rainfall_scenario_mm > 25.0:
            constraints.append("High Rain Hazard: Haul roads require active dewatering & speed restriction.")
        if crusher_choked:
            constraints.append(f"Crusher Choke Bottleneck: Pit output ({scenario_forecast_tonnes} t) exceeds crusher capacity ({max_crusher_intake_tonnes} t). Surplus diverted to ROM surge pad.")
        if rail_rakes_available == 0:
            constraints.append("Rail Dispatch Lockout: Zero BOXN rakes indented today; stockpile surge accumulation active.")

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
            "constraints_violated": constraints,
            # Logistics & Supply Chain Extensions
            "queueing_physics": {
                "queue_bottleneck": queue_bottleneck,
                "shovel_idle_wait_min_per_hr": shovel_queue_wait_min,
                "truck_queue_wait_min_per_cycle": truck_queue_wait_min,
                "ideal_truck_count": round(ideal_trucks, 1),
                "actual_truck_count": available_trucks
            },
            "crushing_circuit": {
                "crusher_rated_capacity_tph": crusher_capacity_tph,
                "max_crusher_intake_tonnes": max_crusher_intake_tonnes,
                "crushed_ore_tonnes": crushed_ore_tonnes,
                "crusher_utilization_pct": crusher_utilization_pct,
                "is_crusher_bottleneck": crusher_choked
            },
            "stockpiles": stockpiles,
            "rail_dispatch": {
                "rakes_indented_today": rail_rakes_available,
                "wagon_type": "BOXN Heavy Freight (58 Wagons)",
                "total_dispatched_tonnes": dispatched_tonnes,
                "destination_corridors": "Visakhapatnam Steel Plant (RINL) & Bhilai Steel Plant (SAIL)",
                "daily_dispatch_balance_tonnes": dispatch_deficit_surplus,
                "logistics_status": "Rail Clearance Synchronized" if dispatched_tonnes >= scenario_forecast_tonnes else "Stockpile Surge Buffer Absorbing Surplus"
            }
        }
