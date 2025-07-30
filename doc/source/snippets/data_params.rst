.. list-table::
   :widths: 2 6 2 2
   :header-rows: 1
   :class: wrap-text

   * - PDF Parameter
     - Description
     - Refineable?
     - Structural or Instrumental?
   * - ``scale``
     - Overall scaling factor between calculated and observed PDFs; sets the absolute intensity.
     - Yes
     - Instrumental
   * - ``qdamp``
     - Damping of PDF peaks due to limited experimental Q-range. Typically affects high-r ripples and overall peak amplitudes.
     - Yes
     - Instrumental
   * - ``qbroad``
     - Instrumental or sample-related broadening of PDF peaks. This is due to the fact that diffraction peaks have different widths as a function of Q.
     - Yes
     - Instrumental
   * - ``qmin``
     - Minimum Q included in the fit; sets the lower bound of the S(Q) integration range.
     - No, from experiment/setup
     - Instrumental
   * - ``qmax``
     - Maximum Q included in the fit; sets the upper bound of the S(Q) integration range.
     - No, from experiment/setup
     - Instrumental
   * - ``rmin``
     - Minimum r (distance) included in the fit; sets the lower bound of the fitting range.
     - No, from experiment/setup
     - Instrumental
   * - ``rmax``
     - Maximum r (distance) included in the fit; sets the upper bound of the fitting range.
     - No, from experiment/setup
     - Instrumental (unless fitting to nanoparticles)
