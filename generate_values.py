#!/usr/bin/env python3
"""
Generate the correct VALUES clause with exactly 70 placeholders
"""

def generate_values_clause(total_placeholders=70, placeholders_per_line=19):
    """Generate VALUES clause with specified number of placeholders"""
    
    lines = []
    remaining = total_placeholders
    
    while remaining > 0:
        if remaining >= placeholders_per_line:
            # Full line
            line = ', '.join(['%s'] * placeholders_per_line) + ','
            lines.append(line)
            remaining -= placeholders_per_line
        else:
            # Partial line
            line = ', '.join(['%s'] * remaining)
            lines.append(line)
            remaining = 0
    
    # Format the output
    result = "            ) VALUES (\n"
    for line in lines:
        result += f"                {line}\n"
    result += "            ) RETURNING id;"
    
    return result

def count_placeholders(values_clause):
    """Count placeholders in the generated clause"""
    return values_clause.count('%s')

# Generate the VALUES clause
values_clause = generate_values_clause(70, 19)
placeholder_count = count_placeholders(values_clause)

print("=== GENERATED VALUES CLAUSE ===")
print()
print(values_clause)
print()
print(f"Total placeholders: {placeholder_count}")
print(f"Expected: 70")
print(f"Match: {'✅' if placeholder_count == 70 else '❌'}")

print()
print("=== COPY THIS TO db_module.py ===")
print("Replace the VALUES section with:")
print()
print(values_clause)
