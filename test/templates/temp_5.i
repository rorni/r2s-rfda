<< -----set initial switches and get nuclear data----- >>
CLOBBER
JSON
GETXS 0
GETDECAY 0
FISPACT
* FNS 5 Minutes Inconel-600
{material}
MIND 1E3
GRAPH 1 2 1 3
UNCERTAINTY 2
HALF
HAZARDS
<< -----irradiation phase----- >>
FLUX    {0}
UNCERT 0
TIME 2 YEARS SPEC
UNCERT 2
FLUX  {1}
TIME 10 YEARS SPEC
LEVEL 100 5
FLUX 0
TIME 0.667 YEARS SPEC
FLUX {2}
TIME 1.330 YEARS SPEC
PULSE 17
  FLUX 0
  TIME 3920 SPEC
  FLUX {3}
  TIME 400 SPEC
ENDPULSE
PULSE 3
  FLUX 0
  TIME 3920 SPEC
  FLUX {4}  
  TIME 400 SPEC
ENDPULSE
<< ----- cooling phase ---- >>
FLUX 0
ZERO
TIME 1 ATOMS
TIME 299 ATOMS
TIME 25 MINS ATOMS
TIME 30 MINS ATOMS
TIME 2 HOURS ATOMS
TIME 2 HOURS ATOMS
TIME 5 HOURS ATOMS
TIME 14 HOURS ATOMS
TIME 2 DAYS ATOMS
TIME 4 DAYS ATOMS
TIME 23 DAYS ATOMS
TIME 60 DAYS ATOMS
TIME 275.25 DAYS ATOMS
TIME 2 YEARS ATOMS
TIME 7 YEARS ATOMS
TIME 20 YEARS ATOMS
TIME 20 YEARS ATOMS
TIME 50 YEARS ATOMS
TIME 900 YEARS ATOMS
END
* END