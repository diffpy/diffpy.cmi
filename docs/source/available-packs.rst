Packs
-----

This page lists the dependencies required by each ``diffpy.cmi`` pack.


====
core
====

The ``core`` pack provides the essential building blocks for creating and running regression workflows in ``diffpy.cmi``.

- ``packaging``
- ``PyYAML``
- ``diffpy.utils``
- ``diffpy.srfit``
- ``diffpy.structure``

===
pdf
===

The ``pdf`` pack is designed to handle pair distribution function (PDF) modeling and analysis.

- ``diffpy.srreal``
- ``pyobjcryst``

====
docs
====

The ``docs`` pack contains the dependencies required to build the documentation for ``diffpy.cmi``.

- ``sphinx``
- ``sphinx_rtd_theme``
- ``sphinx-copybutton``
- ``doctr``
- ``m2r``

========
plotting
========

The ``plotting`` pack provides tools for plotting and visualizing data.

- ``ipywidgets``
- ``matplotlib``
- ``ipympl``
- ``bg-mpl-stylesheets``
- ``py3dmol>=2.0.1``


=====
tests
=====

The ``tests`` pack contains the dependencies required for testing ``diffpy.cmi``.

- ``flake8``
- ``pytest``
- ``codecov``
- ``coverage``
- ``pytest-cov``
- ``pytest-env``
- ``pytest-mock``
- ``freezegun``
- ``DeepDiff``
