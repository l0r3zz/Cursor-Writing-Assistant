# MDC (Model Definition Card) File Format Reference

**For use with Cursor IDE Agent System**

## Overview

MDC files (Model Definition Cards) are agent configuration files that define how AI agents behave in Cursor IDE. They combine YAML frontmatter (metadata) with markdown instructions.

## File Structure

MDC files use a three-section structure separated by `---` delimiters:

```
---
[First Block: Optional alwaysApply flag]
---
[Second Block: Required metadata (name, model, description, etc.)]
---
[Third Section: Markdown instructions/content]
```

## YAML Frontmatter

### First Block (Optional)
- **alwaysApply** (boolean): If `true`, agent's instructions remain active once referenced in a chat session

```yaml
---
alwaysApply: true
---
```

### Second Block (Required)
Contains metadata about the agent:

**Required Fields:**
- **name** (string): Display name for the agent
- **model** (string): AI model to use (e.g., "claude-sonnet-4", "gpt-4o", "perplexity", "gemini-2.5-pro")
- **description** (string): Brief description of the agent's purpose

**Optional Fields:**
- **type** (array): Categories for the agent (e.g., `["Writing", "Content Creation"]`)
- **icon** (string): Emoji or icon identifier (e.g., "✍️", "🔍")
- **actions** (object): Behavior settings
  - `auto_apply_edits` (boolean): Automatically apply code edits
  - `auto_run` (boolean): Automatically run commands
- **tools** (object): Tool permissions
  - `all` (boolean): Grant all tools
  - Or specific tool categories:
    - `search`: `web`, `codebase` (booleans)
    - `edit`: `edit_and_reapply` (boolean)

**Example Second Block:**
```yaml
---
name: "Writing Agent"
model: "claude-sonnet-4"
description: "Drafts book content matching author's technical voice and style"
type: ["Writing", "Content Creation"]
icon: "✍️"
actions:
  auto_apply_edits: true
  auto_run: false
tools:
  all: true
---
```

## Complete Example

```markdown
---
alwaysApply: true
---
name: "Research Agent"
model: "perplexity"
description: "Conducts research using web search and synthesizes findings into structured notes"
type: ["Research", "Fact-checking"]
icon: "🔍"
actions:
  auto_apply_edits: false
  auto_run: false
tools:
  all: false
  search:
    web: true
    codebase: false
  edit:
    edit_and_reapply: true
---

# Research Agent Instructions

You are a research specialist for a technical book about SRE and system reliability.

## Your Role
- Search for recent examples of system failures
- Focus on 2020-2025 for current relevance
- Synthesize findings into structured notes

[Additional markdown instructions...]
```

## Validation

Your project includes a validation script at `scripts/validate_mdc.py` that checks:
- File structure (must start with `---`)
- YAML syntax validity
- Required fields presence
- Code block closure
- Basic formatting issues

**To validate:**
```bash
python scripts/validate_mdc.py [path/to/file.mdc]
```

Or validate all files in `agents/` directory:
```bash
python scripts/validate_mdc.py
```

## Using MDC Files in Cursor

1. **Place files** in your project (typically `agents/` directory)

2. **Reference in Agent chat** using `@` syntax:
   ```
   @agents/research-agent.mdc
   ```

3. **Agent chat access**: Press `Cmd+L` (Mac) or `Ctrl+L` (Windows/Linux)

4. **For agents with `alwaysApply: true`**: Once referenced, instructions remain active for that chat session

## Available Models

Common model identifiers:
- `claude-sonnet-4` - Claude Sonnet 4 (Anthropic)
- `gpt-4o` - GPT-4 Optimized (OpenAI)
- `perplexity` - Perplexity AI (web search)
- `gemini-2.5-pro` - Gemini 2.5 Pro (Google)

## Best Practices

1. **File naming**: Use descriptive names with `.mdc` extension (e.g., `writing-agent.mdc`)
2. **Instructions**: Write clear, actionable instructions in the markdown section
3. **Tool permissions**: Grant only necessary tools for security and cost control
4. **alwaysApply**: Use sparingly - only for agents you want active throughout a session
5. **Documentation**: Include clear role descriptions and expected output formats in the markdown section

## Troubleshooting

**Common errors:**
- Missing `---` delimiters (must have at least 3)
- Missing required fields (`name`, `model`, `description`)
- Unclosed code blocks in markdown section
- Invalid YAML syntax (check indentation, quotes)

**Check structure:**
Run the validation script to identify issues:
```bash
python scripts/validate_mdc.py agents/your-agent.mdc
```

## References

### Video Tutorials

**Video Courses:**
- **LinkedIn Learning**: "AI Coding Agents with GitHub Copilot and Cursor" course includes a tutorial on adding custom instructions for Cursor, which covers MDC files
  - Course: https://www.linkedin.com/learning/ai-coding-agents-with-github-copilot-and-cursor/adding-custom-instructions-for-cursor
- **Instructa.ai**: "Cursor Rules .mdc Files — Ultimate Cursor AI Course" provides in-depth coverage of `.mdc` files
  - Course: https://www.instructa.ai/course/cursor-ai/view/f6fe3ffc-a412-45d5-a9dd-aedcf40effaa

**YouTube:**
- As of 2025, specific YouTube tutorials focused solely on MDC files are limited
- Search YouTube for general "Cursor IDE" tutorials that may cover agent configuration:
  - Search terms: "Cursor IDE tutorial", "Cursor AI agents", "Cursor IDE setup"
  - General Cursor IDE tutorials may include information about agent files and configuration

**Note**: YouTube content changes frequently. Search periodically for new tutorials as the MDC format evolves.

### Written Documentation

- **Workflow Guide**: See `cursor-book-workflow-guide.md` for detailed examples
- **Existing Agents**: See `agents/*.mdc` files for real-world examples
- **Official Docs**: https://cursor.com/docs (check for latest MDC format updates)
- **Validation Script**: `scripts/validate_mdc.py` shows expected structure

### Online Resources

- **Sample MDC Files**: https://www.aideploy.dev/mdc-sample.html (examples and explanations)
- **MDC Introduction**: https://www.aideploy.dev/mdc-intro.html (introductory guide)
- **Cursor Community Forum**: https://forum.cursor.com (discussions on MDC files and best practices)
- **Cursor Best Practices (GitHub)**: https://github.com/digitalchild/cursor-best-practices (guidelines and examples)
- **MDC Rules Library**: https://scott.beards.ly/blog/cursor-rules-library (custom Cursor rules examples)

## Example Agents in This Project

- `agents/research-agent.mdc` - Perplexity research specialist
- `agents/writing-agent.mdc` - Claude drafting agent (alwaysApply: true)
- `agents/critique-agent.mdc` - GPT-4 editorial reviewer
- `agents/technical-agent.mdc` - Gemini technical validator

---

**Note**: MDC format is specific to Cursor IDE. For MCP (Model Context Protocol) configuration, see `mcp_coaching_guide.md` - these are separate systems.
