#!/usr/bin/env python3
"""
Extract and analyze code blocks from the document.
Identifies code blocks with their section headings for validation.
"""

import re
import sys
from collections import defaultdict

def extract_code_blocks_with_headers(filepath):
    """Extract all code blocks with their section headings."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Find all headings (##, ###, ####, etc.)
    headings = []
    current_heading_stack = []
    
    code_blocks = []
    in_code_block = False
    code_block_start = None
    code_block_language = None
    code_block_lines = []
    code_block_heading = None
    
    for i, line in enumerate(lines, 1):
        # Track headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            
            # Maintain heading stack
            while current_heading_stack and len(current_heading_stack[-1][0]) >= level:
                current_heading_stack.pop()
            current_heading_stack.append((heading_match.group(1), text))
        
        # Track code blocks
        if line.startswith('```'):
            if in_code_block:
                # End of code block
                code_blocks.append({
                    'start_line': code_block_start,
                    'end_line': i,
                    'language': code_block_language,
                    'content': '\n'.join(code_block_lines),
                    'line_count': len(code_block_lines),
                    'heading_path': ' > '.join([h[1] for h in current_heading_stack]) if current_heading_stack else 'No heading',
                    'section_heading': current_heading_stack[-1][1] if current_heading_stack else 'No heading'
                })
                in_code_block = False
                code_block_lines = []
            else:
                # Start of code block
                in_code_block = True
                code_block_start = i
                code_block_language = line[3:].strip() or 'plain'
                if code_block_language:
                    code_block_heading = current_heading_stack[-1][1] if current_heading_stack else 'No heading'
        elif in_code_block:
            code_block_lines.append(line)
    
    return code_blocks

def analyze_code_block(block):
    """Analyze a code block for code smells and issues."""
    issues = []
    content = block['content']
    lines = content.split('\n')
    
    # Check for Python code blocks specifically
    if block['language'] == 'python':
        # Extract function definitions
        functions = []
        current_function = None
        current_function_start = None
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            # Find function/class definitions
            func_match = re.match(r'^(\s*)(def|class)\s+(\w+)', line)
            if func_match:
                if current_function:
                    # Save previous function
                    functions.append({
                        'name': current_function['name'],
                        'start': current_function_start,
                        'end': i - 1,
                        'line_count': i - current_function_start,
                        'indent': current_function['indent']
                    })
                
                current_function = {
                    'name': func_match.group(3),
                    'type': func_match.group(2),
                    'indent': len(func_match.group(1))
                }
                current_function_start = i
            
            # Check for docstrings
            if current_function and '"""' in line:
                if current_function.get('has_docstring'):
                    # End of docstring
                    pass
                else:
                    current_function['has_docstring'] = True
        
        # Don't forget last function
        if current_function:
            functions.append({
                'name': current_function['name'],
                'start': current_function_start,
                'end': len(lines),
                'line_count': len(lines) - current_function_start + 1,
                'indent': current_function['indent']
            })
        
        # Analyze functions
        for func in functions:
            # Check function length (smell if > 50 lines)
            if func['line_count'] > 50:
                issues.append({
                    'type': 'long_function',
                    'severity': 'medium',
                    'message': f"Function '{func['name']}' is {func['line_count']} lines long (consider refactoring if > 50 lines)",
                    'location': f"lines {func['start']}-{func['end']}"
                })
            
            # Check for docstrings (should have one)
            func_content = '\n'.join(lines[func['start']-1:func['end']])
            if 'def ' in func_content and '"""' not in func_content[:200]:
                issues.append({
                    'type': 'missing_docstring',
                    'severity': 'low',
                    'message': f"Function '{func['name']}' is missing a docstring",
                    'location': f"line {func['start']}"
                })
        
        # Check for comments
        comment_lines = sum(1 for line in lines if line.strip().startswith('#') or '"""' in line or "'''" in line)
        total_lines = len([l for l in lines if l.strip()])
        comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
        
        if comment_ratio < 0.1 and len(lines) > 10:
            issues.append({
                'type': 'low_comment_ratio',
                'severity': 'low',
                'message': f"Low comment ratio ({comment_ratio:.1%}), code may benefit from more explanatory comments",
                'location': 'throughout'
            })
        
        # Check for obvious bugs or anti-patterns
        full_content = '\n'.join(lines)
        
        # Check for undefined variables (common issues)
        if 'calculate_burn_rate_for_window' in full_content and 'def calculate_burn_rate_for_window' not in full_content:
            issues.append({
                'type': 'undefined_method',
                'severity': 'high',
                'message': "Method 'calculate_burn_rate_for_window' is called but not defined in this class",
                'location': 'see calls to calculate_burn_rate_for_window'
            })
        
        if 'get_threshold' in full_content and 'def get_threshold' not in full_content:
            issues.append({
                'type': 'undefined_method',
                'severity': 'high',
                'message': "Method 'get_threshold' is called but not defined in this class",
                'location': 'see calls to get_threshold'
            })
        
        # Check for undefined imports
        if 'statistics.' in full_content and 'import statistics' not in full_content:
            issues.append({
                'type': 'missing_import',
                'severity': 'medium',
                'message': "Uses 'statistics' module but doesn't import it",
                'location': 'throughout'
            })
        
        # Check for division by zero potential
        if '/' in full_content and 'if.*== 0' not in full_content:
            # Check if there's division without zero checks
            if re.search(r'/\s*\w+', full_content) and not re.search(r'if.*==\s*0|if.*!=.*0|if\s+\w+\s*:', full_content):
                # This is a weak check, but flag for review
                pass
    
    # Check for very long code blocks (could indicate need for refactoring)
    if block['line_count'] > 100:
        issues.append({
            'type': 'long_code_block',
            'severity': 'medium',
            'message': f"Code block is {block['line_count']} lines long (consider breaking into smaller, more focused examples)",
            'location': f"lines {block['start_line']}-{block['end_line']}"
        })
    
    return issues

def main():
    filepath = '/Users/geoffwhite/Documents/SLOBlackSwan-Cursor/input/SLOBLACKSWAN-v0.44.md'
    
    print("Extracting code blocks...")
    blocks = extract_code_blocks_with_headers(filepath)
    
    print(f"Found {len(blocks)} code blocks\n")
    
    # Analyze each block
    all_issues = []
    blocks_with_issues = []
    
    for block in blocks:
        issues = analyze_code_block(block)
        if issues:
            blocks_with_issues.append((block, issues))
            all_issues.extend([(block, issue) for issue in issues])
    
    # Output results
    print("=" * 80)
    print("CODE BLOCK VALIDATION REPORT")
    print("=" * 80)
    print(f"\nTotal code blocks: {len(blocks)}")
    print(f"Blocks with issues: {len(blocks_with_issues)}")
    print(f"Total issues found: {len(all_issues)}\n")
    
    # Group by heading
    by_heading = defaultdict(list)
    for block, issues in blocks_with_issues:
        by_heading[block['section_heading']].append((block, issues))
    
    print("=" * 80)
    print("ISSUES BY SECTION")
    print("=" * 80)
    
    for heading, block_issues in sorted(by_heading.items()):
        print(f"\n## {heading}")
        print("-" * 80)
        
        for block, issues in block_issues:
            print(f"\n**Code Block** (lines {block['start_line']}-{block['end_line']}, {block['language']}, {block['line_count']} lines)")
            print(f"**Full Path:** {block['heading_path']}")
            
            for issue in issues:
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(issue['severity'], '⚪')
                print(f"  {severity_icon} [{issue['severity'].upper()}] {issue['type']}")
                print(f"     {issue['message']}")
                print(f"     Location: {issue['location']}")
            print()
    
    # Summary of code smells
    print("=" * 80)
    print("CODE SMELLS SUMMARY")
    print("=" * 80)
    
    smell_counts = defaultdict(int)
    for block, issues in blocks_with_issues:
        for issue in issues:
            smell_counts[issue['type']] += 1
    
    for smell_type, count in sorted(smell_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{smell_type}: {count}")
    
    # List all blocks that need refactoring
    print("\n" + "=" * 80)
    print("CODE BLOCKS REQUIRING REFACTORING")
    print("=" * 80)
    
    refactor_needed = []
    for block, issues in blocks_with_issues:
        # High severity or multiple issues = needs refactoring
        high_severity = any(i['severity'] == 'high' for i in issues)
        multiple_issues = len(issues) >= 2
        
        if high_severity or multiple_issues or any(i['type'] in ['long_function', 'long_code_block', 'undefined_method'] for i in issues):
            refactor_needed.append((block, issues))
    
    if refactor_needed:
        for block, issues in refactor_needed:
            print(f"\n**{block['section_heading']}**")
            print(f"  Full Path: {block['heading_path']}")
            print(f"  Lines: {block['start_line']}-{block['end_line']}")
            print(f"  Language: {block['language']}, Size: {block['line_count']} lines")
            print(f"  Issues: {len(issues)}")
            for issue in issues:
                print(f"    - [{issue['severity']}] {issue['type']}: {issue['message']}")
    else:
        print("\nNo code blocks require urgent refactoring.")

if __name__ == '__main__':
    main()
