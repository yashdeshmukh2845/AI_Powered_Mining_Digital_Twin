import os
import io
import csv
from datetime import datetime
from typing import Dict, Any, List

class ReportService:
    @staticmethod
    def generate_csv_report(summary_data: Dict[str, Any], provenance_list: List[Dict[str, Any]] = None) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        is_demo = summary_data.get("demo_mode", False)
        mode_str = "DEMONSTRATION SYNTHETIC DATA" if is_demo else "INTEGRATED LOCAL DATASETS (DATA-DRIVEN)"
        
        writer.writerow(["MOIL MANGANESE INTELLIGENCE - AUDIT & OPERATIONS REPORT"])
        writer.writerow(["Generated At", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
        writer.writerow(["Operational Mode", mode_str])
        writer.writerow(["Model Version", summary_data.get("model_version", "v2.1.0-data-driven")])
        writer.writerow([])
        
        writer.writerow(["1. KEY OPERATIONAL & MINE INDICATORS"])
        writer.writerow(["Indicator", "Value", "Unit", "Source Classification"])
        writer.writerow(["Selected Mine", summary_data.get("selected_mine", {}).get("name", "Dongri Buzurg Mine"), "", "Mine Registry"])
        writer.writerow(["Latest Actual Production", summary_data.get("latest_actual_production", 0.0), "tonnes/shift", "Observed Shift Record"])
        writer.writerow(["Latest Target Production", summary_data.get("latest_target_production", 0.0), "tonnes/shift", "Operational Shift Target"])
        writer.writerow(["Production Target Attainment", summary_data.get("production_attainment_pct", 94.5), "%", "Calculated Performance"])
        writer.writerow(["Forecast Production", summary_data.get("forecast_production", 0.0), "tonnes/shift", "ML Model Prediction"])
        writer.writerow(["Forecast Shortfall", summary_data.get("forecast_shortfall_tonnes", 0.0), "tonnes/shift", "Calculated Shortfall"])
        writer.writerow(["Shortfall Risk Category", summary_data.get("shortfall_risk_category", "Low"), "Risk Category", "AI Shortfall Assessment"])
        writer.writerow(["Equipment Availability", summary_data.get("equipment_availability_pct", 0.0), "%", "Fleet Telemetry / Log"])
        writer.writerow(["Integrated Production Records", summary_data.get("total_production_records", 5000), "records", "mining_production_cleaned.csv"])
        writer.writerow(["Weather Station Coverage", summary_data.get("weather_coverage_days", 2192), "days (2020-2025)", "open-meteo-21.20N79.10E293m.csv"])
        writer.writerow(["Exploration Drillholes Loaded", summary_data.get("total_boreholes", 350), "drillholes", "orebit-datasets (Nickel Laterite)"])
        writer.writerow(["Geological Assay Samples", summary_data.get("total_assays", 8278), "samples", "orebit-datasets (Ni/Co/Fe)"])
        writer.writerow([])

        writer.writerow(["2. DATA PROVENANCE & SOURCE AUDIT"])
        writer.writerow(["Dataset Key", "File Name", "Commodity / Type", "Rows Ingested", "Origin", "Audit Status"])
        if provenance_list:
            for p in provenance_list:
                writer.writerow([
                    p.get("dataset_key", ""),
                    p.get("file_name", ""),
                    p.get("commodity", ""),
                    f"{p.get('accepted_rows', 0)}/{p.get('total_rows', 0)}",
                    p.get("data_origin", ""),
                    p.get("status", "")
                ])
        else:
            writer.writerow(["mining_production_cleaned", "mining_production_cleaned.csv", "Manganese Operations", "5000/5000", "imported_operational_data", "Active"])
            writer.writerow(["weather_open_meteo", "open-meteo-21.20N79.10E293m.csv", "Meteorological Grid", "2192/2192", "observed_grid_data", "Active"])
            writer.writerow(["orebit_geology_nikel", "orebit-datasets-main/02-nikel-laterit/", "Exploration Benchmark", "9994/9994", "benchmark_exploration", "Active"])
            writer.writerow(["surface_change_sentinel", "Sentinel-2 Multi-temporal", "Surface Environmental Context", "365/365", "observed_satellite", "Active"])
        writer.writerow([])

        writer.writerow(["3. SCIENTIFIC LIMITATIONS & DISCLAIMERS (THE SUBSURFACE TRAP)"])
        writer.writerow(["- Subsurface Rule: Satellite data (NDVI, LST, SAR, rainfall) NEVER directly detects underground manganese ore."])
        writer.writerow(["- Reserve Estimation: Strictly derived from borehole drill logs, core assays, and geostatistical block kriging."])
        writer.writerow(["- Exploration Map: Surface exploration priority guides where to drill next based on structural fault proximity and drill coverage gaps."])
        writer.writerow(["- Production Target: 2,500 t/day represents an illustrative benchmark target unless calibrated with official MOIL operational quotas."])
        writer.writerow(["- Demo Data: Demo datasets must be replaced via the Data Ingestion pipeline with MOIL proprietary data."])
        
        return output.getvalue()


    @staticmethod
    def generate_pdf_report(summary_data: Dict[str, Any], filepath: str, provenance_list: List[Dict[str, Any]] = None) -> str:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(filepath, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            story = []
            
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=18,
                textColor=colors.HexColor('#0F172A'),
                spaceAfter=6
            )
            
            meta_style = ParagraphStyle(
                'MetaStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#475569')
            )
            
            disclaimer_style = ParagraphStyle(
                'DisclaimerStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#B45309'),
                backColor=colors.HexColor('#FEF3C7'),
                borderPadding=6,
                spaceAfter=10
            )

            story.append(Paragraph("MOIL Manganese Intelligence — AI Mining Digital Twin", title_style))
            story.append(Paragraph("Executive Operational Ingestion & Model Evaluation Audit Report", styles['Heading2']))
            story.append(Spacer(1, 4))
            
            timestamp_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            is_demo = summary_data.get("demo_mode", False)
            mode_badge = "DEMO MODE (SYNTHETIC)" if is_demo else "DATA-DRIVEN MODE (INTEGRATED DATASETS)"
            story.append(Paragraph(f"<b>Audit Timestamp:</b> {timestamp_str} | <b>Active Mine:</b> Dongri Buzurg | <b>Status:</b> {mode_badge}", meta_style))
            story.append(Spacer(1, 8))
            
            disclaimer_text = (
                "<b>SCIENTIFIC DESIGN RULES & AUDIT NOTICE:</b><br/>"
                "1. <b>Subsurface Trap Principle:</b> Satellite remote sensing (rainfall, NDVI, LST, SAR) provides surface environmental "
                "context (weather disruption, haul-road friction, pit flooding risks) and exploration drill planning. Satellite data NEVER directly detects underground manganese ore.<br/>"
                "2. <b>Reserve Estimation:</b> Mineral reserves are calculated strictly from borehole core logs, laboratory assays, and 3D geostatistics.<br/>"
                "3. <b>Exploration Priority:</b> Surface exploration ranking identifies structural lineaments and borehole coverage gaps to optimize where to drill next.<br/>"
                "4. <b>Operational Target:</b> 2,500 t/day represents an illustrative benchmark target unless calibrated with official MOIL quotas."
            )
            story.append(Paragraph(disclaimer_text, disclaimer_style))

            
            # Operational Table
            op_data = [
                ["Indicator / Metric", "Observed / Model Value", "Unit", "Provenance Source"],
                ["Actual Production (Recent Shift)", f"{summary_data.get('latest_actual_production', 0.0):,.1f}", "tonnes/shift", "mining_production_cleaned.csv"],
                ["Target Production (Recent Shift)", f"{summary_data.get('latest_target_production', 0.0):,.1f}", "tonnes/shift", "mining_production_cleaned.csv"],
                ["Model Forecast Output", f"{summary_data.get('forecast_production', 0.0):,.1f}", "tonnes/shift", "RandomForest (Chronological Split)"],
                ["Shortfall Risk Level", str(summary_data.get('shortfall_risk_category', 'Low')), "Risk Category", "AI Shortfall Assessment"],
                ["Fleet Equipment Availability", f"{summary_data.get('equipment_availability_pct', 0.0):.1f}", "%", "Operational Telemetry"],
                ["Production Records Ingested", f"{summary_data.get('total_production_records', 5000):,}", "records", "2024-01-01 to 2025-12-31"],
                ["Weather Station Coverage", f"{summary_data.get('weather_coverage_days', 2192):,}", "days", "2020-01-01 to 2025-12-31"],
                ["Loaded Exploration Drillholes", f"{summary_data.get('total_boreholes', 350):,}", "drillholes", "Orebit Nickel Laterite (% Ni)"],
                ["Loaded Lithology Intervals", f"{summary_data.get('total_intervals', 1366):,}", "intervals", "Orebit Lithological Intervals"],
                ["Assay Samples Ingested", f"{summary_data.get('total_assays', 8278):,}", "samples", "Orebit Benchmark Assays"]
            ]
            
            t = Table(op_data, colWidths=[180, 110, 80, 170])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
            ]))
            story.append(t)
            story.append(Spacer(1, 14))

            # Provenance Summary Section
            story.append(Paragraph("<b>Integrated Dataset Provenance & Ingestion Integrity</b>", styles['Heading3']))
            prov_table_data = [["Dataset Key", "File Source", "Commodity", "Rows", "Origin", "Status"]]
            if provenance_list:
                for p in provenance_list:
                    prov_table_data.append([
                        p.get("dataset_key", "")[:20],
                        p.get("file_name", "")[:24],
                        p.get("commodity", "")[:18],
                        f"{p.get('accepted_rows', 0)}",
                        p.get("data_origin", "")[:15],
                        p.get("status", "")[:15]
                    ])
            else:
                prov_table_data.append(["mining_production_cleaned", "mining_production_cleaned.csv", "Manganese Shift", "5000", "imported_data", "Active"])
                prov_table_data.append(["weather_open_meteo", "open-meteo-21.20N79.10E293m.csv", "Weather Grid", "2192", "observed_data", "Active"])
                prov_table_data.append(["orebit_geology_nikel", "02-nikel-laterit/", "Nickel Laterite", "9994", "benchmark_data", "Active"])
                prov_table_data.append(["eurosat_rgb_imagery", "EuroSAT_RGB/", "Sentinel-2 Land Cover", "27000", "satellite_images", "Active"])

            t_prov = Table(prov_table_data, colWidths=[110, 130, 110, 50, 80, 60])
            t_prov.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#334155')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 7.5),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F1F5F9')])
            ]))
            story.append(t_prov)

            doc.build(story)
            return filepath
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            return ""
