#!/usr/bin/env python3
"""Fix indentation in agent.py"""

import re

with open('src/agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into lines
lines = content.split('\n')
result = []
in_class = False
in_method = False
indent_stack = [0]  # Track indentation levels
i = 0

while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    # Track class definition
    if 'class AIAgent:' in line:
        in_class = True
        result.append(line)
        indent_stack = [0, 4]  # Class level, method level
        i += 1
        continue
    
    # Track method definitions
    if in_class and stripped.startswith('def '):
        result.append('    ' + line.lstrip())
        indent_stack = [0, 4, 8]  # Class, method, block
        i += 1
        continue
    
    # Skip empty lines
    if not stripped:
        result.append('')
        i += 1
        continue
    
    # Handle indentation
    if in_class:
        # If line already has proper indentation (starts with spaces), preserve relative
        if line.startswith('    '):
            # Check if it's a method definition
            if stripped.startswith('def '):
                result.append('    ' + line.lstrip())
            elif line.startswith('        '):
                # Already has method-level indentation
                result.append(line)
            else:
                # Has some indentation but might need more
                result.append('        ' + line.lstrip())
        elif stripped.startswith('#'):
            # Comments - try to match surrounding indentation
            if result and result[-1].strip():
                last_indent = len(result[-1]) - len(result[-1].lstrip())
                result.append(' ' * last_indent + stripped)
            else:
                result.append('        ' + stripped)
        elif stripped.startswith('"""') or stripped.startswith("'''"):
            # Docstrings
            if result and 'def ' in result[-1]:
                result.append('        ' + stripped)
            else:
                result.append('    ' + stripped)
        else:
            # Code that needs indentation
            # Check context to determine proper indentation
            if any(keyword in stripped for keyword in ['if ', 'try:', 'except', 'for ', 'while ', 'else:', 'elif ']):
                # Control flow - needs proper indentation
                if result and any(kw in result[-1] for kw in ['if ', 'try:', 'for ', 'while ', 'def ']):
                    result.append('            ' + stripped)
                else:
                    result.append('        ' + stripped)
            else:
                # Regular code
                result.append('        ' + stripped)
    else:
        result.append(line)
    
    i += 1

# Write back
with open('src/agent.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(result))

print("Indentation fix attempted. Please verify the file.")

