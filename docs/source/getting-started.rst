:tocdepth: -1

.. index:: getting-started

.. _getting-started:

================
Getting started
================

.. image:: ./img/pdfprimer.png
    :alt: codecov-in-pr-comment
    :width: 150px
    :align: right

For detailed instructions and in-depth examples of modeling with ``diffpy.cmi``, we highly recommend the book,

*Atomic Pair Distribution Function Analysis: A Primer* by Simon J. L. Billinge and Kirsten M. Ø. Jensen (Oxford University Press, 2023).

To purchase this book, please visit `this link <https://www.amazon.com/Atomic-Pair-Distribution-Function-Analysis/dp/0198885806>`_.

Installation
------------

To install ``diffpy.cmi``, create a new conda environment or activate an existing environment and install the package from the conda-forge channel.

.. code-block:: bash

    conda create -n diffpy.cmi-env
    conda install -c conda-forge diffpy.cmi
    conda activate diffpy.cmi-env

To confirm that the installation was successful, type

.. code-block:: bash

        python -c "import diffpy.cmi; print(diffpy.cmi.__version__)"

The output should print the latest version.

If the above does not work, you can use ``pip`` to download and install the latest release from
`Python Package Index <https://pypi.python.org>`_.
To install using ``pip`` into your ``diffpy.cmi_env`` environment, type

.. code-block:: bash

        pip install diffpy.cmi

Pack and Profile Installation
-----------------

Use the `cmi` command-line interface to install and manage modular optional dependencies, known as `packs`,
and to configure or execute user-defined workflows that combine multiple packs with optional post-installation steps,
known as `profiles`. To use `cmi`, you can run the following example commands:

Show available commands and options with,

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

    cmi install <pack_name>
    cmi install <profile_name>
    cmi install </absolute/path/to/profile>

List and get installed examples,

.. code-block:: bash

    cmi example list
    cmi example (copy) <example_name>

Data and Examples
-----------------

Worked examples and experimental data from the book are freely available at our
`GitHub repository <https://github.com/Billingegroup/pdfttp_data>`_.
