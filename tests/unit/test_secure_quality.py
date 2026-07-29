"""Regression coverage for Task 8c lifecycle hardening."""

import os
import pathlib
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

from bootc_installer.core.system import Systeminfo
from bootc_installer.utils.processor import Processor
from bootc_installer.utils.progress_parser import apply_progress_event, new_progress_state
from bootc_installer.utils.secure_install import cleanup_stale_credential_files


class TestSecureBootDetection(unittest.TestCase):
    def tearDown(self):
        Systeminfo._secure_boot = None

    def test_has_secure_boot_accepts_enabled_efi_variable(self):
        with tempfile.NamedTemporaryFile() as secure_boot_file, patch(
            "bootc_installer.core.system.glob.glob", return_value=[secure_boot_file.name]
        ):
            secure_boot_file.write(b"\x06\x00\x00\x00\x01")
            secure_boot_file.flush()
            self.assertTrue(Systeminfo.has_secure_boot())

    def test_has_secure_boot_fails_closed_for_malformed_or_unreadable_variable(self):
        with tempfile.NamedTemporaryFile() as secure_boot_file, patch(
            "bootc_installer.core.system.glob.glob", return_value=[secure_boot_file.name]
        ):
            secure_boot_file.write(b"\x01")
            secure_boot_file.flush()
            self.assertFalse(Systeminfo.has_secure_boot())


class TestSecureRecipeTransaction(unittest.TestCase):
    def test_empty_secure_passphrase_creates_no_recovery_file(self):
        finals = [{
            "disk": {"auto": {"disk": "/dev/vda"}},
            "selected_image": "ghcr.io/example/secure:latest",
            "secure_install": True,
            "hostname": "secure-host",
            "encryption": {"use_encryption": True, "encryption_key": ""},
        }]

        with patch("bootc_installer.utils.processor.create_recovery_key_file") as create:
            with self.assertRaisesRegex(ValueError, "recovery passphrase"):
                Processor.gen_install_recipe("log", finals, {})

        create.assert_not_called()

    def test_recipe_write_failure_removes_all_created_credential_files(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            "bootc_installer.utils.secure_install._recovery_directory",
            return_value=pathlib.Path(directory),
        ), patch(
            "bootc_installer.utils.processor.tempfile.NamedTemporaryFile",
            side_effect=OSError("recipe write failed"),
        ):
            finals = [{
                "disk": {"auto": {"disk": "/dev/vda"}},
                "selected_image": "ghcr.io/example/secure:latest",
                "secure_install": True,
                "hostname": "secure-host",
                "encryption": {"use_encryption": True, "encryption_key": "credential"},
            }]

            with self.assertRaisesRegex(OSError, "recipe write failed"):
                Processor.gen_install_recipe("log", finals, {})

            self.assertEqual(list(pathlib.Path(directory).iterdir()), [])


class TestStaleCredentialCleanup(unittest.TestCase):
    def test_stale_cleanup_removes_only_old_regular_managed_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            stale = root / "bootc-secure-mok-password-stale"
            current = root / "bootc-secure-recovery-current"
            caller_owned = root / "caller-key"
            stale.write_bytes(b"old")
            current.write_bytes(b"current")
            caller_owned.write_bytes(b"caller")
            os.chmod(stale, 0o600)
            os.chmod(current, 0o600)
            os.utime(stale, (1, 1))
            os.utime(current, None)

            cleanup_stale_credential_files(root, max_age_seconds=60, active_paths={str(current)})

            self.assertFalse(stale.exists())
            self.assertTrue(current.exists())
            self.assertTrue(caller_owned.exists())

    def test_stale_cleanup_does_not_follow_prefixed_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            target = root / "caller-key"
            link = root / "bootc-secure-mok-password-link"
            target.write_bytes(b"caller")
            link.symlink_to(target)

            cleanup_stale_credential_files(root, max_age_seconds=0)

            self.assertTrue(link.is_symlink())
            self.assertEqual(target.read_bytes(), b"caller")


class TestSecureProgressEvents(unittest.TestCase):
    def test_known_secure_event_updates_friendly_progress_without_secret_data(self):
        state = new_progress_state()

        update = apply_progress_event(
            '{"type":"secure_install","action":"mok_enrollment","status":"staged"}', state
        )

        self.assertEqual(update["label"], "Preparing Secure Boot enrollment…")
        self.assertEqual(state["secure_actions"], {"mok_enrollment": "staged"})

    def test_unknown_secure_event_remains_ignored(self):
        state = new_progress_state()
        self.assertIsNone(apply_progress_event(
            '{"type":"secure_install","action":"unknown","status":"passed"}', state
        ))
        self.assertEqual(state["secure_actions"], {})
