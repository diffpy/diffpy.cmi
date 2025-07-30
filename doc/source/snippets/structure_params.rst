.. list-table::
   :widths: 2 6 2 2
   :header-rows: 1
   :class: wrap-text

   * - PDF Parameter
     - Description
     - Refineable?
     - Structural or Instrumental?
   * - ``a``, ``b``, ``c``
     - Lattice parameters of the crystal structure.
     - Yes
     - Structural
   * - ``alpha``, ``beta``, ``gamma``
     - Angles between lattice vectors
     - Yes
     - Structural
   * - ``delta1``
     - Constant (r-independent) peak broadening parameter accounting for uniform broadening of PDF peaks due to static disorder or residual instrumental effects.
     - Yes
     - Both
   * - ``delta2``
     - Correlated motion parameter accounting for r-dependent broadening (increases with r) of PDF peaks due to correlated atomic motion.
     - Yes
     - Structural
   * - ``biso`` or ``Uiso``
     - Isotropic atomic displacement parameter (ADP); models thermal vibration/disorder for each atom type. (note: ``biso=8*pi^2*Uiso``)
     - Yes
     - Structural
   * - ``uij``
     - Anisotropic ADPs constrained by space group symmetry.
     - Yes
     - Structural
   * - ``dscale``
     - Correction factor for background or density mismatch.
     - Sometimes; often fixed
     - Instrumental
   * - ``sratio``
     - Ratio of coherent to incoherent scattering, used in some models.
     - Sometimes
     - Instrumental
