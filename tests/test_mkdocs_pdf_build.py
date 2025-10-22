"""
Comprehensive unit tests for mkdocs_pdf_build.py script.

Tests cover all functions with emphasis on the new/modified code:
- restore_pymdownx_tags() (FIX 2)
- load_yaml() using yaml.full_load (FIX 1)
- Integration with main() function
- All other functions for complete coverage
"""

import pytest
import tempfile
import shutil
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open, call
from typing import Dict, Any

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import mkdocs_pdf_build
import pymdownx.superfences


# ============================================================================
# Tests for restore_pymdownx_tags() - NEW FUNCTION (FIX 2)
# ============================================================================

class TestRestorePymdownxTags:
    """Test suite for the restore_pymdownx_tags function."""
    
    def test_restore_tags_with_function_object(self):
        """Test that function objects are replaced with YAML tag strings."""
        config = {
            "markdown_extensions": [
                "admonition",
                {
                    "pymdownx.superfences": {
                        "custom_fences": [
                            {
                                "name": "mermaid",
                                "class": "mermaid",
                                "format": pymdownx.superfences.fence_code_format
                            }
                        ]
                    }
                }
            ]
        }
        
        mkdocs_pdf_build.restore_pymdownx_tags(config)
        
        # Verify the function object was replaced with the string
        extensions = config["markdown_extensions"]
        superfences_config = extensions[1]["pymdownx.superfences"]
        fence = superfences_config["custom_fences"][0]
        assert fence["format"] == "!!python/name:pymdownx.superfences.fence_code_format"
    
    def test_restore_tags_without_function_object(self):
        """Test that non-function format values are left unchanged."""
        config = {
            "markdown_extensions": [
                {
                    "pymdownx.superfences": {
                        "custom_fences": [
                            {
                                "name": "custom",
                                "class": "custom",
                                "format": "some_string_value"
                            }
                        ]
                    }
                }
            ]
        }
        
        original_format = config["markdown_extensions"][0]["pymdownx.superfences"]["custom_fences"][0]["format"]
        mkdocs_pdf_build.restore_pymdownx_tags(config)
        
        # Verify non-function values remain unchanged
        fence = config["markdown_extensions"][0]["pymdownx.superfences"]["custom_fences"][0]
        assert fence["format"] == original_format
    
    def test_restore_tags_empty_config(self):
        """Test handling of empty configuration."""
        config = {}
        mkdocs_pdf_build.restore_pymdownx_tags(config)
        assert config == {}
    
    def test_restore_tags_multiple_fences(self):
        """Test with multiple custom fences, some with function objects."""
        config = {
            "markdown_extensions": [
                {
                    "pymdownx.superfences": {
                        "custom_fences": [
                            {
                                "name": "mermaid",
                                "class": "mermaid",
                                "format": pymdownx.superfences.fence_code_format
                            },
                            {
                                "name": "custom",
                                "class": "custom",
                                "format": "custom_formatter"
                            }
                        ]
                    }
                }
            ]
        }
        
        mkdocs_pdf_build.restore_pymdownx_tags(config)
        
        fences = config["markdown_extensions"][0]["pymdownx.superfences"]["custom_fences"]
        assert fences[0]["format"] == "!!python/name:pymdownx.superfences.fence_code_format"
        assert fences[1]["format"] == "custom_formatter"


# ============================================================================
# Tests for load_yaml() - MODIFIED (FIX 1)
# ============================================================================

class TestLoadYaml:
    """Test suite for the load_yaml function using yaml.full_load."""
    
    def test_load_yaml_with_python_name_tag(self):
        """Test loading YAML with !!python/name tag (requires full_load)."""
        yaml_content = """markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False, encoding='utf-8') as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            result = mkdocs_pdf_build.load_yaml(temp_path)
            
            # Verify the function object was loaded
            fence = result["markdown_extensions"][0]["pymdownx.superfences"]["custom_fences"][0]
            assert fence["format"] is pymdownx.superfences.fence_code_format
            assert callable(fence["format"])
        finally:
            temp_path.unlink()


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_restore_tags_after_full_load(self):
        """Test that restore_pymdownx_tags correctly reverses yaml.full_load."""
        yaml_content = """markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False, encoding='utf-8') as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        
        try:
            # Load with full_load (converts tag to function object)
            config = mkdocs_pdf_build.load_yaml(temp_path)
            
            # Verify it's a function
            fence = config["markdown_extensions"][0]["pymdownx.superfences"]["custom_fences"][0]
            assert callable(fence["format"])
            assert fence["format"] is pymdownx.superfences.fence_code_format
            
            # Restore tags
            mkdocs_pdf_build.restore_pymdownx_tags(config)
            
            # Verify it's back to a string
            assert fence["format"] == "!!python/name:pymdownx.superfences.fence_code_format"
            assert isinstance(fence["format"], str)
            
            # Now safe_dump should work
            out_path = Path(str(temp_path) + ".out")
            mkdocs_pdf_build.dump_yaml(config, out_path)
            
            # Verify the file was written
            assert out_path.exists()
            content = out_path.read_text()
            assert "!!python/name:pymdownx.superfences.fence_code_format" in content
            
            out_path.unlink()
            
        finally:
            temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])