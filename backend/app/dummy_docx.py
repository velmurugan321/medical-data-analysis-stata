"""Utilities for accepting DOCX dummy-table templates.

The statistical engine uses openpyxl internally. This adapter converts the
first Word table into a simple in-memory XLSX workbook before handing it to
the existing, validated table-filling engine. The uploaded DOCX is never
stored in the repository.
"""

import io
from docx import Document
from openpyxl import Workbook


def docx_dummy_to_xlsx(content: bytes) -> bytes:
    """Convert the first non-empty DOCX table to an XLSX byte stream."""
    document = Document(io.BytesIO(content))
    tables = [table for table in document.tables if len(table.rows) and len(table.columns)]
    if not tables:
        raise ValueError("The DOCX dummy table does not contain a readable Word table.")

    table = tables[0]
    wb = Workbook()
    ws = wb.active
    ws.title = "Table 1"

    for r_idx, row in enumerate(table.rows, start=1):
        for c_idx, cell in enumerate(row.cells, start=1):
            # Word merged cells appear more than once; keeping the visible text
            # in the first encountered cell is sufficient for table parsing.
            value = " ".join(line.strip() for line in cell.text.splitlines() if line.strip()).strip()
            ws.cell(r_idx, c_idx).value = value

    # Preserve basic column readability without depending on Word styling.
    for column_cells in ws.columns:
        max_len = max((len(str(cell.value or "")) for cell in column_cells), default=10)
        ws.column_dimensions[column_cells[0].column_letter].width = min(max(max_len + 2, 12), 45)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()
