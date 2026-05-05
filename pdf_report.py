from __future__ import annotations

import datetime
from typing import Any

from fpdf import FPDF


def generate_pdf(patient: dict[str, Any], risk_result: dict[str, Any], voice_report: dict[str, Any] | None) -> bytes:
    class Report(FPDF):
        def header(self) -> None:
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(192, 57, 43)
            self.cell(0, 10, "HeartLens - Cardiac Risk Report", align="C", new_x="LMARGIN", new_y="NEXT")
            self.set_font("Helvetica", "", 9)
            self.set_text_color(100, 100, 100)
            self.cell(
                0,
                6,
                f"Generated: {datetime.datetime.now().strftime('%d %B %Y %H:%M')} | MVP",
                align="C",
                new_x="LMARGIN",
                new_y="NEXT",
            )
            self.ln(4)

        def footer(self) -> None:
            self.set_y(-14)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 8, "Educational tool only. Not a substitute for clinical evaluation.", align="C")

    pdf = Report()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=14)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(52, 73, 94)
    pdf.cell(0, 8, "Patient Profile", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    for label, value in [
        ("Name", patient.get("name", "Unknown")),
        ("Age", str(patient.get("age", ""))),
        ("Sex", patient.get("sex", "")),
        ("Life Stage", patient.get("life_stage", "")),
        ("Phone", patient.get("phone", "")),
    ]:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(45, 7, f"{label}:")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(52, 73, 94)
    pdf.cell(0, 8, "Risk Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(
        0,
        7,
        f"Risk Score: {risk_result.get('risk_score', 'N/A')}% | {risk_result.get('risk_level', 'Not available')}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(
        0,
        7,
        f"Diagnostic gaps flagged: {risk_result.get('gap_count', 0)} / {risk_result.get('total_biomarkers', 0)}",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(2)

    reference_ranges = risk_result.get("reference_ranges", [])
    if reference_ranges:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(52, 73, 94)
        pdf.cell(0, 8, "Reference Range Findings", new_x="LMARGIN", new_y="NEXT")
        pdf.set_fill_color(52, 73, 94)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(58, 7, "Biomarker", fill=True, border=1)
        pdf.cell(24, 7, "Value", fill=True, border=1)
        pdf.cell(36, 7, "Male", fill=True, border=1)
        pdf.cell(36, 7, "Female", fill=True, border=1)
        pdf.cell(26, 7, "Gap", fill=True, border=1, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        for item in reference_ranges:
            pdf.set_text_color(0, 0, 0)
            pdf.cell(58, 7, str(item.get("metric", "")), border=1)
            pdf.cell(24, 7, f"{item.get('value', '')} {item.get('unit', '')}".strip(), border=1)
            pdf.cell(36, 7, str(item.get("male_status", "")), border=1)
            pdf.cell(36, 7, str(item.get("female_status", "")), border=1)
            pdf.cell(26, 7, "YES" if item.get("gap") else "No", border=1, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    women_advisory = risk_result.get("women_advisory", [])
    if women_advisory:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(52, 73, 94)
        pdf.cell(0, 8, "Women-Specific Advisory", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(0, 0, 0)
        for index, point in enumerate(women_advisory, start=1):
            pdf.multi_cell(0, 6, f"{index}. {point}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    if voice_report:
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(52, 73, 94)
        pdf.cell(0, 8, "AI Screening Call", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, f"Status: {voice_report.get('status', 'unknown')}", new_x="LMARGIN", new_y="NEXT")
        if voice_report.get("red_flags"):
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "Red Flags", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            for flag in voice_report["red_flags"]:
                pdf.multi_cell(0, 6, f"- {flag}", new_x="LMARGIN", new_y="NEXT")
        if voice_report.get("recommendation"):
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 7, "Recommendation", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(0, 6, str(voice_report["recommendation"]), new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())