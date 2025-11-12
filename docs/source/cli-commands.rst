:tocdepth: -1

.. index:: cli-commands

.. _cli-commands:

CMI Command-Line Interface (CLI)
--------------------------------

The ``cmi`` command provides access to ``diffpy.cmi``.
It allows users to explore, install, and run **packs**, **profiles**, and **example workflows**.

============
Getting Help
============

The ``-h`` flag is available for **all** cmi commands and subcommands.
It's highly recommended to use it wherever necessary.

To display help for the main CLI, type

.. code-block:: bash

    cmi -h
    cmi --help

Display help for a specific subcommand with,

.. code-block:: bash

    cmi <subcommand> -h

Open the full online manual in a web browser by typing,

.. code-block:: bash

    cmi --manual

====================
``cmi info`` command
====================

To print information about available and installed packs, profiles, and examples, type,

.. code-block:: bash

   cmi info

To print information about packs, profiles, or examples, type

.. code-block:: bash

   cmi info packs
   cmi info profiles
   cmi info examples

=======================
``cmi install`` command
=======================

To install packs or profiles into your environment, type

.. code-block:: bash

    cmi install <pack-name>
    cmi install <profile-name>

Installation of multiple packs or profiles is also supported, e.g.,

.. code-block:: bash

    cmi install <pack-name> <profile-name>

====================
``cmi copy`` command
====================

To view all examples available to copy, type

.. code-block:: bash

    cmi info examples

To copy an example or list of examples to cwd, type

.. code-block:: bash

    cmi copy <example-name>
    cmi copy <example-name1> <example-name2>

To copy all examples from a pack or list of packs to cwd, type

.. code-block:: bash

    cmi copy <pack-name>
    cmi copy <pack-name1> <pack-name2>

To copy all examples to cwd, type

.. code-block:: bash

    cmi copy all

To copy an example to a target directory, type

.. code-block:: bash

    cmi copy <example-name> -t <target-directory>

To force overwrite a preexisting example directory, type

.. code-block:: bash

    cmi copy <example-name> -f

====================
``cmi env`` command
====================

To show basic information about your current conda environment, type

.. code-block:: bash

   cmi env
