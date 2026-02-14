from pathlib import Path
from re import sub as re_sub
from crossconfig import get_config, ConfigProtocol


def config() -> ConfigProtocol:
    """Get crossconfig instance, loading config if keys not initialized."""
    conf = get_config("tarot-oracle")
    if len(conf.list()) == 0:
        conf.load()
    return conf


def sanitize_filename(name: str) -> str | None:
    """Sanitize filename to prevent path traversal. Returns None if invalid."""
    safe_name = re_sub(r'[^a-zA-Z0-9._-]', '', name)
    safe_name = safe_name.lstrip('.-')
    return safe_name if safe_name else None


def validate_path_security(resolved: Path, path_arg: str) -> None:
    """Ensure resolved path is within allowed directories, raising ValueError otherwise."""
    if not (resolved.is_relative_to(Path.cwd()) or
            resolved.is_relative_to(Path(config().path()))):
        raise ValueError(f"Attempted to access file outside allowed directories: {path_arg}")


def ensure_config_directories() -> None:
    """Create required subdirectories for decks, invocations, and spreads."""
    conf = config()
    for subdir in ["decks", "invocations", "spreads"]:
        Path(conf.path(subdir)).mkdir(parents=True, exist_ok=True)

