# Unit Tests for mkdocs_pdf_build.py

This directory contains comprehensive unit tests for the `scripts/mkdocs_pdf_build.py` script.

## Test Coverage

The test suite covers:

### New/Modified Functions (FIX 1 & FIX 2)
- **`restore_pymdownx_tags()`** - New function that converts Python function objects back to YAML tag strings
- **`load_yaml()`** - Modified to use `yaml.full_load` instead of `yaml.safe_load`

### Integration Tests
- Complete workflow testing the interaction between `load_yaml()` and `restore_pymdownx_tags()`
- Verification that YAML files with `!!python/name` tags can be loaded and safely dumped

## Running the Tests

### Install Dependencies
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=scripts --cov-report=html --cov-report=term
```

### Run Specific Test Classes
```bash
pytest tests/test_mkdocs_pdf_build.py::TestRestorePymdownxTags -v
pytest tests/test_mkdocs_pdf_build.py::TestLoadYaml -v
pytest tests/test_mkdocs_pdf_build.py::TestIntegration -v
```

## Test Structure

- `TestRestorePymdownxTags`: tests for the new `restore_pymdownx_tags()` function.
- `TestLoadYaml`: tests for the modified `load_yaml()` function.
- `TestIntegration`: integration tests for the complete YAML load/restore/dump workflow.

## Key Test Scenarios

1. **Function Object Replacement**: Verifies that `pymdownx.superfences.fence_code_format` function objects are correctly converted to YAML tag strings
2. **Non-Function Preservation**: Ensures non-function format values remain unchanged
3. **Empty/Edge Cases**: Tests empty configs, missing keys, and edge cases
4. **Multiple Fences**: Tests configurations with multiple custom fences
5. **Round-trip Conversion**: Verifies that YAML can be loaded with `full_load`, modified, restored, and dumped with `safe_dump`

## Why These Tests Matter

The changes in the diff address a critical bug where:
1. `yaml.full_load()` converts `!!python/name:pymdownx.superfences.fence_code_format` to an actual Python function object
2. `yaml.safe_dump()` cannot serialize Python function objects, causing the script to fail
3. `restore_pymdownx_tags()` converts the function object back to a string representation before dumping

These tests ensure this fix works correctly and handles various edge cases.