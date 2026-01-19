"""Unified loader system for custom invocations and spreads."""

import json
import re
from pathlib import Path
from typing import Any

from tarot_oracle.config import config


class InvocationLoader:
    """Handles loading and management of custom invocation files."""

    def load_invocation(self, name: str) -> str | None:
        """Load invocation text by name using search order with security validation:
        
        Search order:
        1. ./{name}
        2. ./{name}.txt  
        3. ./{name}.md
        4. ~/.tarot-oracle/invocations/{name}
        5. ~/.tarot-oracle/invocations/{name}.txt
        6. ~/.tarot-oracle/invocations/{name}.md
        
        Args:
            name: Name of the invocation to load
            
        Returns:
            Full text of the invocation, or None if not found
        """
        # Sanitize filename to prevent path traversal
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '', name)
        safe_name = safe_name.lstrip('.-')
        if not safe_name:
            return None
            
        search_paths = [
            Path.cwd() / safe_name,
            Path.cwd() / f"{safe_name}.txt",
            Path.cwd() / f"{safe_name}.md",
            config.invocations_dir / safe_name,
            config.invocations_dir / f"{safe_name}.txt",
            config.invocations_dir / f"{safe_name}.md"
        ]

        for path in search_paths:
            if path.exists() and path.is_file():
                resolved = path.resolve()
                # Ensure path is within expected directories
                if (resolved.is_relative_to(Path.cwd()) or 
                    resolved.is_relative_to(config.home_dir)):
                    try:
                        with open(resolved, 'r', encoding='utf-8') as f:
                            return f.read().strip()
                    except (OSError, UnicodeDecodeError):
                        continue
        return None

    def list_invocations(self) -> list[dict[str, str]]:
        """Scan ~/.tarot-oracle/invocations/ and return invocation metadata.
        
        Returns:
            List of dictionaries containing invocation metadata (filename, preview)
        """
        if not config.invocations_dir.exists() or not config.invocations_dir.is_dir():
            return []

        invocations = []
        
        # Find all .txt and .md files in the invocations directory
        for text_file in config.invocations_dir.glob("*"):
            if text_file.suffix in ['.txt', '.md'] and text_file.is_file():
                try:
                    with open(text_file, 'r', encoding='utf-8') as f:
                        preview = f.read(100).strip()
                        if preview:
                            preview = preview.replace('\n', ' ')[:97] + '...' if len(preview) > 100 else preview
                        else:
                            preview = "Empty invocation file"
                            
                    invocations.append({
                        "filename": text_file.name,
                        "name": text_file.stem,
                        "preview": preview
                    })
                except (OSError, UnicodeDecodeError):
                    # Skip files that can't be read
                    continue
                    
        return invocations


class SpreadLoader:
    """Handles loading and management of custom spread configurations."""

    def load_spread(self, name: str) -> dict[str, Any] | None:
        """Load spread configuration by name using search order with security validation.
        
        Search order:
        1. ./{name}.json
        2. ~/.tarot-oracle/spreads/{name}.json
        
        Args:
            name: Name of the spread to load
            
        Returns:
            Spread configuration dictionary, or None if not found
        """
        # Sanitize filename to prevent path traversal
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '', name)
        safe_name = safe_name.lstrip('.-')
        if not safe_name:
            return None
            
        search_paths = [
            Path.cwd() / f"{safe_name}.json",
            config.spreads_dir / f"{safe_name}.json"
        ]

        for path in search_paths:
            if path.exists() and path.is_file():
                resolved = path.resolve()
                # Ensure path is within expected directories
                if (resolved.is_relative_to(Path.cwd()) or 
                    resolved.is_relative_to(config.home_dir)):
                    try:
                        with open(resolved, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        return self._validate_spread_config(config_data, str(path))
                    except (OSError, json.JSONDecodeError, ValueError):
                        continue
        return None

    def _validate_spread_config(self, config: dict[str, Any], path: str) -> dict[str, Any]:
        """Validate spread configuration structure and content.
        
        Args:
            config: Loaded configuration dictionary
            path: File path for error reporting
            
        Returns:
            Validated configuration dictionary
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate required fields
        if 'name' not in config:
            raise ValueError(f"Spread configuration must include 'name' field: {path}")
        
        if 'layout' not in config:
            raise ValueError(f"Spread configuration must include 'layout' field: {path}")
        
        # Validate layout - support both matrix format and position dictionary format
        layout = config['layout']
        if not isinstance(layout, list):
            raise ValueError(f"Spread 'layout' must be a list: {path}")
        
        # Check if this is a matrix layout (nested lists of integers)
        if layout and isinstance(layout[0], list):
            # Matrix layout format - validate that it contains integers or 0
            for i, row in enumerate(layout):
                if not isinstance(row, list):
                    raise ValueError(f"Layout row {i} must be a list: {path}")
                for j, cell in enumerate(row):
                    if not isinstance(cell, int):
                        raise ValueError(f"Layout cell [{i}][{j}] must be an integer: {path}")
        else:
            # Position dictionary format - traditional validation
            for i, position in enumerate(layout):
                if not isinstance(position, dict):
                    raise ValueError(f"Layout position {i} must be a dictionary: {path}")
                if 'position' not in position:
                    raise ValueError(f"Layout position {i} must include 'position' field: {path}")

        # Validate semantic groups if present
        if 'semantic_groups' in config:
            semantic_groups = config['semantic_groups']
            if not isinstance(semantic_groups, dict):
                raise ValueError(f"semantic_groups must be a dictionary: {path}")

        # Validate semantics matrix if present
        if 'semantics' in config:
            semantics = config['semantics']
            if not isinstance(semantics, list):
                raise ValueError(f"semantics must be a list: {path}")
            
            # Check if this is a matrix format (nested lists)
            if semantics and isinstance(semantics[0], list):
                # Matrix format - validate that it contains strings or empty values
                for i, row in enumerate(semantics):
                    if not isinstance(row, list):
                        raise ValueError(f"Semantics row {i} must be a list: {path}")
                    for j, cell in enumerate(row):
                        if cell is not None and not isinstance(cell, str):
                            raise ValueError(f"Semantics cell [{i}][{j}] must be a string or null: {path}")
            else:
                # Dictionary format - traditional validation
                for i, semantic in enumerate(semantics):
                    if not isinstance(semantic, dict):
                        raise ValueError(f"Semantics entry {i} must be a dictionary: {path}")

        # Validate variable placeholders in semantics (only for matrix format)
        semantics = config.get('semantics', [])
        if semantics and isinstance(semantics[0], list):
            self._validate_variable_placeholders_matrix(semantics, path)

        return config

    def _validate_variable_placeholders_matrix(self, semantics: list[list[str|None]], path: str) -> None:
        """Validate variable placeholder syntax in semantics matrix.
        
        Args:
            semantics: Matrix of semantic strings to validate
            path: File path for error reporting
            
        Raises:
            ValueError: If invalid variable placeholders are found
        """
        # Valid variable patterns
        valid_variables = {
            'water', 'fire', 'air', 'earth', 'spirit'
        }
        
        pattern = r'\$\{([^}]+)\}'
        
        for i, row in enumerate(semantics):
            for j, cell in enumerate(row):
                if isinstance(cell, str):
                    # Find all variable placeholders
                    matches = re.findall(pattern, cell)
                    for match in matches:
                        if match not in valid_variables:
                            raise ValueError(
                                f"Invalid variable placeholder '${{{match}}}' in semantics[{i}][{j}]. "
                                f"Valid variables: {', '.join(sorted(valid_variables))}: {path}"
                            )

    def _validate_variable_placeholders(self, semantics: list[dict], path: str) -> None:
        """Validate variable placeholder syntax in semantics.
        
        Args:
            semantics: List of semantic entries to validate
            path: File path for error reporting
            
        Raises:
            ValueError: If invalid variable placeholders are found
        """
        # Valid variable patterns
        valid_variables = {
            'water', 'fire', 'air', 'earth', 'spirit'
        }
        
        pattern = r'\$\{([^}]+)\}'
        
        for semantic in semantics:
            for key, value in semantic.items():
                if isinstance(value, str):
                    # Find all variable placeholders
                    matches = re.findall(pattern, value)
                    for match in matches:
                        if match not in valid_variables:
                            raise ValueError(
                                f"Invalid variable placeholder '${{{match}}}' in semantics. "
                                f"Valid variables: {', '.join(sorted(valid_variables))}: {path}"
                            )

    def list_spreads(self) -> list[dict[str, str]]:
        """Scan ~/.tarot-oracle/spreads/ and return spread metadata.
        
        Returns:
            List of dictionaries containing spread metadata (filename, name, description)
        """
        if not config.spreads_dir.exists() or not config.spreads_dir.is_dir():
            return []

        spreads = []
        
        # Find all .json files in the spreads directory
        for json_file in config.spreads_dir.glob("*.json"):
            try:
                config_data = self.load_spread(json_file.stem)
                if config_data:
                    spreads.append({
                        "filename": json_file.name,
                        "name": config_data.get("name", "Unnamed Spread"),
                        "description": config_data.get("description", "No description available")
                    })
            except Exception:
                # Skip invalid spread files
                continue
                    
        return spreads

    def save_spread(self, name: str, spread_config: dict[str, Any]) -> str:
        """Save a spread configuration to the spreads directory.
        
        Args:
            name: Name of the spread (without .json extension)
            spread_config: Spread configuration dictionary
            
        Returns:
            Path to the saved file
            
        Raises:
            ValueError: If configuration is invalid
            OSError: If file cannot be written
        """
        # Validate the configuration first
        validated_config = self._validate_spread_config(spread_config, "new spread")
        
        # Ensure spreads directory exists
        config.spreads_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitize filename
        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '', name)
        safe_name = safe_name.lstrip('.-')
        if not safe_name:
            raise ValueError("Invalid spread name")
            
        file_path = config.spreads_dir / f"{safe_name}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(validated_config, f, indent=2)
            return str(file_path)
        except OSError as e:
            raise OSError(f"Failed to save spread: {e}")