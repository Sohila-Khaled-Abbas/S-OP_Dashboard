import os
import re
import glob

# Paths
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES_DIR = os.path.join(WORKSPACE_DIR, "S&OP_Dashboard.SemanticModel", "definition", "tables")
RELATIONSHIPS_FILE = os.path.join(WORKSPACE_DIR, "S&OP_Dashboard.SemanticModel", "definition", "relationships.tmdl")
OUTPUT_FILE = os.path.join(WORKSPACE_DIR, "docs", "data_dictionary.md")

def parse_tmdl_table(filepath):
    """
    Parses a single TMDL file to extract table name, columns, and measures.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    table_name = ""
    columns = []
    measures = []
    
    current_col = None
    current_measure = None
    in_measure_expression = False
    measure_expr_lines = []

    # Get Table Name
    table_match = re.search(r'^table\s+(\w+)', content, re.MULTILINE)
    if table_match:
        table_name = table_match.group(1)
    else:
        return None

    # Parse line by line for structured columns and measures
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())

        # Match Columns
        col_match = re.match(r'^column\s+(\w+)', stripped)
        if col_match:
            if current_col:
                columns.append(current_col)
            current_col = {
                "name": col_match.group(1),
                "dataType": "unknown",
                "sourceColumn": "",
                "summarizeBy": "",
                "description": ""
            }
            current_measure = None
            in_measure_expression = False
            i += 1
            continue

        # Match Measures
        measure_match = re.match(r'^measure\s+([\w\s\'\"\-]+)', stripped)
        if measure_match:
            if current_col:
                columns.append(current_col)
                current_col = None
            if current_measure:
                current_measure["expression"] = "\n".join(measure_expr_lines).strip()
                measures.append(current_measure)
            
            current_measure = {
                "name": measure_match.group(1).strip(),
                "expression": "",
                "description": ""
            }
            measure_expr_lines = []
            in_measure_expression = False
            
            # Check if expression is on the same line or next line
            # In TMDL: measure Name = DAX...
            if "=" in stripped:
                expr_part = stripped.split("=", 1)[1].strip()
                if expr_part:
                    measure_expr_lines.append(expr_part)
                in_measure_expression = True
            
            i += 1
            continue

        # If we are parsing column properties
        if current_col:
            if stripped.startswith("dataType:"):
                current_col["dataType"] = stripped.replace("dataType:", "").strip()
            elif stripped.startswith("sourceColumn:"):
                current_col["sourceColumn"] = stripped.replace("sourceColumn:", "").strip()
            elif stripped.startswith("summarizeBy:"):
                current_col["summarizeBy"] = stripped.replace("summarizeBy:", "").strip()
            elif stripped.startswith("annotation Description ="):
                current_col["description"] = stripped.replace("annotation Description =", "").strip().strip('"')

        # If we are parsing measure properties
        if current_measure:
            if stripped.startswith("annotation Description ="):
                current_measure["description"] = stripped.replace("annotation Description =", "").strip().strip('"')
                in_measure_expression = False
            elif in_measure_expression:
                # If indentation drops back, we are out of the expression
                if indent > 0:
                    measure_expr_lines.append(stripped)
                else:
                    in_measure_expression = False
            elif stripped.startswith("lineageTag:") or stripped.startswith("formatString:"):
                in_measure_expression = False
            elif line.startswith("\t\t") or line.startswith("        "):
                measure_expr_lines.append(stripped)

        i += 1

    # Append remaining
    if current_col:
        columns.append(current_col)
    if current_measure:
        current_measure["expression"] = "\n".join(measure_expr_lines).strip()
        measures.append(current_measure)

    return {
        "table": table_name,
        "columns": columns,
        "measures": measures
    }

def parse_relationships():
    """
    Parses relationships.tmdl to extract model relationships.
    """
    if not os.path.exists(RELATIONSHIPS_FILE):
        return []

    with open(RELATIONSHIPS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by relationship blocks
    blocks = content.split("relationship ")
    relationships = []
    
    for block in blocks[1:]:
        lines = block.split("\n")
        
        from_table = ""
        from_col = ""
        to_table = ""
        to_col = ""
        is_active = True
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("fromColumn:"):
                val = stripped.replace("fromColumn:", "").strip()
                if "." in val:
                    from_table, from_col = val.split(".", 1)
            elif stripped.startswith("toColumn:"):
                val = stripped.replace("toColumn:", "").strip()
                if "." in val:
                    to_table, to_col = val.split(".", 1)
            elif stripped.startswith("isActive:"):
                val = stripped.replace("isActive:", "").strip().lower()
                if val == "false":
                    is_active = False
        
        if from_table and to_table:
            relationships.append({
                "fromTable": from_table,
                "fromColumn": from_col,
                "toTable": to_table,
                "toColumn": to_col,
                "isActive": is_active
            })
            
    return relationships

def generate_markdown():
    """
    Scans tables and relationships and outputs a styled data dictionary markdown.
    """
    tmdl_files = glob.glob(os.path.join(TABLES_DIR, "*.tmdl"))
    model_data = []

    for filepath in tmdl_files:
        parsed = parse_tmdl_table(filepath)
        if parsed:
            model_data.append(parsed)

    relationships = parse_relationships()

    # Sort tables: Dimensions first, then Facts
    model_data.sort(key=lambda x: (0 if x["table"].startswith("Dim") else 1, x["table"]))

    md = []
    md.append("# 📖 Automated Data Dictionary & Model Schema")
    md.append("\n*This document is dynamically generated from the project's TMDL schemas. Do not edit directly.*")
    md.append("\n---\n")

    # Table of Contents
    md.append("## 🗂️ Model Tables")
    for data in model_data:
        table_type = "Dimension" if data["table"].startswith("Dim") else "Fact"
        md.append(f"- **[{data['table']}](#{data['table'].lower()})** ({table_type}) — {len(data['columns'])} Columns, {len(data['measures'])} Measures")

    md.append("\n---\n")

    # Relationships section
    md.append("## 🕸️ Model Relationships")
    md.append("| From Table | From Column | Active Connection | To Table | To Column |")
    md.append("| :--- | :--- | :---: | :--- | :--- |")
    for rel in relationships:
        conn = "`──►`" if rel["isActive"] else "`──(inactive)──►`"
        md.append(f"| `{rel['fromTable']}` | `{rel['fromColumn']}` | {conn} | `{rel['toTable']}` | `{rel['toColumn']}` |")

    md.append("\n---\n")

    # Details per Table
    for data in model_data:
        table_type = "Dimension" if data["table"].startswith("Dim") else "Fact"
        md.append(f"## {data['table']}")
        md.append(f"*Type: `{table_type}`*")
        md.append("\n### Columns")
        md.append("| Column Name | Data Type | Source Field | Summarize By | Description |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        
        for col in data["columns"]:
            desc = col["description"] if col["description"] else "-"
            src = col["sourceColumn"] if col["sourceColumn"] else "-"
            md.append(f"| **`{col['name']}`** | `{col['dataType']}` | `{src}` | `{col['summarizeBy']}` | {desc} |")

        if data["measures"]:
            md.append("\n### Measures")
            md.append("| Measure Name | DAX Expression | Description |")
            md.append("| :--- | :--- | :--- |")
            for m in data["measures"]:
                desc = m["description"] if m["description"] else "-"
                # Format expression in single or multiline block
                expr = m["expression"].replace("\n", " ")
                if len(expr) > 60:
                    expr = f"`{expr[:57]}...`"
                else:
                    expr = f"`{expr}`"
                md.append(f"| **`{m['name']}`** | {expr} | {desc} |")
                
        md.append("\n---\n")

    # Ensure output dir exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(md))
        
    print(f"Data Dictionary successfully updated at {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_markdown()
