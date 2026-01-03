import sys

def check_line_lengths(filepath, limit=75):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    in_code_block = False
    violations = []
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if line_stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            # Check length of the line (excluding newline)
            line_len = len(line.rstrip('\n'))
            if line_len > limit:
                violations.append({
                    'line_num': i + 1,
                    'length': line_len,
                    'content': line.rstrip('\n')
                })

    if violations:
        print(f"File: {filepath}")
        print(f"Found {len(violations)} lines exceeding {limit} characters in code blocks:")
        print("-" * 60)
        for v in violations:
            # print truncated content if too long for display
            display_content = v['content']
            if len(display_content) > 100:
                display_content = display_content[:97] + "..."
            print(f"Line {v['line_num']} ({v['length']} chars): {display_content}")
    else:
        print(f"No line length violations found in {filepath} (limit: {limit})")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_line_lengths.py <filepath> [limit]")
    else:
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 75
        check_line_lengths(sys.argv[1], limit)
