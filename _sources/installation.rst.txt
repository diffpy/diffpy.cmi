:tocdepth: -1

.. index:: installation

.. _installation:

================
Installation
================

To install ``diffpy.cmi``, create a new conda environment or activate an existing environment and install the package from the conda-forge channel.

.. code-block:: bash

    conda create -n diffpy.cmi-env
    conda activate diffpy.cmi-env
    conda install -c conda-forge diffpy.cmi

To confirm that the installation was successful, type

.. code-block:: bash

        cmi --version

The output should print the latest version.

If the above does not work, you can use ``pip`` to download and install the latest release from
`Python Package Index <https://pypi.python.org>`_.
To install using ``pip`` into your ``diffpy.cmi_env`` environment, type

.. code-block:: bash

        pip install diffpy.cmi
