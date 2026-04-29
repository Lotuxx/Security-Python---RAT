# AGENTS.md - Security-Python-RAT Codebase Guide

## Project Overview
This is a **school security course template project** for ESGI's 4th-year Python security course. It contains two independent security applications:
- **Server (TP1)**: Network traffic capture, analysis, and PDF reporting system
- **Client (TP3)**: Remote Administration Tool (RAT) with CLI-based command execution

## Quick Start

### Development Setup
```bash
poetry lock
poetry install
```

### Running Applications
```bash
poetry run server    # Launches network capture and analysis
poetry run client    # Launches RAT with Typer CLI
```

### Running Tests
```bash
pytest           # All tests
pytest tests/    # Full test suite
pytest tests/server/utils/test_*.py  # Specific test groups
```

## Architecture & Data Flow

### Server Module (src/server/)
**Purpose**: Capture network traffic, detect security threats, generate PDF reports.

**Flow**:
1. `main.py` → Creates `Capture` instance
2. `Capture` → Uses `lib.choose_interface()` to select network interface
3. `capture.capture_traffic()` → Captures packets
4. `capture.analyse("tcp")` → Analyzes protocols for attacks (SQL injection, ARP spoofing, etc.)
5. `Report` → Generates PDF with summary, array, and graph
6. `report.save(filename)` → Writes report file

**Key Classes**:
- `Capture`: Manages traffic capture and analysis (`src/server/utils/capture.py`)
- `Report`: Handles PDF generation and file output (`src/server/utils/report.py`)

### Client Module (src/client/)
**Purpose**: RAT with multiple command capabilities (incomplete template).

**Architecture**:
- `main.py` → Uses Typer framework to create CLI app
- `cli.py` → CLI handler with commands: help, download, upload, shell, ipconfig, screenshot, search, hashdump, keylogger, webcam_snapshot, webcam_stream, record_audio
- `session.py` → Session class for captcha solving and flag submission
- `captcha.py` → Captcha handling utilities

## File Structure & Key Modules

### Root Config (src/config.py)
- **Central logging setup** imported by all modules
- Uses both FileHandler (`app.log`) and StreamHandler
- **Pattern**: Each submodule creates logger with its own name: `logger = logging.getLogger("TP1")` or `logger = logging.getLogger("TP3")`

### Import Pattern
**IMPORTANT**: Inconsistent import styles exist in codebase:
- Absolute: `from src.server.utils.lib import choose_interface`
- Relative: `from server.utils.config import logger`
- **When modifying**: Use `from src.<module>.<path>` for consistency

### Test Conventions
**Pattern**: Given-When-Then with unittest.mock
```python
def test_given_X_when_Y_then_Z():
    # Given
    capture = Capture()
    # When
    result = capture.capture_traffic()
    # Then
    assert result == expected_value
```
**Mocking style**: `patch.object(capture, "method_name")` and `MagicMock()` for dependencies

## Dependencies & External Tools

### Key Dependencies (from pyproject.toml)
- **Network**: `scapy` (packet sniffing), `capstone` (disassembly)
- **Reporting**: `pygal` (charts), `fpdf2` (PDF generation)
- **CLI**: `typer` (command-line parsing)
- **Utilities**: `requests`, `python-dotenv`, `pytest`

### Entry Points (pyproject.toml)
```toml
[tool.poetry.scripts]
server = "server.main:main"
client = "client.main:main"
```

## Project-Specific Patterns & Conventions

### Logging Pattern
All modules inherit logging from `src/config.py`. Log output goes to both console and `app.log` file.
```python
from server.utils.config import logger  # Already configured
logger.info("Message")
```

### State & Method Naming
- Methods returning empty strings indicate **TODO implementations**: `sort_network_protocols()`, `get_all_protocols()`
- Private methods prefixed with `_`: `_gen_summary()`
- Boolean/filter methods don't use `is_` prefix consistently (watch for this in new code)

### Report Generation Pattern
```python
report.generate("graph")   # Generates graph, updates self.graph
report.generate("array")   # Generates array, updates self.array
report.concat_report()     # Combines title + summary + array + graph
report.save(filename)      # Writes concatenated content to file
```

### CLI Parameter Pattern (Typer)
Parameters use `Annotated` type hints with `typer.Option(...)`:
```python
def cli(
    help: Annotated[str, typer.Option(..., "--url", help="url")] = "",
):
```

## Critical Implementation Notes

### Known Issues
1. **Import inconsistency**: `capture.py` mixes absolute (`from src.`) and relative (`from server.`) imports - standardize when refactoring
2. **CLI incomplete**: Many commands in `cli.py` have identical placeholders and no implementation
3. **Empty implementations**: Core methods return empty strings - part of assignment structure

### Common Mistakes to Avoid
- Don't bypass the centralized logging in `src/config.py` - use logger from respective `utils/config.py`
- Test mocking should use `unittest.mock`, not other libraries
- File I/O in `Report.save()` uses `self.filename` (instance variable), not passed parameter

### Testing File Organization
- Server tests: `tests/server/utils/test_*.py`
- Client tests: `tests/client/utils/test_*.py`
- Test for mock: imported as `from src.server.utils.capture import Capture`

## Development Workflow

### Adding New Features
1. Implement in appropriate module (`src/server/utils/` or `src/client/utils/`)
2. Create corresponding test file following Given-When-Then pattern
3. Use centralized logger from that module's `config.py`
4. Run: `pytest tests/<module>/utils/test_<feature>.py`

### Running Full Test Suite
```bash
pytest -v        # Verbose output
pytest --cov     # With coverage (if configured)
```

### Debugging
Check `app.log` for execution logs. Logging format includes timestamp, module name, level, and message.

## Security Context
This is a **security training project covering**:
- Network protocol analysis
- Attack detection patterns (SQL injection, ARP spoofing)
- Evidence collection and reporting
- Remote command execution (RAT template)

**Note**: This is educational code - not production-ready.

