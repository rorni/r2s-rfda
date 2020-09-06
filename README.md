# r2s-rfda
This is a R2S technique implementation. 
It requires FISPACT code installed on your machine. Also path to fispact.exe must present on your path variable.
r2s-rfda requires mckit installed to the python distribution.

## Capabilities

r2s-rfda is a tool for activation calculations by FISPACT code using MCNP input model and FMesh tally for neutron fluxes.
It can form gamma-radiation decay source for MCNP (SDEF) to run SDDR calculations.

## Usage

The following files are needed for calculations:
1. MCNP geometrical model. It contains geometry description and materials. r2s-rfda uses cell names and material composition.
2. FMesh tally file with neutron fluxes.
3. FISPACT template file. It must contain irradiation scenario.
4. r2s-rfda command file. It contains paths to all input files, FISPACT libraries, FMesh tally name and other settings.

Files 1 - 3 are standard and must be familiar to users that need to run SDDR calculations. Command file (4) needs some explanation.
It is ordinary ini file (and must have .ini extension). It must contain three sections:
1. [MODEL]
   Description of the model. The section contains following parameters:
   - mcnp = input.i -- name of MCNP input file.
   - fmesh = fmesh.m -- name of MCNP meshtal file.
   - tally = 4 -- name of FMesh tally to be used in calculations.
   - approach = simple | full -- Calculation approach. full - to run calculations for every mesh voxel. simple - use superposition method.
   - minvol = 0.001 -- minimum volume - option for mckit volume calculations.
   
2. [DATALIB]
   It contains paths to FISPACT data libraries. The format is lib_name = lib_path. lib_name is the same as for FISPACT 'files' file.
   
3. [FISPACT]
   Fispact options.
   - inventory = inventory.temp -- name of FISPACT input template file. It has FISPACT inventory file syntax and contains irradiation scenario.
   - libxs = 1 -- whether to use binary library. 1 - to use text libraries, -1 - to use binary libraries. Binary library must be properly prepared as described in FISPACT manual.
   - norm_flux = 4.5643E+12 -- normalization flux. It is the flux in inventory file for which MCNP calculations were run. Fluxes in every voxel will be normalized respectively.
   
An expample of input file can be found in test folder (r2s_sample.ini).

All input files must be stored in some folder. Then, to run activation calculations run the following commands:
1. r2s-rfda prepare folder
   Reads input files, calculates volumes of cell parts that fall in every fmesh voxel. Creates FISPACT input files.
   
2. r2s-rfda run --threads 10 folder
   Runs FISPACT calculations. For every created case FISPACT is run. threads parameter sets the number of processes (10 tasks will be run in parallel for the example).
   
3. r2s-rfda fetch folder
   Runs fetch operation. During this stage all FISPACT output files are read and merged. Resulting activation data is stored in binary files.
   
4. r2s-rfda source --zero -i 1.e-3 -v 1.e-3 folder sdef_filename time
   Creates decay gamma source (SDEF). time sets time moment for which source must be created (1y, 12d, etc). --zero flag indicates that time is counted since end of irradiation.
   -i and -v options are used to set an intensity and volume thresholds for bin to be included into SDEF. Usually it helps to avoid MCNP error -- low sampling efficiency.

To get help on commands and options you can use --help command. For example:

r2s-rfda --help
r2s-rfda source --help
