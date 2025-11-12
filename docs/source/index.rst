#######
|title|
#######

.. |title| replace:: diffpy.cmi documentation
| Software version |release|
| Last updated |today|.

``diffpy.cmi`` - Complex modeling infrastructure: a modular framework for multi-modal modeling of scientific data.

``diffpy.cmi`` is designed as an extensible complex modeling infrastructure.
Users and developers can readily integrate novel data types and constraints into custom workflows.
While widely used for advanced analysis of structural data, the framework is general and can be applied to any problem where
model parameters are refined to fit data.

``diffpy.cmi`` is a community-driven project that supports Unix, Linux, macOS, and Windows platforms.
It is designed to be used in Python scripts enabling flexible scripting and automation for advanced and reproducible workflows.
Users are encouraged to leverage the software for their modeling needs and to contribute feedback,
use cases, and extensions through the project community.

.. image:: ./img/diffpycmi_screenshot.png
    :alt: codecov-in-pr-comment
    :width: 600px
    :align: center

=======================================
The power of diffpy.cmi
=======================================

``diffpy.cmi`` is designed to be a **generalized regression engine** for any data type, enabling researchers to fit, analyze, and combine multiple sources of information in a unified framework.

.. raw:: html

    <div style="border: 4px solid #555; border-radius: 8px; padding: 10px; margin: 1em 0; text-align: center; background-color: #f8f8f8;">
        <strong>diffpy.cmi can be used to fit ANY type of data!</strong>
    </div>

One of the key strengths of ``diffpy.cmi`` is its modular design, which allows the integration and fitting of *any* data type.
While its most commonly used functionality is in pair distribution function (PDF) modeling and multi-dataset fitting,
**we actively encourage and support community-developed modules and workflows for any data types you see fit!**

.. image:: ./img/cmi_problem_types.png
    :alt: codecov-in-pr-comment
    :width: 500px
    :align: center

To make ``diffpy.cmi`` easy to use, we organize functionality into **Packs** and **Profiles**, allowing users to contribute their own modules and workflows seamlessly.
Please see the :ref:`overview <overview>` for more information on these concepts and how you can contribute your own extensions to the community!

===============
Getting started
===============

To get started, please visit the :ref:`Getting started <installation>` section.


.. image:: ./img/pdfprimer.png
    :alt: codecov-in-pr-comment
    :width: 150px
    :align: right

For detailed instructions and in-depth examples of modeling Pair Distribution Function data with ``diffpy.cmi``, we highly recommend the book,

*Atomic Pair Distribution Function Analysis: A Primer* by Simon J. L. Billinge and Kirsten M. Ø. Jensen (Oxford University Press, 2023).

To purchase this book, please visit `this link <https://www.amazon.com/Atomic-Pair-Distribution-Function-Analysis/dp/0198885806>`_.



=======
Authors
=======

``diffpy.cmi`` is developed by Simon Billinge and members of the Billinge Group. The maintainer for this project is Simon Billinge. For a detailed list of contributors see
https://github.com/diffpy/diffpy.cmi/graphs/contributors.

============
Installation
============

See the :ref:`installation` page or the `README <https://github.com/diffpy/diffpy.cmi#installation>`_
file included with the distribution.

================
Acknowledgements
================

``diffpy.cmi`` is built and maintained with `scikit-package <https://scikit-package.github.io/scikit-package/>`_.

========
Citation
========

If you use ``diffpy.cmi`` in a scientific publication, we would like you to cite this package as

    Juhás, P.; Farrow, C. L.; Yang, X.; Knox, K. R.; Billinge, S. J. L.
    Complex Modeling: A Strategy and Software Program for Combining Multiple Information Sources to Solve Ill Posed Structure and Nanostructure Inverse Problems.
    *Acta Crystallogr A Found Adv* **2015**, *71* (6), 562–568.
    `https://doi.org/10.1107/S2053273315014473 <https://doi.org/10.1107/S2053273315014473>`_


=================
Table of contents
=================

.. toctree::
    :maxdepth: 1
    :caption: WHAT IS DIFFPY.CMI?

    Overview <overview.rst>

.. toctree::
    :maxdepth: 1
    :caption: GETTING STARTED

    Installation <installation>
    Command-Line Interface <cli-commands>
    Package API <api/diffpy.cmi>

.. toctree::
    :maxdepth: 1
    :caption: AVAILABLE PACKS & PROFILES

    Packs <available-packs>
    Profiles <available-profiles>

.. toctree::
    :maxdepth: 1
    :caption: EXAMPLES & MORE

    Examples <tutorials/index>

.. toctree::
    :maxdepth: 1
    :caption: REFERENCE

    Release notes <release>
    License <license>


=======
Indices
=======

* :ref:`genindex`
* :ref:`search`
