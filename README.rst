|Icon| |title|_
===============

.. |title| replace:: diffpy.cmi
.. _title: https://diffpy.github.io/diffpy.cmi

.. |Icon| image:: https://avatars.githubusercontent.com/diffpy
        :target: https://diffpy.github.io/diffpy.cmi
        :height: 100px

|PyPI| |Forge| |PythonVersion| |PR|

|CI| |Codecov| |Black| |Tracking|

.. |Black| image:: https://img.shields.io/badge/code_style-black-black
        :target: https://github.com/psf/black

.. |CI| image:: https://github.com/diffpy/diffpy.cmi/actions/workflows/matrix-and-codecov-on-merge-to-main.yml/badge.svg
        :target: https://github.com/diffpy/diffpy.cmi/actions/workflows/matrix-and-codecov-on-merge-to-main.yml

.. |Codecov| image:: https://codecov.io/gh/diffpy/diffpy.cmi/branch/main/graph/badge.svg
        :target: https://codecov.io/gh/diffpy/diffpy.cmi

.. |Forge| image:: https://img.shields.io/conda/vn/conda-forge/diffpy.cmi
        :target: https://anaconda.org/conda-forge/diffpy.cmi

.. |PR| image:: https://img.shields.io/badge/PR-Welcome-29ab47ff

.. |PyPI| image:: https://img.shields.io/pypi/v/diffpy.cmi
        :target: https://pypi.org/project/diffpy.cmi/

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/diffpy.cmi
        :target: https://pypi.org/project/diffpy.cmi/

.. |Tracking| image:: https://img.shields.io/badge/issue_tracking-github-blue
        :target: https://github.com/diffpy/diffpy.cmi/issues

Complex modeling infrastructure: a modular framework for multi-modal modeling of scientific data.

DiffPy.CMI is designed as an extensible complex modeling infrastructure. Users and developers can readily integrate novel data types and constraints into custom workflows. While widely used for advanced analysis of structural data, the framework is general and can be applied to any problem where model parameters are refined to fit calculated quantities to data.

DiffPy.CMI is a community-driven project that supports Unix, Linux, macOS, and Windows platforms. It is designed to be used in Python scripts enabling flexible scripting and automation for advanced and reproducible workflows. Users are encouraged to leverage the software for their modeling needs and to contribute feedback, use cases, and extensions through the project community.

For more information about the diffpy.cmi library, please consult our `online documentation <https://diffpy.github.io/diffpy.cmi>`_.

Citation
--------

If you use diffpy.cmi in a scientific publication, we would like you to cite this package as

        Juhás, P.; Farrow, C. L.; Yang, X.; Knox, K. R.; Billinge, S. J. L. Complex Modeling: A Strategy and Software Program for Combining Multiple Information Sources to Solve Ill Posed Structure and Nanostructure Inverse Problems. Acta Crystallogr A Found Adv 2015, 71 (6), 562–568. https://doi.org/10.1107/S2053273315014473.

Installation
------------

The preferred method is to use `Miniconda Python
<https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html>`_
and install from the "conda-forge" channel of Conda packages.

To add "conda-forge" to the conda channels, run the following in a terminal. ::

        conda config --add channels conda-forge

We want to install our packages in a suitable conda environment.
The following creates and activates a new environment named ``diffpy.cmi_env`` ::

        conda create -n diffpy.cmi_env diffpy.cmi
        conda activate diffpy.cmi_env

To confirm that the installation was successful, type ::

        python -c "import diffpy.cmi; print(diffpy.cmi.__version__)"

The output should print the latest version displayed on the badges above.

If the above does not work, you can use ``pip`` to download and install the latest release from
`Python Package Index <https://pypi.python.org>`_.
To install using ``pip`` into your ``diffpy.cmi_env`` environment, type ::

        pip install diffpy.cmi

If you prefer to install from sources, after installing the dependencies, obtain the source archive from
`GitHub <https://github.com/diffpy/diffpy.cmi/>`_. Once installed, ``cd`` into your ``diffpy.cmi`` directory
and run the following ::

        pip install .

Getting Started
---------------

Use the `cmi` command-line interface to install and manage modular optional dependencies, known as `packs`,
and to configure or execute user-defined workflows that combine multiple packs with optional post-installation steps,
known as `profiles`. To use `cmi`, you can run the following example commands:

 Show available commands and options,

.. code-block:: bash

        cmi -h

List installed and available packs and profiles,

.. code-block:: bash

        cmi pack list
        cmi profile list

Show details of a specific pack or profile,

.. code-block:: bash

        cmi pack show <pack_name>
        cmi profile show <profile_name>

Install a pack or profile (by name or path),

.. code-block:: bash

        cmi install <pack_name|profile_name|/absolute/path/to/profile>

List and get installed examples,

.. code-block:: bash

        cmi example list
        cmi example (copy) <example_name>

You may consult our `online documentation <https://diffpy.github.io/diffpy.cmi>`_ for more information,
tutorials, and API references.

Support and Contribute
----------------------

If you see a bug or want to request a feature, please `report it as an issue <https://github.com/diffpy/diffpy.cmi/issues>`_ and/or `submit a fix as a PR <https://github.com/diffpy/diffpy.cmi/pulls>`_.

Feel free to fork the project and contribute. To install diffpy.cmi
in a development mode, with its sources being directly used by Python
rather than copied to a package directory, use the following in the root
directory ::

        pip install -e .

To ensure code quality and to prevent accidental commits into the default branch, please set up the use of our pre-commit
hooks.

1. Install pre-commit in your working environment by running ``conda install pre-commit``.

2. Initialize pre-commit (one time only) ``pre-commit install``.

Thereafter your code will be linted by black and isort and checked against flake8 before you can commit.
If it fails by black or isort, just rerun and it should pass (black and isort will modify the files so should
pass after they are modified). If the flake8 test fails please see the error messages and fix them manually before
trying to commit again.

Improvements and fixes are always appreciated.

Before contributing, please read our `Code of Conduct <https://github.com/diffpy/diffpy.cmi/blob/main/CODE_OF_CONDUCT.rst>`_.

Contact
-------

For more information on diffpy.cmi please visit the project `web-page <https://diffpy.github.io/>`_ or email Simon Billinge at sb2896@columbia.edu.

Acknowledgements
----------------

``diffpy.cmi`` is built and maintained with `scikit-package <https://scikit-package.github.io/scikit-package/>`_.
