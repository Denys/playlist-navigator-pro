# Session Start Workflow

Use this workflow when a session begins. It is designed to follow the universal agentic prompt guidelines and the tool-detection reference, and it starts with the `/session_start` command.

## /session_start

### 1) Load Core Instructions
1. Read `_agentic_promts/AGENTS.md`.
2. Run platform detection using the table in `_agentic_promts/AGENTS.md`.
3. Read the tool-specific file that matches detection:
   - Kilo Code → `_agentic_promts/KILO.md`
   - Claude Code → `_agentic_promts/CLAUDE.md`
   - Gemini → `_agentic_promts/GEMINI.md`
   - OpenCode → `_agentic_promts/OPENCODE.md`
4. Merge instructions with tool-specific overrides.

### 2) Run Tool-Detection Test (Required)
Follow `_agentic_promts/TOOL_DETECTION_TEST.md` precisely:
1. Verify detection criteria against available tools/capabilities.
2. Confirm the expected behavior for the detected platform.
3. Apply the correct tool usage patterns (file reads, searches, and command execution rules).
4. If detection is uncertain, prompt for tool choice and then load the corresponding file.

### 3) Initialize Session State
1. Read `CHECKPOINT.md` if present.
2. Read `{project}_bugs.md` if present.
3. Read `completion_monitor.md` if present.
4. Scan `directives/` for available SOPs.
5. Scan `execution/` for available tools.

### 4) Establish Execution Posture
- Apply checkpoint strategy (per Kilo Code when detected):
  - Checkpoint before untested scripts, paid APIs, new files, or destructive actions.
  - No checkpoint for read/search/log-only operations.
- Confirm error recovery protocol is active.

### 5) Begin Task Execution
- Proceed with the user’s task using the merged instruction set.
- Prefer existing execution tools over new scripts.
- Update session state files at end of significant work.

---

## Session Start Checklist
- [ ] Read `_agentic_promts/AGENTS.md`
- [ ] Detect platform and read tool-specific file
- [ ] Execute `_agentic_promts/TOOL_DETECTION_TEST.md`
- [ ] Read session state files (if present)
- [ ] Review directives and execution tools
- [ ] Start task with correct tool usage and checkpoints
