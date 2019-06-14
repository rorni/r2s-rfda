<< -----set initial switches and get nuclear data----- >>
CLOBBER
GETXS 0
GETDECAY 0
FISPACT
* FULL TEST
{material}
MIND 1E3
HALF
HAZARDS
TOLERANCE 0 1.0e-3 1.e-9
<< -----irradiation phase----- >>
FLUX    0.05E+00
TIME 1 YEARS ATOMS
FLUX  1.0E+00
TIME 10 MINS ATOMS
<< ----- cooling phase ---- >>
FLUX 0
ZERO
TIME 1 HOURS ATOMS
TIME 23 HOURS ATOMS
TIME 9 DAYS ATOMS
TIME 355 DAYS ATOMS
END
* END