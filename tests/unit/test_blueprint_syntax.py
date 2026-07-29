"""Compile Task 8c Blueprint files when a compiler is available."""

import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest


_ROOT = pathlib.Path(__file__).resolve().parents[2]
_FILES = [
    _ROOT / "bootc_installer/gtk/default-encryption.blp",
    _ROOT / "bootc_installer/gtk/mok-enrollment.blp",
]


class TestTask8cBlueprintSyntax(unittest.TestCase):
    def test_task8c_style_lists_use_blueprint_list_grammar(self):
        for blueprint in _FILES:
            with self.subTest(blueprint=blueprint.name):
                self.assertIsNone(
                    re.search(r"styles\s*\[[^]]*\];", blueprint.read_text()),
                    "styles lists must not end with a semicolon",
                )

    def test_task8c_blueprints_compile_when_compiler_is_available(self):
        compiler = shutil.which("blueprint-compiler")
        if compiler is None:
            self.skipTest("blueprint-compiler is unavailable")

        with tempfile.TemporaryDirectory() as output:
            subprocess.run(
                [compiler, "batch-compile", output, str(_ROOT / "bootc_installer"), *map(str, _FILES)],
                check=True,
            )
