import os
import io
import csv
from datetime import datetime
from typing import Dict, Any

class ReportService:
    @staticmethod
    def generate_csv_report(summary_data: Dict[str, Any]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["MOIL MANGANESE INTELLIGENCE - EXECUTIVE REPORT"])
        writer.writerow(["Generated At", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
        writer.writerow(["Data Source", "MOIL Mining Digital Twin Database (DEMO MODE)"])
        writer.writerow([])
        
        writer.writerow(["KEY PERFORMANCE INDICATOR", "VALUE", "UNIT"])
        writer.writerow(["Selected Mine", summary_data.get("selected_mine", {}).get("name", "Dongri Buzurg Mine"), ""])
        writer.writerow(["Estimated Ore Resources", summary_data.get("est_resources_tonnes", 0.0), "tonnes"])
        writer.writerow(["Estimated Contained Manganese", summary_data.get("est_contained_mn_tonnes", 0.0), "tonnes"])
        writer.writerow(["Average Mn Grade", summary_data.get("avg_mn_grade_pct", 0.0), "%"])
        writer.writerow(["Latest Target Production", summary_data.get("latest_target_production", 0.0), "tonnes/day"])
        writer.writerow(["Latest Actual Production", summary_data.get("latest_actual_production", 0.0), "tonnes/day"])
        writer.writerow(["Forecast Production", summary_data.get("forecast_production", 0.0), "tonnes/day"])
        writer.writerow(["Forecast Shortfall", summary_data.get("forecast_shortfall_tonnes", 0.0), "tonnes/day"])
        writer.writerow(["Shortfall Percentage", summary_data.get("forecast_shortfall_pct", 0.0), "%"])
        writer.writerow(["Shortfall Risk Category", summary_data.get("shortfall_risk_category", "Low"), "Category"])
        writer.writerow(["Equipment Availability", summary_data.get("equipment_availability_pct", 0.0), "%"])
        writer.writerow(["High Prospectivity Ore Blocks", summary_data.get("num_high_prospectivity_blocks", 0), "blocks"])
        writer.writerow([])
        
        writer.writerow(["DEMO MODE NOTICE: Values are synthetic demonstration data and are not official MOIL operational figures."])
        
        return output.getvalue()

    @staticmethod
    def generate_pdf_report(summary_data: Dict[str, Any], filepath: str) -> str:
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',
                fontSize=20,
                textColor=colors.HexColor('#1E293B'),
                spaceAfter=12
            )
            
            story.append(Paragraph("MOIL Manganese Intelligence", title_style))
            story.append(Paragraph("Executive Mining Operations & Prospectivity Report", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            timestamp_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            story.append(Paragraph(f"<b>Generated:</b> {timestamp_str} | <b>Mine:</b> Dongri Buzurg Manganese Mine", styles['Normal']))
            story.append(Paragraph("<b>Notice:</b> DEMO MODE — Values are synthetic and are not official MOIL operational figures.", styles['Italic']))
            story.append(Spacer(1, 15))
            
            table_data = [
                ["Indicator", "Value", "Unit"],
                ["Estimated Ore Resources", f"{summary_data.get('est_resources_tonnes', 0.0):,.1f}", "tonnes"],
                ["Contained Manganese", f"{summary_data.get('est_contained_mn_tonnes', 0.0):,.1f}", "tonnes"],
                ["Average Mn Grade", f"{summary_data.get('avg_mn_grade_pct', 0.0):.2f}", "%"],
                ["Daily Target Production", f"{summary_data.get('latest_target_production', 0.0):,.1f}", "tonnes"],
                ["Forecast Production", f"{summary_data.get('forecast_production', 0.0):,.1f}", "tonnes"],
                ["Forecast Shortfall", f"{summary_data.get('forecast_shortfall_tonnes', 0.0):,.1f}", "tonnes"],
                ["Shortfall Risk Level", str(summary_data.get('shortfall_risk_category', 'Low')), "Risk Category"],
                ["Equipment Availability", f"{summary_data.get('equipment_availability_pct', 0.0):.1f}", "%"]
            ]
            
            t = Table(table_data, colWidths=[200, 150, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
            ]))
            story.append(t)
            
            doc.build(story)
            return filepath
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            return ""
