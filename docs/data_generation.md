# Data Generation & Causal Operational Physics Methodology

## 1. Overview & Non-Negotiable Scientific Principles

In accordance with strict mining data integrity rules:
1. **The Subsurface Trap Principle**: Space-borne remote sensing data (precipitation, soil moisture, NDVI, LST, SAR coherence) tracks **surface environmental context only** (weather disruption, haul road friction, pit flooding risks). **Satellite data does NOT detect subterranean manganese ore.** Subsurface reserves require borehole drill cores, physical chemical assays, and 3D geostatistical kriging.
2. **Transparent Provenance**: All synthetic demo data is explicitly tagged `data_source: "synthetic"`, while satellite meteorological observations fetched from NASA POWER / Open-Meteo are tagged `data_source: "public_real"`.

---

## 2. Real Environmental Ingestion (NASA POWER & Open-Meteo)

Daily meteorological data for Dongri Buzurg Mine ($21.5342^\circ\text{ N}, 79.6915^\circ\text{ E}$, Bhandara District, Maharashtra, India) is fetched via `scripts/fetch_satellite_context.py`:
- **Precipitation**: Daily rainfall sum ($\text{mm}$) capturing central India's monsoon (June to September).
- **Temperature**: Mean, maximum, and minimum ambient temperatures ($^\circ\text{C}$).
- **Soil Moisture**: Surface layer ($0\text{--}7\text{ cm}$) saturation index ($\text{m}^3/\text{m}^3$).
- **Multi-Spectral Surface Indices**:
  - Normalized Difference Vegetation Index (NDVI) tracking environmental buffer canopy.
  - Land Surface Temperature (LST).
  - Sentinel-1 SAR Coherence tracking ground stability.

---

## 3. Causal Operational Physics Rules

Unlike naive synthetic datasets that insert arbitrary random numbers, the 365-day operational records are governed by explicit, documented causal engineering equations:

### 3.1 Haul Road Friction & Rain Speed Penalty
When daily precipitation exceeds $10\text{ mm}$, haul roads experience surface slipping and mud accumulation:
$$\text{Rain Speed Penalty} = \min\left(0.50, (\text{Rainfall} - 10.0) \times 0.015\right) \quad \text{for } \text{Rainfall} > 10\text{ mm}$$
This directly penalizes haul truck round-trip cycle speeds by up to $50\%$.

### 3.2 Rain Dewatering Operating Window Reduction
Heavy rain ($>15\text{ mm}$) requires temporary ramp clearance and active sump dewatering before haul trucks can descend to deep benches:
$$\text{Rain Delay Hours} = \min\left(4.0, \frac{\text{Rainfall}}{20.0} \times 1.5\right) \quad \text{for } \text{Rainfall} > 15\text{ mm}$$

### 3.3 Net Productive Operating Hours
$$\text{Net Operating Hours} = \max\left(4.0, 16.0 - \text{Downtime Hours} - \text{Blasting Delays} - \text{Rain Delay Hours}\right)$$

### 3.4 Effective Fleet Throughput & Realized Production
$$\text{Effective Throughput Rate (TPH)} = \text{Base Throughput } (160\text{ TPH}) \times (1.0 - \text{Rain Speed Penalty})$$
$$\text{Actual Production (Tonnes)} = \text{Net Operating Hours} \times \text{Effective Throughput} \times \left(\frac{\text{Equipment Availability } \%}{95.0}\right) + \epsilon$$
where $\epsilon \sim \mathcal{N}(0, 45\text{ tonnes})$ models residual cycle time noise.

---

## 4. Equipment Telemetry & Failure Dynamics

Seven core heavy mining machines are monitored:
- **CAT 390F Excavator #1** (350 TPH)
- **Komatsu PC1250 Excavator #2** (400 TPH)
- **Volvo A45G Articulated Hauler #1** (180 TPH)
- **Volvo A45G Articulated Hauler #2** (180 TPH)
- **CAT 775G Rigid Dump Truck #3** (220 TPH)
- **Sandvik DR412i Rotary Blast-Hole Drill #1** (120 TPH)
- **Primary Jaw Crusher #1** (600 TPH)

Machine failure probability within 24h, 48h, and 72h is driven causally by:
1. `hours_since_last_maintenance` relative to standard 250-hour service cycle.
2. `average_load_pct` (engine overload stress).
3. `ambient_temp` ($>38^\circ\text{C}$ creates hydraulic fluid overheating).
4. `rainfall_3d_sum` (water ingestion and undercarriage track wear).
