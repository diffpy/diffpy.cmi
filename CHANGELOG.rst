=============
Release notes
=============

.. current developments

3.1.2
=====

**Added:**

* Add color to console print statements.
* Add ``diffpy.srfit`` examples to ``core`` pack.
* Add test for ``print_profiles``.

**Changed:**

* Update command-line interface instructions in the README.
* Pin ``sphinx<9`` until ``sphinx_rt_theme`` supports sphinx 9.

**Removed:**

* Remove Python 2 code from ``linefit`` example.


3.1.1
=====

**Added:**

* Add test for ``copy_examples``.
* Added ``print_info`` function.
* Add workflow to run ``examples/validate_examples.py`` manually.
* Add modules ``cli``, ``conda``, ``installer``, ``log``, ``packsmanager``, ``profilesmanager``.
* Add cmi cli commands for managing/installing profiles and packs; example and manual commands.
* Add `all.yml` for profile installation demonstration.
* Add `_tests.yml` profile for profile post-steps demonstration.
* Add test for building examples dict.
* Add tests that run PDF example scripts
* Add example for installing pdf pack and add example scripts.
* Add line fitting example.
* Add functionality for copying examples.
* Add temp dir fixture for testing.
* Add BG stylesheets for plotting.
* Add tutorial on `linefit` to documentation.
* Add installation instructions for packs.
* Add diffpy.cmi as entrypoint.
* Added ``print_profiles`` function.
* Add comprehensive documentation highlighting new cli changes.

**Changed:**

* Changed workflow so that ``validate_examples.py`` is ran only on manual triggers.
* Update names to skpkg standard.
* Change requirements dir for packs and profiles management.
* Change example dict build process.
* Changed the cli syntax.
* change examples directory structure to insert the name of the ``pack" that the examples exemplify.

**Fixed:**

* Fixed how paths are handled in tests for different operating systems.


0.0.1
=====

**Added:**

* Add CLI to return diffpy.cmi version and help page.
* Add getting started page to docs with link to primer book.
* Add section to docs for community-driven modules.
* Add long description to README.
* Add light-weight documentation migrated from old diffpy-CMI documentation.
* Add bulk Ni PDF fitting tutorial.
