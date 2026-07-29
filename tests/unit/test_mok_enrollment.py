"""Unit tests for the dedicated post-install MOK acknowledgement page."""

import importlib
import os
import sys
import types
import unittest
from unittest.mock import MagicMock


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def _import_mok_page():
    gi_mod = types.ModuleType("gi")
    repo_mod = types.ModuleType("gi.repository")

    class Template:
        def __call__(self, *_args, **_kwargs):
            return lambda cls: cls

        def Child(self, *_args, **_kwargs):
            return None

    gtk_mod = types.ModuleType("gi.repository.Gtk")
    gtk_mod.Template = Template()
    adw_mod = types.ModuleType("gi.repository.Adw")
    adw_mod.Bin = type("Bin", (), {})
    gobject_mod = types.ModuleType("gi.repository.GObject")
    gobject_mod.SignalFlags = types.SimpleNamespace(RUN_FIRST=0)
    repo_mod.Gtk = gtk_mod
    repo_mod.Adw = adw_mod
    repo_mod.GObject = gobject_mod
    gi_mod.repository = repo_mod
    sys.modules.update({
        "gi": gi_mod,
        "gi.repository": repo_mod,
        "gi.repository.Gtk": gtk_mod,
        "gi.repository.Adw": adw_mod,
        "gi.repository.GObject": gobject_mod,
    })
    sys.modules.pop("bootc_installer.views.mok_enrollment", None)
    return importlib.import_module("bootc_installer.views.mok_enrollment")


class TestMokEnrollment(unittest.TestCase):
    def test_generated_password_is_selectable_and_requires_recording_acknowledgement(self):
        module = _import_mok_page()
        page = module.BootcMokEnrollment.__new__(module.BootcMokEnrollment)
        page.password_row = MagicMock()
        page.password_value = MagicMock()
        page.operator_password_note = MagicMock()
        page.ack_check = MagicMock()
        page.btn_continue = MagicMock()

        page.prepare("AbcDef0123456789", parent_generated=True)

        page.password_row.set_visible.assert_called_once_with(True)
        page.password_value.set_text.assert_called_once_with("AbcDef0123456789")
        page.operator_password_note.set_visible.assert_called_once_with(False)
        page.ack_check.set_label.assert_called_once()
        page.btn_continue.set_sensitive.assert_called_once_with(False)

    def test_external_password_is_not_displayed(self):
        module = _import_mok_page()
        page = module.BootcMokEnrollment.__new__(module.BootcMokEnrollment)
        page.password_row = MagicMock()
        page.password_value = MagicMock()
        page.operator_password_note = MagicMock()
        page.ack_check = MagicMock()
        page.btn_continue = MagicMock()

        page.prepare(parent_generated=False)

        page.password_row.set_visible.assert_called_once_with(False)
        page.password_value.set_text.assert_called_once_with("")
        page.operator_password_note.set_visible.assert_called_once_with(True)
    def test_acknowledgement_requires_confirmation_before_continuing(self):
        module = _import_mok_page()
        page = module.BootcMokEnrollment.__new__(module.BootcMokEnrollment)
        page.btn_continue = MagicMock()
        page.password_value = MagicMock()
        page.emit = MagicMock()
        checkbox = MagicMock()
        checkbox.get_active.return_value = True

        page._BootcMokEnrollment__on_ack_toggled(checkbox)
        page._BootcMokEnrollment__on_continue()

        page.btn_continue.set_sensitive.assert_called_once_with(True)
        page.password_value.set_text.assert_called_once_with("")
        page.emit.assert_called_once_with("mok-enrollment-acknowledged")
