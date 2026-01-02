#!/usr/bin/env python3
"""Fix indentation in agent.py"""

import re

with open('src/agent.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_class = False
in_method = False
indent_level = 0
result = []
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Detect class start
    if 'class AIAgent:' in line:
        in_class = True
        result.append(line)
        i += 1
        continue
    
    # Detect method definitions
    if in_class and stripped.startswith('def '):
        result.append('    ' + line.lstrip())
        i += 1
        continue
    
    # Skip empty lines and comments at class level
    if in_class and not stripped:
        result.append(line)
        i += 1
        continue
    
    # Fix indentation for class body (methods and attributes)
    if in_class:
        # If line starts with whitespace, preserve relative indentation
        if line.startswith('    '):
            # Already has some indentation, keep it but ensure it's at least 4 spaces
            result.append(line)
        elif stripped and not stripped.startswith('"""') and not stripped.startswith('#'):
            # Code that needs indentation
            if 'def ' in stripped:
                result.append('    ' + line.lstrip())
            else:
                # Try to detect proper indentation level
                result.append('        ' + line.lstrip())
        else:
            result.append(line)
    else:
        result.append(line)
    
    i += 1

with open('src/agent.py', 'w', encoding='utf-8') as f:
    f.writelines(result)

print("Indentation fix attempted. Please check the file manually.")

