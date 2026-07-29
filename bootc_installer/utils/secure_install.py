"""Parent-side helpers for Fisherman's explicit secure-install API."""

import json
import os
import pathlib
import secrets
import stat
import string
import tempfile
import time


_RECOVERY_PREFIX = "bootc-secure-recovery-"
_MOK_PASSWORD_PREFIX = "bootc-secure-mok-password-"
_STALE_RECOVERY_MAX_AGE_SECONDS = 24 * 60 * 60
_MANAGED_CREDENTIAL_PREFIXES = (_RECOVERY_PREFIX, _MOK_PASSWORD_PREFIX)
_managed_credential_paths: dict[str, int] = {}


def _recovery_directory() -> pathlib.Path:
    """Return a host-visible directory in both native and Flatpak launches."""
    return pathlib.Path(os.environ.get("HOME", "/tmp")) / ".cache" / "bootc-installer"


def _prepare_credential_directory(directory: pathlib.Path) -> pathlib.Path:
    """Create or validate the private parent-owned credential directory."""
    try:
        directory.mkdir(mode=0o700, parents=True)
    except FileExistsError:
        pass
    try:
        directory_stat = os.lstat(directory)
    except OSError as error:
        raise ValueError("credential directory is unavailable") from error
    if not stat.S_ISDIR(directory_stat.st_mode):
        raise ValueError("credential directory must be a real directory")
    flags = os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0)
    try:
        directory_fd = os.open(directory, flags)
    except OSError as error:
        raise ValueError("credential directory must not be a symlink") from error
    try:
        directory_stat = os.fstat(directory_fd)
        if not stat.S_ISDIR(directory_stat.st_mode):
            raise ValueError("credential directory must be a real directory")
        os.fchmod(directory_fd, 0o700)
    finally:
        os.close(directory_fd)
    return directory


def create_recovery_key_file(credential: str, directory: pathlib.Path | None = None) -> str:
    """Create the one ephemeral recovery credential file Fisherman may consume."""
    directory = _prepare_credential_directory(pathlib.Path(directory or _recovery_directory()))
    fd, path = tempfile.mkstemp(prefix=_RECOVERY_PREFIX, dir=directory)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(os.dup(fd), "wb") as credential_file:
            credential_file.write(credential.encode())
        os.fstat(fd)
    except BaseException:
        os.close(fd)
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
        raise
    _managed_credential_paths[path] = fd
    return path


def _is_managed_recovery_key_file(path: str) -> bool:
    return path in _managed_credential_paths


def _is_private_regular_file(file_stat: os.stat_result, size: int | None = None) -> bool:
    return (
        stat.S_ISREG(file_stat.st_mode)
        and stat.S_IMODE(file_stat.st_mode) == 0o600
        and file_stat.st_nlink == 1
        and (size is None or file_stat.st_size == size)
    )


def _managed_path_matches_descriptor(path: str, fd: int, size: int | None = None) -> bool:
    """Verify the path still names the private file retained by this process."""
    path_stat = os.stat(path, follow_symlinks=False)
    descriptor_stat = os.fstat(fd)
    return (
        _is_private_regular_file(path_stat, size)
        and _is_private_regular_file(descriptor_stat, size)
        and (path_stat.st_dev, path_stat.st_ino) == (descriptor_stat.st_dev, descriptor_stat.st_ino)
    )


def create_mok_password_file(directory: pathlib.Path | None = None) -> tuple[str, str]:
    """Create a generated one-time MOK password file for Fisherman."""
    password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    directory = _prepare_credential_directory(pathlib.Path(directory or _recovery_directory()))
    fd, path = tempfile.mkstemp(prefix=_MOK_PASSWORD_PREFIX, dir=directory)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(os.dup(fd), "w", encoding="ascii") as password_file:
            password_file.write(password)
        os.fstat(fd)
    except BaseException:
        os.close(fd)
        try:
            os.unlink(path)
        except FileNotFoundError:
            pass
        raise
    _managed_credential_paths[path] = fd
    return path, password


def remove_recovery_key_file(path: str) -> None:
    """Delete a credential created by this process without touching caller-owned files."""
    credential_fd = _managed_credential_paths.pop(path, None)
    if credential_fd is not None:
        try:
            if _managed_path_matches_descriptor(path, credential_fd):
                os.unlink(path)
        except FileNotFoundError:
            pass
        finally:
            os.close(credential_fd)


def cleanup_credentials_from_recipe(recipe_path: str) -> None:
    """Remove only parent-created secure credential files named by a recipe."""
    try:
        with open(recipe_path) as recipe_file:
            secure_install = json.load(recipe_file).get("secureInstall", {})
    except (OSError, ValueError, AttributeError):
        return
    for field in ("recoveryKeyFile", "mokPasswordFile"):
        credential_path = secure_install.get(field, "")
        if isinstance(credential_path, str):
            remove_recovery_key_file(credential_path)


def get_managed_mok_password_from_recipe(recipe_path: str) -> str:
    """Read the generated MOK password only for the successful GUI handoff."""
    try:
        with open(recipe_path) as recipe_file:
            password_path = json.load(recipe_file).get("secureInstall", {}).get("mokPasswordFile", "")
        if not isinstance(password_path, str) or not _is_managed_recovery_key_file(password_path):
            return ""
        password_fd = _managed_credential_paths[password_path]
        if not _managed_path_matches_descriptor(password_path, password_fd, size=16):
            return ""
        password = os.pread(password_fd, 17, 0).decode("ascii")
    except (OSError, ValueError, AttributeError, UnicodeError):
        return ""
    if len(password) == 16 and password.isascii() and password.isalnum():
        return password
    return ""


def cleanup_stale_credential_files(
    directory: pathlib.Path | None = None,
    max_age_seconds: int = _STALE_RECOVERY_MAX_AGE_SECONDS,
    active_paths: set[str] | None = None,
) -> None:
    """Remove only old, regular, owner-only generated credential files from a prior crash.

    Generated credentials use the private prefix and mode 0600. Files younger
    than 24 hours, active paths, symlinks, hard links, and caller-owned names
    are retained. The age window avoids racing a concurrently starting app.
    """
    directory = pathlib.Path(directory or _recovery_directory())
    active_paths = active_paths or set(_managed_credential_paths)
    try:
        entries = list(os.scandir(directory))
    except OSError:
        return
    cutoff = time.time() - max_age_seconds
    for entry in entries:
        if not entry.name.startswith(_MANAGED_CREDENTIAL_PREFIXES) or entry.path in active_paths:
            continue
        try:
            file_stat = entry.stat(follow_symlinks=False)
        except OSError:
            continue
        if (
            not stat.S_ISREG(file_stat.st_mode)
            or stat.S_IMODE(file_stat.st_mode) != 0o600
            or file_stat.st_nlink != 1
            or file_stat.st_mtime > cutoff
        ):
            continue
        try:
            os.unlink(entry.path)
        except OSError:
            pass


# Compatibility names for existing callers during the secure-install transition.
cleanup_recovery_key_from_recipe = cleanup_credentials_from_recipe
cleanup_stale_recovery_key_files = cleanup_stale_credential_files


def acknowledgement_route(needs_recovery: bool, needs_mok: bool) -> list[str]:
    """Return the ordered post-success acknowledgement pages."""
    route = []
    if needs_recovery:
        route.append("recovery")
    if needs_mok:
        route.append("mok")
    route.append("done")
    return route
