# File: scripts/mkdocs_hooks.py
#
# Description:
# An MkDocs on_config hook that runs during *every* standard MkDocs build (serve or build).
# It fetches real-time metadata (Git hash, build date, MkDocs version, license content)
# and injects it into the 'extra' configuration dictionary. This ensures that the
# documentation site (like the 'about.md' page) always displays the current build info.
#
# Dependencies:
# - mkdocs
# - pyyaml
# - git (must be accessible in the environment)
#
# Usage:
# Referenced directly in mkdocs.yml under the 'plugins' section:
# plugins:
#   - python:
#       module: scripts.mkdocs_hooks
#
# Note: This runs alongside the custom PDF script, ensuring both HTML and PDF
# output are correctly stamped with build traceability.

import os
import subprocess
from datetime import datetime
import pkg_resources
from mkdocs.config.base import Config
from mkdocs.utils import log

def get_tool_versions():
    """
    DOCSTRING: Fetches the version of MkDocs.
    
    Returns:
        dict: A dictionary containing the MkDocs version string.
    """
    versions = {}
    try:
        # PEP 8: Use proper spacing for dictionary access
        versions['mkdocs_version'] = pkg_resources.get_distribution('mkdocs').version
    except pkg_resources.DistributionNotFound:
        versions['mkdocs_version'] = 'MkDocs Not Found'
    return versions

def get_git_metadata():
    """
    DOCSTRING: Fetches Git repository metadata (commit hash and dirty status).
    
    Returns:
        dict: A dictionary containing 'git_hash', 'is_dirty', and 'dirty_status'.
    """
    metadata = {}
    try:
        # Get current commit hash (short form)
        commit_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
        metadata['git_hash'] = commit_hash

        # Check for uncommitted changes (dirty status)
        git_status = subprocess.check_output(['git', 'status', '--porcelain']).strip().decode('utf-8')
        metadata['is_dirty'] = bool(git_status)

        metadata['dirty_status'] = "Yes (Uncommitted changes exist) ⚠️" if metadata['is_dirty'] else "No (Clean working tree) ✅"

    except subprocess.CalledProcessError as e:
        log.warning(f"Git command failed during hook execution: {e}. Build metadata will be incomplete.")
        metadata['git_hash'] = 'N/A'
        metadata['is_dirty'] = True
        metadata['dirty_status'] = "Error running git command ❌"
    except FileNotFoundError:
        log.warning("Git executable not found. Build metadata will be incomplete.")
        metadata['git_hash'] = 'N/A'
        metadata['is_dirty'] = True
        metadata['dirty_status'] = "Git executable not found ❌"

    return metadata

def get_license_content(repo_root):
    """
    DOCSTRING: Reads the content of the LICENSE file from the repository root.
    
    Args:
        repo_root (str): The absolute path to the repository root directory.
        
    Returns:
        str: The content of the LICENSE file or an error message.
    """
    # Assuming LICENSE is in the root of the repository, one level up from the docs directory
    license_path = os.path.join(repo_root, 'LICENSE')
    if os.path.exists(license_path):
        try:
            with open(license_path, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            log.warning(f"Error reading LICENSE file at {license_path}: {e}")
            return "Could not read LICENSE file."
    return "LICENSE file not found."


def on_config(config: Config) -> Config:
    """
    DOCSTRING: MkDocs 'on_config' hook. Injects build metadata into the 
    MkDocs configuration 'extra' dictionary for use in Jinja2 templates (e.g., about.md).
    
    Args:
        config (Config): The MkDocs configuration object.
        
    Returns:
        Config: The modified MkDocs configuration object.
    """
    # Assuming 'docs' is inside the repository root
    base_dir = config.docs_dir
    # Move up one directory from 'docs' to get the repo root
    repo_root = os.path.dirname(base_dir)

    # 1. Gather Metadata
    git_metadata = get_git_metadata()
    tool_versions = get_tool_versions()
    license_content = get_license_content(repo_root)
    # Get current time in UTC
    build_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # 2. Define the injection structure
    injected_metadata = {
        'generated_on': build_date,
        'git_hash': git_metadata['git_hash'],
        'is_dirty': git_metadata['is_dirty'],
        'dirty_status': git_metadata['dirty_status'],
        'mkdocs_version': tool_versions['mkdocs_version'],
        'license_content': license_content,
    }

    # 3. Inject into the config.extra dictionary
    if 'extra' not in config:
        config['extra'] = {}
    
    # Initialize 'build_metadata' if it doesn't exist
    if 'build_metadata' not in config['extra'] or config['extra']['build_metadata'] is None:
        config['extra']['build_metadata'] = {}

    config['extra']['build_metadata'].update(injected_metadata)

    log.info(f"Injected build metadata: Git Hash={git_metadata['git_hash']}, Dirty={git_metadata['is_dirty']}")

    return config
