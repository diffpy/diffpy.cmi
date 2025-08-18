# setup.py
#
# DO NOT REMOVE setup.py. It is needed for
# including example files in the shipped package
import os
import shutil

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


class build_py(_build_py):
    def run(self):
        super().run()
        extra_dirs = [
            ("docs/build", os.path.join("diffpy", "cmi", "docs", "build")),
            (
                "docs/examples",
                os.path.join("diffpy", "cmi", "docs", "examples"),
            ),
            ("requirements", os.path.join("diffpy", "cmi", "requirements")),
        ]
        for src, rel_dst in extra_dirs:
            if not os.path.exists(src):
                print(f"Skipping missing directory: {src}")
                continue
            dst = os.path.join(self.build_lib, rel_dst)
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)


setup(
    cmdclass={"build_py": build_py},
)
