"""Focused tests for the parent secure-install boundary."""

import json
import os
import stat
import unittest
from unittest.mock import patch

from bootc_installer.utils.processor import Processor
from bootc_installer.utils.secure_install import (
    acknowledgement_route,
    create_mok_password_file,
    create_recovery_key_file,
    cleanup_credentials_from_recipe,
    get_managed_mok_password_from_recipe,
    remove_recovery_key_file,
)


class TestSecureInstall(unittest.TestCase):
    def test_secure_local_source_keeps_the_selected_remote_registry_ref(self):
        import pathlib
        import tempfile

        remote = "ghcr.io/frostyard/snow:latest"
        with tempfile.TemporaryDirectory() as directory, patch(
            "bootc_installer.utils.secure_install._recovery_directory",
            return_value=pathlib.Path(directory),
        ):
            recipe_path = Processor.gen_install_recipe("log", [{
                "disk": {"auto": {"disk": "/dev/vda"}},
                "selected_image": remote,
                "secure_install": True,
                "hostname": "secure-host",
                "encryption": {"use_encryption": True, "encryption_key": "recovery"},
            }], {
                "imgref": remote,
                "local_imgref": "containers-storage:ghcr.io/frostyard/snow:latest",
            })
            with open(recipe_path) as recipe_file:
                recipe = json.load(recipe_file)

            self.assertEqual(recipe["image"], remote)
            self.assertEqual(recipe["targetImgref"], remote)
            cleanup_credentials_from_recipe(recipe_path)
            os.unlink(recipe_path)

    def test_secure_nvidia_source_keeps_the_selected_remote_registry_ref(self):
        import pathlib
        import tempfile

        remote = "ghcr.io/frostyard/snow:latest"
        with tempfile.TemporaryDirectory() as directory, patch(
            "bootc_installer.utils.secure_install._recovery_directory",
            return_value=pathlib.Path(directory),
        ), patch(
            "bootc_installer.core.system.Systeminfo.has_nvidia_gpu", return_value=True,
        ):
            recipe_path = Processor.gen_install_recipe("log", [{
                "disk": {"auto": {"disk": "/dev/vda"}},
                "selected_image": remote,
                "secure_install": True,
                "nvidia_imgref": "ghcr.io/frostyard/snow-nvidia:latest",
                "hostname": "secure-host",
                "encryption": {"use_encryption": True, "encryption_key": "recovery"},
            }], {})
            with open(recipe_path) as recipe_file:
                recipe = json.load(recipe_file)

            self.assertEqual(recipe["image"], remote)
            self.assertEqual(recipe["targetImgref"], remote)
            cleanup_credentials_from_recipe(recipe_path)
            os.unlink(recipe_path)

    def test_non_secure_local_source_still_overrides_only_the_install_image(self):
        remote = "ghcr.io/frostyard/snow:latest"
        recipe_path = Processor.gen_install_recipe("log", [{
            "disk": {"auto": {"disk": "/dev/vda"}},
            "selected_image": remote,
            "hostname": "generic-host",
            "encryption": {"use_encryption": False},
        }], {
            "imgref": remote,
            "local_imgref": "containers-storage:ghcr.io/frostyard/snow:latest",
        })
        with open(recipe_path) as recipe_file:
            recipe = json.load(recipe_file)

        self.assertEqual(recipe["image"], "containers-storage:ghcr.io/frostyard/snow:latest")
        self.assertEqual(recipe["targetImgref"], remote)
        os.unlink(recipe_path)

    def test_non_secure_nvidia_selection_remains_unchanged(self):
        remote = "ghcr.io/frostyard/snow:latest"
        nvidia = "ghcr.io/frostyard/snow-nvidia:latest"
        with patch("bootc_installer.core.system.Systeminfo.has_nvidia_gpu", return_value=True):
            recipe_path = Processor.gen_install_recipe("log", [{
                "disk": {"auto": {"disk": "/dev/vda"}},
                "selected_image": remote,
                "nvidia_imgref": nvidia,
                "hostname": "generic-host",
                "encryption": {"use_encryption": False},
            }], {})
        with open(recipe_path) as recipe_file:
            recipe = json.load(recipe_file)

        self.assertEqual(recipe["image"], nvidia)
        self.assertEqual(recipe["targetImgref"], nvidia)
        os.unlink(recipe_path)

    def test_mok_password_file_is_private_one_link_and_safe_alphanumeric(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path, password = create_mok_password_file(directory=directory)

            self.assertEqual(len(password), 16)
            self.assertTrue(password.isascii() and password.isalnum())
            with open(path, encoding="ascii") as password_file:
                self.assertEqual(password_file.read(), password)
            file_stat = os.stat(path)
            self.assertEqual(stat.S_IMODE(file_stat.st_mode), 0o600)
            self.assertEqual(file_stat.st_nlink, 1)
            remove_recovery_key_file(path)
            self.assertFalse(os.path.exists(path))

    def test_recovery_key_file_preserves_bytes_and_uses_owner_only_mode(self):
        import tempfile
        credential = "correct horse\n"

        with tempfile.TemporaryDirectory() as directory:
            path = create_recovery_key_file(credential, directory=directory)

            with open(path, "rb") as credential_file:
                self.assertEqual(credential_file.read(), credential.encode())
            self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o600)
            remove_recovery_key_file(path)
            self.assertFalse(os.path.exists(path))

    def test_secure_recipe_references_ephemeral_credentials_without_serializing_them(self):
        import pathlib
        import tempfile
        with tempfile.TemporaryDirectory() as directory, patch(
            "bootc_installer.utils.secure_install._recovery_directory",
            return_value=pathlib.Path(directory),
        ):
            credential = "trailing-newline-is-significant\n"
            finals = [{
                "disk": {"auto": {"disk": "/dev/vda"}, "filesystem": "xfs"},
                "selected_image": "ghcr.io/example/not-inferred:latest",
                "secure_install": True,
                "composefs_backend": False,
                "bootloader": "grub2",
                "image_filesystem": "xfs",
                "hostname": "secure-host",
                "encryption": {
                    "use_encryption": True,
                    "type": "tpm2-luks-passphrase",
                    "encryption_key": credential,
                },
            }]

            recipe_path = Processor.gen_install_recipe("log", finals, {})
            with open(recipe_path) as recipe_file:
                recipe = json.load(recipe_file)
            recovery_path = recipe["secureInstall"]["recoveryKeyFile"]
            mok_path = recipe["secureInstall"]["mokPasswordFile"]

            self.assertEqual(recipe["filesystem"], "btrfs")
            self.assertIs(recipe["composeFsBackend"], True)
            self.assertEqual(recipe["bootloader"], "systemd")
            self.assertEqual(recipe["encryption"], {"type": "luks-passphrase"})
            self.assertEqual(recipe["cosignPubKey"], "/usr/lib/snosi/cosign.pub")
            with open(recovery_path, "rb") as credential_file:
                self.assertEqual(credential_file.read(), credential.encode())
            with open(recipe_path) as recipe_file:
                recipe_text = recipe_file.read()
            self.assertFalse(credential in recipe_text, "recipe must not contain the recovery credential")
            with open(mok_path, encoding="ascii") as password_file:
                mok_password = password_file.read()
            self.assertEqual(len(mok_password), 16)
            self.assertTrue(mok_password.isascii() and mok_password.isalnum())
            self.assertFalse(mok_password in recipe_text, "recipe must not contain the MOK password")

            cleanup_credentials_from_recipe(recipe_path)
            self.assertFalse(os.path.exists(recovery_path))
            self.assertFalse(os.path.exists(mok_path))
            os.unlink(recipe_path)

    def test_recipe_cleanup_preserves_caller_owned_mok_password_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            caller_owned = os.path.join(directory, "operator-mok-password")
            with open(caller_owned, "w", encoding="ascii") as credential_file:
                credential_file.write("OperatorPassword")
            recipe_path = os.path.join(directory, "recipe.json")
            with open(recipe_path, "w", encoding="utf-8") as recipe_file:
                json.dump({"secureInstall": {"mokPasswordFile": caller_owned}}, recipe_file)

            cleanup_credentials_from_recipe(recipe_path)

            self.assertTrue(os.path.exists(caller_owned))

    def test_managed_cleanup_does_not_remove_a_replacement_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path, _password = create_mok_password_file(directory=directory)
            os.unlink(path)
            with open(path, "w", encoding="ascii") as replacement:
                replacement.write("operator-owned")
            os.chmod(path, 0o600)

            remove_recovery_key_file(path)

            self.assertTrue(os.path.exists(path))

    def test_credential_directory_is_exactly_owner_only_when_preexisting(self):
        import pathlib
        import tempfile

        with tempfile.TemporaryDirectory() as parent:
            directory = pathlib.Path(parent) / "credentials"
            directory.mkdir(mode=0o755)
            os.chmod(directory, 0o755)

            path, _password = create_mok_password_file(directory=directory)

            self.assertEqual(stat.S_IMODE(os.stat(directory).st_mode), 0o700)
            remove_recovery_key_file(path)

    def test_credential_directory_rejects_symlinks_and_non_directories(self):
        import pathlib
        import tempfile

        with tempfile.TemporaryDirectory() as parent:
            root = pathlib.Path(parent)
            target = root / "target"
            target.mkdir()
            link = root / "credentials-link"
            link.symlink_to(target)
            not_directory = root / "credentials-file"
            not_directory.write_text("not a directory")

            with self.assertRaises(ValueError):
                create_mok_password_file(directory=link)
            with self.assertRaises(ValueError):
                create_mok_password_file(directory=not_directory)

    def test_mok_handoff_rejects_a_valid_replacement_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            path, _password = create_mok_password_file(directory=directory)
            os.unlink(path)
            with open(path, "w", encoding="ascii") as replacement:
                replacement.write("A" * 16)
            os.chmod(path, 0o600)
            recipe_path = os.path.join(directory, "recipe.json")
            with open(recipe_path, "w", encoding="utf-8") as recipe_file:
                json.dump({"secureInstall": {"mokPasswordFile": path}}, recipe_file)

            self.assertEqual(get_managed_mok_password_from_recipe(recipe_path), "")

    def test_only_parent_managed_mok_password_is_available_for_success_handoff(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            managed_path, password = create_mok_password_file(directory=directory)
            recipe_path = os.path.join(directory, "managed-recipe.json")
            with open(recipe_path, "w", encoding="utf-8") as recipe_file:
                json.dump({"secureInstall": {"mokPasswordFile": managed_path}}, recipe_file)
            self.assertEqual(get_managed_mok_password_from_recipe(recipe_path), password)

            caller_owned = os.path.join(directory, "operator-mok-password")
            with open(caller_owned, "w", encoding="ascii") as credential_file:
                credential_file.write("OperatorPassword")
            with open(recipe_path, "w", encoding="utf-8") as recipe_file:
                json.dump({"secureInstall": {"mokPasswordFile": caller_owned}}, recipe_file)
            self.assertEqual(get_managed_mok_password_from_recipe(recipe_path), "")

            cleanup_credentials_from_recipe(recipe_path)
            remove_recovery_key_file(managed_path)

    def test_acknowledgements_keep_recovery_and_mok_as_separate_steps(self):
        self.assertEqual(acknowledgement_route(False, False), ["done"])
        self.assertEqual(acknowledgement_route(True, False), ["recovery", "done"])
        self.assertEqual(acknowledgement_route(False, True), ["mok", "done"])
        self.assertEqual(acknowledgement_route(True, True), ["recovery", "mok", "done"])
