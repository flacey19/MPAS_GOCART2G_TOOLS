# MPAS-GOCART2G Instructions

The instructions are tailored for running MPAS-GOCART2G on the NSF NCAR HPC system called Derecho.

These instructions combine information from both the <a href="https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/" target="_blank" rel="noopener noreferrer">MPAS Tutorial - Practice Guide</a> and the specific instructions for running with GOCART-2G aerosols. Be sure to go to the <a href="https://mpas-dev.github.io/" target="_blank" rel="noopener noreferrer">MPAS Home page</a> and <a href="https://www2.mmm.ucar.edu/projects/mpas/site/index.html" target="_blank" rel="noopener noreferrer">MPAS-Atmosphere webpage</a> where there is a lot more information and documentation.

## **Table of Contents**

**Background chapter** provides a brief description of the MPAS-GOCART-2G model. 

**Chapter 1** gives instructions on running a case where all the input files are provided. It allows the new user to become familiar with the workflow in preparing a MPAS-GOCART2G simulation and is great for ensuring that the user has configured their system properly. 

**Chapter 2** provides information on setting up your own case using the same grid mesh as in chapter 1 but running a different time period, including where to obtain input files and running the program *init\_atmosphere* which sets up the MPAS-GOCART2G simulation. 

**Chapter 3** provides information on running with a variable resolution grid mesh and setting up different variable resolution grids. 

**Chapter 4** provides instructions for viewing MPAS-GOCART2G output using uxarray in Python scripts. 

**Appendix A** explains how to download MERRA2 files.

**Appendix B** describes ways to visualize MPAS-GOCART2G output.

### Quick workflow guide for first-time users

If you are new to MPAS-GOCART2G, use this order:

1. Read the background section only to understand the model and terminology.
2. Complete Chapter 1 to build and test the example case with pre-provided inputs.
3. Use Chapter 2 to prepare the files needed for your own case.
4. Once the case is set up, verify that the generated `namelist.*` and `streams.*` files are in the run directory.
5. Submit the job and check model output files before trying a larger simulation.

## **Background chapter Familiarizing yourself with the physics suite to run a MPAS-GOCART2G simulation**

The MPAS-GOCART2G model has been developed as part of the NSF NCAR’s vision to move towards a unified modeling framework and links the MPAS-A dynamical core (Skamarock et al., 2012) to the GOCART2G chemical mechanism (Collow et al., 2024). The GOCART2G module adds 30 new scalars to represent eight tropospheric aerosol species and their precursors. Major aerosol species represented by GOCART2G include black carbon (BC), brown carbon (BrC), organic carbon (OC), sulfate, nitrate, ammonium, dust, and sea-salt. BC, BrC, and OC are present in hydrophobic and hydrophilic modes with an e-folding lifetime of 2.5 days for conversion of hydrophobic mode to hydrophilic mode. All the aerosol species are subjected to gravitational settling, dry deposition, and wet deposition processes. Gravitational settling is calculated following the parameterization of Fuchs (1965). Dry deposition velocity of aerosol and precursor species is estimated using the Wesely (1989) scheme. Resolved scale wet deposition of aerosols is calculated using aerosol-aware Thompson-Eidhammer 2014 scheme. Convective transport of all chemical constituents and wet deposition is simulated using nTiedtke scheme.  

The implementation of GOCART-2G is illustrated in Figure 1 and can be categorized into four layers as the Input Layer, the Model Initialization and Temporal Update Layer, The Physics and Dynamics Layer, and the Chemistry and Diagnostics layer:

```{figure} static/MPAS_GOCART2G_Inst_F1.png
:alt: The MPAS-A, chemistry, and external tools system flowchart
:align: center
:width: 100%

**Figure 1.** The MPAS-A system (gray and blue boxes) and chemistry and GOCART-2G system (green and yellow boxes).
```

Anthropogenic emissions are represented using the CAMS emissions inventory (Soulie et al., 2023). BC emissions from all sources are assumed to be 80% in hydrophobic mode while BrC and OC emissions are assumed to be 50% in hydrophobic mode at the time of emissions. The remaining fractions are considered to be hydrophilic. Anthropogenic emissions from the aviation sector (if provided as input to the model) are distributed in three layers: Landing and Take off emissions are assigned to the 100 m layer, Continuous Climb and Descent Operations (CDO) emissions are assigned to 100 m \- 9 km layer and the remaining aircraft flight operations are distributed between 9 and 10 km altitude layers. Emissions from all other anthropogenic sources are emitted within the lowest 100 m. 

Biogenic emissions are read from pre-calculated emissions files available in the CAMS inventory (i.e., they are *not* computed at each emission time step with inputs from local temperature and PAR). CAMS v4 biogenic emissions include only isoprene emissions, therefore CAMS v3.1 is used and CAMS 2019 biogenic emissions are applied to MPAS-GOCART2G simulations for case studies for all years\. Following Collow et al. (2024), isoprene, monoterpene, and other terpene emissions are assigned to the hydrophilic mode of the OC. Since their emissions occur at the tree top, they are only emitted in the lowest model layer.   

Biomass burning emissions in MPAS-GOCART-2G are represented using FINN version 2.5.1 (Wiedinmyer et al., 2023). A climatological diurnal profile is applied to distribute the emissions to hourly values. MPAS-GOCART-2G then uniformly mixes the biomass burning emissions within the PBL. To ensure model stability and prevent unrealistically high Aerosol Optical Depth (AOD) values from biomass burning, the model limits biomass burning emissions in such a way that AOD from biomass burning emissions over all time steps in a day cannot exceed AOD = 30.0.  

Dust aerosols are represented using five size bins (radii of 0.73, 1.4, 2.4, 4.5, and 8.0 µm) and their emissions are calculated online within the model utilizing the Ginoux et al. (2001) parameterization but with the dimensionless factor C set to 0.65 µg s<sup>2</sup> m<sup>-5</sup> as in (Zhao et al., 2010). Static geographical fields such as “erod” (erodibility representing the areas from where dust aerosols can be emitted), clayfrac and sandfrac required for dust emissions are mapped to the MPAS-GOCART domain along with the processing of other static geographical fields (see Section 1.3 of <a href="https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/" target="_blank" rel="noopener noreferrer">MPAS Tutorial - Practice Guide</a> for processing these fields). Sea-salt aerosols also use five size bins, specifically with radii of 0.079, 0.316, 1.119, 2.818, and 7.772 µm. Emissions for sea-salt are calculated using the Gong (2003) wind-driven parameterization, but this includes two key modifications: first, friction velocity has replaced the 10m wind speed, which is required for tuning the parameterization's constants; and second, a correction term dependent on sea surface temperature was added. This temperature-dependent modification is similar to the approach by Jaegle et al. (2011) but was specifically tuned to improve agreement between the simulated sea-salt AOD and MODIS-retrieved AOD. The GOCART2G’s default scale-aware factor of 0.6 at grid spacings exceeding 200 km to 0.35 at grid spacings less than 12 km has been applied to model sea-salt emissions as a function of model grid spacing. 

### **References**

- Collow, A. B., Colarco, P. R., da Silva, A. M., Buchard, V., Bian, H., Chin, M., Das, S., Govindaraju, R., Kim, D., and Aquila, V.: Benchmarking GOCART-2G in the Goddard Earth Observing System (GEOS), Geosci. Model Dev., 17, 1443–1468, https://doi.org/10.5194/gmd-17-1443-2024, 2024. 
- Gong, S. L.: A parameterization of sea-salt aerosol source function for sub- and super-micron particles, Glob. Biogeochem. Cycles, 17, https://doi.org/10.1029/2003GB002079, 2003.
- Ginoux, P., Chin, M., Tegen, I., Prospero, J. M., Holben, B., Dubovik, O., and Lin, S.-J.: Sources and distributions of dust aerosols simulated with the GOCART model, J. Geophys. Res. Atmos., 106, 20255–20273, https://doi.org/10.1029/2000JD000053, 2001.
- Jaeglé, L., Quinn, P. K., Bates, T. S., Alexander, B., and Lin, J.-T.: Global distribution of sea salt aerosols: new constraints from in situ and remote sensing observations, Atmos. Chem. Phys., 11, 3137–3157, https://doi.org/10.5194/acp-11-3137-2011, 2011.
- Skamarock, W. C., Klemp, J. B., Duda, M. G., Fowler, L. D., Park, S.-H., and Ringler, T. D.: A Multiscale Nonhydrostatic Atmospheric Model Using Centroidal Voronoi Tesselations and C-Grid Staggering, https://doi.org/10.1175/MWR-D-11-00215.1, 2012.
- Soulie, A.; Granier, C.; Darras, S.; Zilbermann, N.; Doumbia, T.; Guevara, M.; Jalkanen, J.-P.; Keita, S.; Liousse, C.; Crippa, M.; Guizzardi, D.; Hoesly, R.; Smith, S. Global Anthropogenic Emissions (CAMS-GLOB-ANT) for the Copernicus Atmosphere Monitoring Service Simulations of Air Quality Forecasts and Reanalyses. Earth System Science Data Discussions 2023, 1–45. https://doi.org/10.5194/essd-2023-306.
- Wesely, M. L.: Parameterization of surface resistances to gaseous dry deposition in regional-scale numerical models, Atmos. Environ. 1967, 23, 1293–1304, https://doi.org/10.1016/0004-6981(89)90153-4, 1989.
- Wiedinmyer, C.; Kimura, Y.; McDonald-Buller, E. C.; Emmons, L. K.; Buchholz, R. R.; Tang, W.; Seto, K.; Joseph, M. B.; Barsanti, K. C.; Carlton, A. G.; Yokelson, R. The Fire Inventory from NCAR Version 2.5: An Updated Global Fire Emissions Model for Climate and Chemistry Applications. Geoscientific Model Development 2023, 16 (13), 3873–3891. https://doi.org/10.5194/gmd-16-3873-2023.
- Zhao, C., Liu, X., Leung, L. R., Johnson, B., McFarlane, S. A., Gustafson, W. I. J., Fast, J. D., and Easter, R.: The spatial distribution of mineral dust and its shortwave radiative forcing over North Africa: modeling sensitivities to dust emissions and aerosol size treatments, Atmos. Chem. Phys., 10, 8821–8838, https://doi.org/10.5194/acp-10-8821-2010, 2010. 


### **Physics Configuration with MPAS-GOCART2G**

A new physics suite named "MPAS-GOCART2G" has been developed based on the “convection\_permitting” MPAS-A physics suite. Please see the physics component of the namelist.atmosphere below. The PBL mixing of chemical constituents is calculated inside the MYNN PBL scheme. Note that deposition velocity of chemical constituents is still calculated by GOCART-2G and is passed to MYNN for deposition along with the turbulent mixing. Convective transport of tracers is performed using the nTiedtke scheme. In addition to setting these options in the physics part of the namelist, additional variables need to be set in the “chemistry” part of the namelist (see in bold font below under “chemistry” components). GOCART-2G aerosols also interact with the Thompson cloud microphysics and RRTMG radiation schemes.  

\&physics  
    config\_sst\_update \= false  
    config\_sstdiurn\_update \= false  
    config\_deepsoiltemp\_update \= false  
    config\_radtlw\_interval \= '00:30:00'  
    config\_radtsw\_interval \= '00:30:00'  
    config\_bucket\_update \= 'none'  
    config\_physics\_suite \= 'MPAS\-GOCART2G'  
    config\_microp\_scheme \= 'mp\_thompson\_gocart2G'  
    config\_pbl\_scheme \= 'bl\_mynn'        
    config\_mynn\_mixchems \= true  
    config\_convection\_scheme \= 'cu\_ntiedtke'  
    config\_ntiedtke\_ctrchems \= true  
    config\_ntiedtke\_scavchems \= true  
/

\&chemistry  
    config\_gocart2G\_do\_CA2Gbc       \= true  
    config\_gocart2G\_do\_CA2Gbr       \= true  
    config\_gocart2G\_do\_CA2Goc       \= true  
    config\_gocart2G\_do\_SOA2G        \= true  
    config\_gocart2G\_do\_DU2G         \= true  
    config\_gocart2G\_do\_NI2G         \= true  
    config\_gocart2G\_do\_SS2G         \= true  
    config\_gocart2G\_do\_SU2G         \= true  
    **config\_gocart2G\_toRRTMG \= true**  
    **config\_gocart2G\_toMYNN  \= true**  
    **config\_gocart2G\_toTHOM \= true**  
    **config\_gocart2G\_toNTIEDTKE \= true**  
/

A detailed documentation of all the chemistry namelist options will be generated using Registry\*.xml files to preserve consistency between the model registry files and documentation. 

### **Workflow for preparing a MPAS-GOCART2G simulation**

Figure 2 displays the workflow for preparing a MPAS-GOCART2G simulation. The lefthand column are detailed in Chapter 1 and the righthand column (boxes outlined in purple) are described in Chapter 2\. 

```{figure} static/MPAS_GOCART2G_Inst_F2.png
:alt: MPAS-GOCART2G Workflow Diagram
:align: center
:width: 100%

**Figure 2.** Workflow for preparing MPAS-GOCART2G simulations. Boxes shaded in blue and red are described in the MPAS-A Tutorial Guide and MPAS-GOCART2G github README.md file, respectively. Boxes shaded in yellow are tasks specific to the GOCART-2G configuration. The gray boxes are MPAS-ready files from the pre-processing steps and the green boxes are the MPAS-GOCART2G executables and output files.
```

## **Chapter 1 Becoming Familiar with running a MPAS-GOCART2G Simulation**

### Prerequisites

MPAS-A requires that your Derecho environment is set up with available capabilities, such as MPI-2, NetCDF-4, PnetCDF, and PIO libraries. To learn how to set up your environment, please see the instructions in Chapter 0 of the <a href="https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/" target="_blank" rel="noopener noreferrer">MPAS Tutorial - Practice Guide</a>. 

Note: If you are using tcsh instead of bash, the PATH can be set as:  
setenv PATH /glade/campaign/mmm/wmr/mpas\_tutorial/metis/bin:${PATH}

### Download MPAS-GOCART2G from Github:

First, go to a directory where you would like to store the MPAS-GOCART2G source code and processing toos, such as the /glade/work/$USER directory where $USER is your login name on Derecho.  
cd  /glade/work/$USER

Depending on the version and host repository of the model, especially for development branches, you may need to set up an SSH key for the Derecho environment. Instructions for this can be found on this page <a href="https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent" target="_blank" rel="noopener noreferrer">Populating GitHub SSH Keys and Agents</a>.

Next, clone the code from Github or copy a version from campaign storage.   
git clone git@github.com:NCAR/MPAS-GOCART2G.git

Or copy the code from the ACOM campaign storage location:

cp \-rp /glade/campaign/acom/MUSICA/MPAS/MPAS-GOCART2G .  
   
   
This will give you all of the tools needed to run MPAS-GOCART2g, including the source code in the *gocartMPAS* directory. The top level directory should include the following:  
ls \-l MPAS_GOCART2G/  

total 20
drwxr-xr-x 7 USER ncar 4096 Oct 22 09:43 gocartMPAS
drwxr-xr-x 2 USER ncar 4096 Oct 22 09:43 init_MPAS-GOCART2G
-rw-r--r-- 1 USER ncar 2311 Oct 22 09:43 LICENSE
-rw-r--r-- 1 USER ncar  252 Oct 22 09:43 README.md
drwxr-xr-x 2 USER ncar 4096 Oct 22 09:43 UPTEMPO

Where the source code is located in gocartMPAS. Navigate to this directory and the following should be the directory contents:

cd MPAS-GOCART2G/gocartMPAS
ls \-l

total 74  
drwxrwxr-x+      4 USER acom-weather 16384 Sep 15 11:33 cmake/  
\-rwxrwxr-x+     1 USER acom-weather  8128 Sep 15 11:33 CMakeLists.txt\*  
drwxrwxr-x+      3 USER acom-weather 16384 Sep 15 11:33 docs/  
\-rwxrwxr-x+     1 USER acom-weather  3131 Sep 15 11:33 INSTALL\*  
\-rwxrwxr-x+     1 USER acom-weather  2311 Sep 15 11:33 LICENSE\*  
\-rwxrwxr-x+     1 USER acom-weather 55424 Sep 15 11:33 Makefile\*  
\-rwxrwxr-x+     1 USER acom-weather  2811 Sep 15 11:33 README.md\*  
drwxrwxr-x+     14 USER acom-weather 16384 Sep 15 11:33 src/  
drwxrwxr-x+      5 USER acom-weather 16384 Sep 15 11:33 testing\_and\_setup/

### Compile MPAS-GOCART2G:

Before starting, make sure you have all of the following in place:

- Access to the Derecho HPC environment and a valid project account key (`$PROJ`)
- A working directory on Derecho or another supported HPC system
- Either a cloned copy of the MPAS-GOCART2G repository or a local copy from campaign storage
- A valid GitHub SSH key if you are cloning from GitHub (see the instructions in the background section)

If those prerequisties are met, compiling MPAS-GOCART2G follows the same steps as that for MPAS-A compilation. Please follow the steps outlined in chapter 1.2 of the <a href="https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/" target="_blank" rel="noopener noreferrer">MPAS Tutorial - Practice Guide</a>. For those who are familiar with compiling MPAS-A, the commands are the following:

```
cd gocartMPAS  
qcmd -A $PROJ -- make gnu CORE=init_atmosphere GOCART2G=true AUTOCLEAN=true  
qcmd -A $PROJ -- make gnu CORE=atmosphere GOCART2G=true AUTOCLEAN=true
```

where $PROJ is the NCAR HPC Derecho project account key that your work is charged to. If you don’t have access to Derecho, please refer to job submission guidelines for your local HPC. If you want to debug your simulation because of an error, you can compile the code with the DEBUG option turned on:

```
qcmd -A $PROJ -- make gnu CORE=init_atmosphere GOCART2G=true AUTOCLEAN=true DEBUG=true  
qcmd -A $PROJ -- make gnu CORE=atmosphere GOCART2G=true AUTOCLEAN=true DEBUG=true
```

### What a successful compile should produce

When both builds finish successfully, your repository directory should contain the executables, namelist files, and stream files needed to set up and run MPAS-GOCART2G.

Expected files include:

init\_atmosphere\_model\*  
atmosphere\_model\*  
build\_tables\*

namelist.init\_atmosphere  
namelist.atmosphere

stream\_list.atmosphere.output   
streams.atmosphere  
streams.init\_atmosphere

For more information about these files, see the <a href="https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/" target="_blank" rel="noopener noreferrer">MPAS Tutorial - Practice Guide</a>. 

### Build the Thompson lookup tables

**The next step** is to create the look-up tables used by the Thompson microphysics scheme by issuing the following command. Depending on the version of MPAS-GOCART2G you are using, these table may already be compiled within the model, so check for them in this directory first:

src/core\_atmosphere/physics/physics\_wrf/files/ 

If they are not present they must be built using:

./build\_tables

It will take 10-15 minutes to complete this job. Once it is finished, the following files now reside in the directory.  
   MP\_THOMPSON\_QRacrQG\_DATA.DBL  
   MP\_THOMPSON\_QRacrQS\_DATA.DBL  
   MP\_THOMPSON\_freezeH2O\_DATA.DBL  
   MP\_THOMPSON\_QIautQS\_DATA.DBL  
As suggested by the program output, copy these files to the src/core\_atmosphere/physics/physics\_wrf/files/ directory.

### Checkpoint: what you should have before moving on

At this point, you should be able to confirm all of the following:

- The MPAS-GOCART2G source code is present in `gocartMPAS/`
- The model executables were built successfully
- The lookup tables were generated and copied to the physics files directory
- You are ready to create and submit a case run directory

If any of these items are missing, go back and finish the compile step before proceeding.

### MPAS-GOCART2G I/O: 

Similar to MPAS-A, the reading and writing of model fields MPAS-GOCART2G is handled by user-configurable streams. We refer the users to MPAS-A User’s guide to familiarize themselves with these streams (<a href="https://www2.mmm.ucar.edu/projects/mpas/site/documentation/users_guide/configuring_io.html" target="_blank" rel="noopener noreferrer">MPAS IO</a>). In addition to the standard MPAS output, the MPAS-GOCART2G I/O requires input streams for anthropogenic, biomass burning, and biogenic emissions and output streams for three-dimensional output of aerosols and related variables, diagnostic variables (e.g., total PM2.5, total and individual species AOD at 550 nm, Angstrom exponent, etc.). Example stream files are provided with the MPAS-GOCART2G release.    

### Running MPAS-GOCART2G: Example 1

The practice example (Example-1) is a global 60-km uniform grid mesh with a start date of 15 October 2024 at 00:00 UTC. The simulation can be run for 5 days, but for testing whether MPAS-GOCART2G works or not, **this example will perform a 3-hour simulation** which should take about 10 minutes of wallclock time. Note, it is okay to run a 5-day simulation, but be aware of the computational costs. We find that the 5-day simulation takes about 8 hours of wallclock time for the number of CPUs requested in the submission script. 

It is best to run MPAS\_GOCART2G on the Derecho scratch directory. Begin by creating a run directory and moving to that directory.

mkdir \-p /glade/derecho/scratch/$USER/gocartMPAS/Example-1  
cd /glade/derecho/scratch/$USER/gocartMPAS/Example-1

For this example, we have provided a shell script that will set up and build your simulation directory and submit the jobs. You can copy this script into your new directory using the following command.

cp /glade/campaign/acom/MUSICA/MPAS/scripts/submit\_mpas\_gocart.bash .

This copies a helper script that will set up the case and submit the jobs. The script is configurable and can be modified for other case studies (for example, the workflow in Chapter 2).

In the script, you will need to change line 11 (`proj=P19010000`) to use the Derecho Account Key that you can use to submit your jobs. If you don’t have access to Derecho, please refer to job submission guidelines for your local HPC.

*What does the script do?*
The script creates a new directory in which the *init\_atmosphere* and *atmosphere* executables are run. The directory’s name is based on the start date of the simulation. In this example, the script creates the directory, 20241015/.

The commands within the script are documented in the file, and the workflow it implements is more structured than the original exercise description. The script performs the following actions in order:

1. Set simulation controls and run metadata: start date, forecast length, grid name, project account, and whether to create the static chemistry file and/or nudging stage.
2. Define the necessary directory paths for the MPAS-GOCART2G source code, the forecast output directory, GFS meteorology, MERRA-2 initialization files, emissions, background oxidant fields, grid files, and the namelist/stream templates.
3. Create the case directory (for example, RUN\_001/20241015) and compute the simulation start and end dates used to populate the namelist templates.
4. Copy the standard namelist and stream templates from the local input directories, then render them in place by replacing the grid placeholder (`__GRID_NAME__`) and writing the final `namelist.*` and `streams.*` files to the run directory.
5. Link the default MPAS grid, static field files, background data, emissions, GFS/MERRA files, and compiled executables (`init_atmosphere_model`, `atmosphere_model`) into the case directory so that the model can run without manual file copying.
6. Prepare and write the PBS job scripts for the required model stages. The default workflow is `static` init-atmosphere, then `chem` init-atmosphere, and then the forecast atmosphere step. If `run_nudging=TRUE`, the script also prepares a `nudging` init-atmosphere stage followed by the nudged atmosphere stage.
7. Submit the generated job scripts on Derecho with the project account and core allocation configured in the script. The atmosphere jobs are staged after the required init-atmosphere jobs complete so the case builds in the proper order.

Review the script to ensure the project number, start date, forecast length, and paths for the source code and output files (`path_fcst`) are correct. Then submit the script on Derecho:

./submit\_mpas\_gocart.bash

The script automatically creates the files needed for the case setup, including the generated namelists and stream files in the run directory. This is especially useful for new users because it reduces the number of manual edits needed when setting up a case that differs from the tutorial example.

The init\_atmosphere code creates the init\_chems\_emissions.nc file, which contains initial conditions for meteorology, static geographical fields, and all GOCART2G chemical (both gas and aerosol) species as well as emissions from anthropogenic, biomass burning, and biogenic sources.

As the atmosphere code integrates through the simulation, the following hourly output files are created:

* 163842.output.2024-10-15\_0\*.00.00.nc — These files contain selected variables (including aerosol concentrations) specified in “stream\_list.output”.   

You will not generate the 163842.restart.2024-10\*.nc files with this example run as the defined restart timestep is 12:00 hours, and the simulation run time is only 3 hours. Restart files are checkpoints of the model state and can be used to restart a simulation from the point they are written.  

Chapter 2 (Section 5\) discusses the definition of output in the streams file in more detail allowing for more control and flexibility in MPAS-GOCART2G simulations. 

### Quick Viewing of the Model Results

For viewing model output to confirm that the model is running correctly, we recommend converting the model output to a regular latitude-longitude grid using the *convert\_mpas* tool. The converted output (on a latitude-longitude grid) can then be viewed using the *ncview* command or with plotting scripts. 

Section 3.4 of the <a href="https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/" target="_blank" rel="noopener noreferrer">MPAS Tutorial - Practice Guide</a>) describes how to obtain the *convert\_mpas* tool and compile it. An example command line for running *convert\_mpas* (we recommend adding the full path of convert\_mpas to your $PATH so that you can use it in any directory) is given here.

convert\_mpas x1.163842.static\_chems.nc 163842.output.2024-10-15\_03.00.00.nc

When *convert\_mpas* is run, it creates a file called *latlon.nc*. Note, if you wish to convert other MPAS-GOCART2G files to a latitude-longitude grid, then you must rename or delete the current latlon.nc file.

More information about plotting MPAS-GOCART2G output is given in **Appendix B**. Specifically, we recommend using the uxarray within python to plot results on the native grid mesh. 

## **Chapter 2 Setting Up a Different Case**  {#chapter-2-setting-up-a-different-case}

### Introduction

This chapter provides information on setting up a different case using the same grid mesh as in chapter 1 but running a different time period. A description is given on where to obtain input files for running the program *init\_atmosphere* which sets up the MPAS-GOCART2G simulation. The chapter is structured by the four types of input files needed to run a new case:

1. Meteorology fields
2. MERRA-2 files for initial chemical conditions
3. Emissions files (anthropogenic, biogenic, and biomass burning)
4. Background oxidant and aerosol optical-property data

If any one of these is missing or incorrectly formatted, the model setup will not be complete.

### Before you begin: quick checklist

Before moving into the detailed steps, confirm that you have:

- a valid Derecho project account (`$PROJ`), if using Derecho
- the MPAS-GOCART2G source code compiled and available
- a working directory for pre-processing files
- access to the required input datasets from MERRA-2, CAMS, FINN, and the MPAS campaign directories

At the end of this chapter, the goal is to have all required inputs staged and ready so that the `init_atmosphere` setup step can run cleanly.

### 1. Preparation of Meteorology Fields

A 2-week spin-up is needed before the start of your case study, so you should obtain meteorology input data beginning 2 weeks before the case start date. The end date should match the end date of the case study.

For a first case, it is strongly recommended that you use the same 60-km uniform grid mesh as Chapter 1. Once you are comfortable with the setup, you can experiment with other mesh configurations.

The MPAS-A tutorial contains the detailed instructions for generating the required meteorology input files. In practice, you should follow the tutorial’s preparation steps to create a `met_data/` directory containing files such as:

```text
GFS:yyyy-mm-dd-hh
ERA5:yyyy-mm-dd-hh
```

These files are then converted into the intermediate file format expected by `init_atmosphere_model`. If you are planning on runnijng using meteorlogical nidging, you will need to generate these files at the apporpirate timesteps (usually 6 hours) for the entire simulation period. 

Expected outcome: after this step, you should have a complete `met_data/` directory covering the necessary spin-up and simulation window.


### 2. Getting MERRA data and convert to MPAS intermediate files

MERRA2 files provide initial concentrations for the predicted fields as well as HNO3, NH3, CO, and isoprene. The HNO3 and NH3 are used for the thermodynamics calculation of the SO4-NH4-NO3 system. Isoprene and CO are used for the simplified SOA production. 

Appendix A provides information on how to download MERRA data from the NASA Earthdata site. You will need to have an NASA Earthdata user name and password to download the data when running the python script. 

Once the MERRA input files are in a local directory, converting the MERRA data to the MPAS-A grid mesh can be done with the python MERRA processing script, *run\_processing.py*. The script and instructions for running the script can be found on the <a href="https://github.com/NCAR_MPAS-GOCART2G/init_MPAS-GOCART2G" target="_blank" rel="noopener noreferrer">init_MPAS_GOCART2G</a>.

Expected outcome: after this step, you should have the chemically prepared MERRA-2 intermediate files in the correct format for the MPAS grid.

### 3. Preparation of the Emissions via UPTEMPO

The emissions preprocessor, UPTEMPO, is a Python tool used to prepare the anthropogenic, biogenic, and biomass burning emissions needed for MPAS-GOCART2G.

You can obtain UPTEMPO from the MPAS-GOCART2G repository, or clone it directly with:

git clone https://github.com/NCAR/MPAS-GOCART2G/UPTEMPO UPTEMPO

To run UPTEMPO you can either use your Terminal or submit a job to Derecho’s PBS system. 

Go to the <a href="https://github.com/NCAR_MPAS-GOCART2G/UPTEMPO" target="_blank" rel="noopener noreferrer">UPTEMPO</a> and follow the instructions in the README files.   

#### Anthropogenic emissions from CAMS

Use the instructions in `README_CAMS.md` and the configuration file `config_cams_anth_regrid.yaml`.

This file includes the CAMS v6.2 emissions directories and the MPAS uniform 60-km grid configuration. If the required year is not already available on Derecho, download the needed files from the ECCAD database. See the <a href="https://eccad.aeris-data.fr/user_guide/" target="_blank" rel="noopener noreferrer">ECCAD Users Guide</a>.

Important: download all sectors. GOCART-2G requires sector-resolved emissions for different species.

#### Biogenic emissions from CAMS

Use `README_CAMS_BIOG.md`.

Biogenic emissions are based on a climatological dataset, so a specific year is not required. The example setup uses 2019 as a placeholder; the resulting fields are climatological and do not represent a specific year.

#### Biomass burning emissions from FINN2.5

Use `README_FINN.md`.

To obtain FINN v2.5 data:

- For 2012-2023, use the data from the Geoscience Data Exchange (GDEX) archive: <a href="https://gdex.ucar.edu/datasets/d312009/" target="_blank" rel="noopener noreferrer">GDEX Fire Inventory from NCAR database</a>
- For 2024-present, use the near-real-time daily files from <a href="https://www.acom.ucar.edu/acresp/MODELING/finn_emis_txt/" target="_blank" rel="noopener noreferrer">FINN Emission text files</a>

The data file type depends on the period:

- annual files: use `file_type: 'annual'`
- daily files: use `file_type: 'daily'`

After downloading the files, copy them to a local working directory and decompress them as needed using `gunzip` on Linux.

Expected outcome: after this step, you should have processed anthropogenic, biogenic, and biomass-burning emission files ready to be linked into the case run directory.

### 4. Background Oxidants Data and Aerosol Optical Properties Data

Background oxidant data is currently produced using climatological GMI simulations. These background oxidant data files are located in the following directory:

/glade/campaign/acom/MUSICA/MPAS/input/BACKGROUND

The *submit\_mpas\_gocart.bash* script links to this directory, so no changes by the user are needed.

Aerosol optical properties are from Chin et al., 2002\. These data files are located in the following directory:

/glade/campaign/acom/MUSICA/MPAS/input/optics\_files

Again, the example submission script links here automatically.

If you would like to use different background or aerosol optical property data files, then simply create those files in the same format as those provided in the directory and modify the *submit\_mpas\_gocart.bash* script to link to the new files.   

*Note:* In the future, obtaining the background oxidants data from WACCM output will become available.  

### Checkpoint before setting up the case

At this point, you should have the following prepared and ready:

- meteorology files covering the spin-up and simulation period
- MERRA-2 files converted to MPAS-compatible format
- processed emissions files from UPTEMPO
- background oxidant and optical property input files

Once these are all in place, the next steps are to modify `streams.init_atmosphere` and `streams.atmosphere`, then create and submit the new case.

### 5. Modification of streams.init\_atmosphere and streams.atmosphere

For a new case, you usually do not edit the compiled `streams.*` and `namelist.*` files in the source tree. Instead, the run script generates a case-specific copy from templates stored in the model input directories. This is especially important now that the example `submit_mpas_gocart.bash` script generates these files automatically from template files and substitutes the case metadata (for example, the grid name via `__GRID_NAME__`).

The typical workflow is:

1. Start from the template files in the model source tree.
2. Copy them into the case run directory.
3. Replace placeholders such as `__GRID_NAME__`.
4. Update any file names, emission stream names, or output selections for the new case.
5. Run the generated `init_atmosphere` or `atmosphere` job using the case-specific `namelist.*` and `streams.*` files.

This is the recommended approach because it keeps the setup reproducible and avoids editing the original compiled templates by hand.

For more information about what these files contain and how they are used, see <a href="https://www2.mmm.ucar.edu/projects/mpas/site/documentation/users_guide/configuring_io.html" target="_blank" rel="noopener noreferrer">Chapter 5 of the MPAS User’s Guide</a>. For MPAS-GOCART2G, the essential point is that the model needs stream definitions for anthropogenic, biomass-burning, and biogenic emissions, plus the standard output variables you want to save.

### What to check in a new case

When you create a new case, the emission file names in the stream files often differ from the default template values. Therefore, after the script creates the case-specific files, review `streams.atmosphere` and `streams.init_atmosphere` and confirm that the file paths and stream names match the files generated in the emissions preprocessing step.

The simplest workflow is:

- edit the templates before submitting the case if the change is systematic, or
- edit the generated case files in the run directory after the script has created them if the change is case specific.

The example submission script is designed to link the stream files correctly and generate the matching PBS job files. It calls commands like:

```bash
mpiexec ./init_atmosphere_model -n <namelist> -s <stream>
mpiexec ./atmosphere_model -n <namelist> -s <stream>
```

This ensures the namelist, stream, and job submission files stay consistent for each model stage.

### Adding a custom output stream

For user-defined output, follow the instructions in Section 6.2 of the <a href="https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/" target="_blank" rel="noopener noreferrer">MPAS Tutorial - Practice Guide</a>. In short, output streams can be defined either by listing variables directly in the stream block or by referencing a separate `stream_list` file.

#### Option 1: define variables directly in `streams.atmosphere`

```xml
<stream name="sfc_winds"
        type="output"
        filename_template="surface_winds.$Y-$M-$D_$h.nc"
        filename_interval="output_interval"
        output_interval="60:00">

    <var name="u10"/>
    <var name="v10"/>
</stream>
```
```

#### Option 2: define a separate `stream_list` file

Create a file named `stream_list.sfc_winds` containing:

```text
u10
v10
```

Then add the following to `streams.atmosphere`:

```xml
<stream name="sfc_winds"
        type="output"
        io_type="pnetcdf,cdf5"
        filename_template="surface_winds.$Y-$M-$D_$h.nc"
        output_interval="00_01:00:00">
    <file name="stream_list.sfc_winds"/>
</stream>
```

This is the same stream definition but it uses a text file to list the output variables instead of writing each variable directly in the XML block.

### Generated `stream_list.*` files

When MPAS-GOCART2G is compiled, a number of `stream_list.atmosphere.*` files are created. The standard files are:

```text
stream_list.atmosphere.diagnostics
stream_list.atmosphere.output
stream_list.atmosphere.surface
```

These files define which diagnostic and output variables are written during the simulation. For a new case, review these files after the script has generated the case directory to confirm that the correct output variables and emission streams are in place.

If you are following the template-driven workflow in the `submit_mpas_gocart.bash` this is usually the point at which you should check the generated files rather than editing the source templates directly or add in new user-defined stream_list files and fields.

## **Appendix A:  Downloading MERRA2 Files** 

This section describes the procedure for (1) downloading, (2) preparing, and (3) generating the MPAS required MERRA2 fields for GOCART simulations using aerosol and nitrate precursor concentrations. 

Note: To accommodate the need for a 2-week spin-up of the gases and aerosols for MPAS-GOCART2G simulations, be sure to obtain and process MERRA data for the spin-up period as well as the simulation time frame. 

Two different sets of MERRA2 files are needed to populate the chemical fields needed for GOCART, this first being for aerosol species “inst3\_3d\_aer\_Nv” and the second being for the gaseous species “inst0\_3d\_ovp\_Nv”. 

To download the correct files, the first step is to copy the following shell script into a temporary location with adequate storage capacity for processing (\~15 Gb per day needed), for the purposes of this example we will assume this is completed on Derecho’s scratch directory: 

`mkdir /glade/derecho/scratch/$USER/MERRA_TEST/`  
`cd /glade/derecho/scratch/$USER/MERRA_TEST/`  
`mkdir SAT_FILES`  
`cd SAT_FILES` 

Next copy the download script from the MPAS campaign storage:

`cp /glade/campaign/acom/MUSICA/MPAS/input/MERRA2/download_merra.sh .`

Modify the download script starting on line 98 to replace the list of files you will need corresponding to your simulation time. You can do this manually by modifying the file or by generating a list of the files from Earthdata. Make sure to have both the “aer” and “ovp” files for the correct time listed. (NOTE: MERRA2 “ovp” files are not available after 2019 due to shifts in assimilation products. While we are working on a long term fix using other NASA products, for simulations after 2019, please use the 2019 files and a two-week spinup if needed).  

Here is an example section of the script targeting five days in October 2019 that you can should edit for downloading:

`fetch_urls <<'EDSCEOF'`  
`https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/M2I3NVAER.5.12.4/2019/10/MERRA2_400.inst3_3d_aer_Nv.20191015.nc4`  
`https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/M2I3NVAER.5.12.4/2019/10/MERRA2_400.inst3_3d_aer_Nv.20191016.nc4`  
`https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/M2I3NVAER.5.12.4/2019/10/MERRA2_400.inst3_3d_aer_Nv.20191017.nc4`  
`https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/M2I3NVAER.5.12.4/2019/10/MERRA2_400.inst3_3d_aer_Nv.20191018.nc4`  
`https://data.gesdisc.earthdata.nasa.gov/data/MERRA2/M2I3NVAER.5.12.4/2019/10/MERRA2_400.inst3_3d_aer_Nv.20191019.nc4`  
`https://portal.nccs.nasa.gov/datashare/merra2_gmi/Y2019/M10/MERRA2_GMI.inst0_3d_ovp_Nv.20191015_1200z.nc4`  
`https://portal.nccs.nasa.gov/datashare/merra2_gmi/Y2019/M10/MERRA2_GMI.inst0_3d_ovp_Nv.20191016_1200z.nc4`  
`https://portal.nccs.nasa.gov/datashare/merra2_gmi/Y2019/M10/MERRA2_GMI.inst0_3d_ovp_Nv.20191017_1200z.nc4`  
`https://portal.nccs.nasa.gov/datashare/merra2_gmi/Y2019/M10/MERRA2_GMI.inst0_3d_ovp_Nv.20191018_1200z.nc4`  
`https://portal.nccs.nasa.gov/datashare/merra2_gmi/Y2019/M10/MERRA2_GMI.inst0_3d_ovp_Nv.20191019_1200z.nc4`  
`EDSCEOF`

While you can manually update the dates, if you are a more experienced user of the NASA DAACs you can also use one of the subsetting tools to generate the download script or list of URLs to paste in here too. You will now run each script to download the files by running the script using: 

`./download_merra.sh`

All of the fields needed for MPAS-GOCART2G are listed in the MERRA\_IC config.yaml file in the ‘target’ fields and listed below:

`species_map:`  
  `- {source: "BCPHILIC", file: "prefix_in_1", target: "BCPHILIC", desc: "Hydrophilic Black Carbon Mixing Ratio", units: "kg kg^-1"}`  
  `- {source: "BCPHOBIC", file: "prefix_in_1", target: "BCPHOBIC", desc: "Hydrophobic Black Carbon Mixing Ratio", units: "kg kg^-1"}`  
  `- {source: "OCPHILIC", file: "prefix_in_1", target: "OCPHILIC", desc: "Hydrophilic Organic Carbon Mixing Ratio", units: "kg kg^-1"}`  
  `- {source: "OCPHOBIC", file: "prefix_in_1", target: "OCPHOBIC", desc: "Hydrophobic Organic Carbon Mixing Ratio", units: "kg kg^-1"}`  
  `- {source: "DU001",    file: "prefix_in_1", target: "DU001",    desc: "Dust Mixing Ratio in Bin 001", units: "kg kg^-1"}`  
  `- {source: "DU002",    file: "prefix_in_1", target: "DU002",    desc: "Dust Mixing Ratio in Bin 002", units: "kg kg^-1"}`  
  `- {source: "DU003",    file: "prefix_in_1", target: "DU003",    desc: "Dust Mixing Ratio in Bin 003", units: "kg kg^-1"}`  
  `- {source: "DU004",    file: "prefix_in_1", target: "DU004",    desc: "Dust Mixing Ratio in Bin 004", units: "kg kg^-1"}`  
  `- {source: "DU005",    file: "prefix_in_1", target: "DU005",    desc: "Dust Mixing Ratio in Bin 005", units: "kg kg^-1"}`  
  `- {source: "NI001",    file: "prefix_in_1", target: "NI001",    desc: "Nitrate Mixing Ratio in Bin 001", units: "kg kg^-1"}`  
  `- {source: "NI002",    file: "prefix_in_1", target: "NI002",    desc: "Nitrate Mixing Ratio in Bin 002", units: "kg kg^-1"}`  
  `- {source: "NI003",    file: "prefix_in_1", target: "NI003",    desc: "Nitrate Mixing Ratio in Bin 003", units: "kg kg^-1"}`  
  `- {source: "SO2",      file: "prefix_in_1", target: "SO2",      desc: "Sulphur Dioxide Mixing Ratio", units: "kg kg^-1"}`  
  `- {source: "SO2v",     file: "prefix_in_1", target: "SO2V",     desc: "Sulphur Dioxide Mixing Ratio (volcanic)", units: "kg kg^-1"}`  
  `- {source: "SO4",      file: "prefix_in_1", target: "SO4",      desc: "Sulfate Mixing Ratio", units: "kg kg^-1"}`  
  `- {source: "SO4v",     file: "prefix_in_1", target: "SO4V",     desc: "Sulfate Mixing Ratio (volcanic)", units: "kg kg^-1"}`  
  `- {source: "SS001",    file: "prefix_in_1", target: "SS001",    desc: "Seasalt Mixing Ratio in Bin 001", units: "kg kg^-1"}`  
  `- {source: "SS002",    file: "prefix_in_1", target: "SS002",    desc: "Seasalt Mixing Ratio in Bin 002", units: "kg kg^-1"}`  
  `- {source: "SS003",    file: "prefix_in_1", target: "SS003",    desc: "Seasalt Mixing Ratio in Bin 003", units: "kg kg^-1"}`  
  `- {source: "SS004",    file: "prefix_in_1", target: "SS004",    desc: "Seasalt Mixing Ratio in Bin 004", units: "kg kg^-1"}`  
  `- {source: "SS005",    file: "prefix_in_1", target: "SS005",    desc: "Seasalt Mixing Ratio in Bin 005", units: "kg kg^-1"}`  
  `- {source: "DMS",      file: "prefix_in_1", target: "DMS",      desc: "Dimethylsulphide Mixing Ratio", units: "kg kg^-1"}`  
  `- {source: "MSA",      file: "prefix_in_1", target: "MSA",      desc: "Methanesulphonic Acid Mixing Ratio", units: "kg kg^-1"}`  
  `- {source: "AIRDENS",  file: "prefix_in_1", target: "AIRDENS",  desc: "Moist_Air_Density", units: "kg m^-3"}`  
  `- {source: "RH",       file: "prefix_in_1", target: "RH",       desc: "Relative Humidity", units: "-"}`  
  `- {source: "DELP",     file: "prefix_in_1", target: "DPRES",    desc: "Pressure Thickness", units: "Pa"}`  
  `- {source: "PS",       file: "prefix_in_1", target: "PS",       desc: "Surface Pressure", units: "Pa"}`  
  `- {source: "LWI",      file: "prefix_in_1", target: "LWI",      desc: "Land(1)_Water(0)_Ice(2)_Flag", units: "-"}`  
  `- {source: "OVP14_HNO3",            file: "prefix_in_2", target: "HNO3",          desc: "Nitric Acid", units: "mole mole-1"}`  
  `- {source: "OVP14_HNO3COND",        file: "prefix_in_2", target: "HNO3COND",      desc: "Condensed Nitric Acid", units: "mole mole-1"}`  
  `- {source: "OVP14_GOCART_NH3_VAR",  file: "prefix_in_2", target: "NH3",           desc: "Ammonia", units: "mole mole-1"}`  
  `- {source: "OVP14_CO",              file: "prefix_in_2", target: "CO",            desc: "Carboin Monoxide", units: "mole mole-1"}`  
  `- {source: "OVP14_ISOP",            file: "prefix_in_2", target: "ISOPRENE",      desc: "Isoprene", units: "mole mole-1"}`  
`You can confirm the species mapping between the files using ncdump. Any missing species will be filled in with zeros in the MERRA_IC code, but it is better to fill the data with an available year (2019 has all species available).` 

## **Appendix B: Visualization of MPAS output**

MPAS-GOCART2G uses a variable-resolution, unstructured spherical centroidal Voronoi mesh for simulation and therefore traditional lat/lon visualization methods (i.e. NCVIEW) do not work with input and output files. Therefore simplified tools have been developed for quick visualization of MPAS files. 

### **MPAS-A tutorial python script**

**The first method** is explained in detail in Section 6.5 of the <a href="https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/" target="_blank" rel="noopener noreferrer">MPAS Tutorial - Practice Guide</a> and uses a python script within the terminal to create images that visualize the native MPAS files. 

To use this method for a file in your run directory first run: 

**cp /glade/campaign/mmm/wmr/mpas\_tutorial/python\_scripts/latlon\_cells.py .**

to copy the python script to your run directory. This script takes an MPAS file with appropriate grid information (usually the init\_chems) and uses that to plot an output netcdf file into a PNG file. To run this you need to input both the grid file and the desired output file, for which this example will be the output init\_chems\_emissions.nc file. 

**ln \-s /glade/campaign/acom/MUSICA/MPAS/input/[x1.163842.grid.nc](http://x1.163842.grid.nc) .**

To plot specific outputs you will also need to change the latlon\_cells.py file to look at the correct variable. So modify the following line 4 from:

**field \= 'wind\_speed\_level1\_max'**

to:

**field \= 'bc\_anth\_less100m'**

You can then run the python script using:

**./latlon\_cells.py [x1.163842.grid.nc](http://x1.163842.grid.nc) init\_chems\_emissions.nc**  
**display cell\_plot.png**

To output and display the following graphic. 

```{figure} static/MPAS_GOCART2G_Inst_F3.png
:alt: Sample Global Emissions Plot
:align: center
:width: 100%

**Figure 3.** Global 60km Resolution Surface BC Emissions Example Plot.
```

The default version of the tool works directly with 2D fields, but if you would like to plot 3D variables you will also need to change line 50 from: 

**fld \= uxds\_mpas\[field\].isel(Time=0)**

to: 

**fld \= uxds\_mpas\[field\].isel(Time=0, nVertLevels=0)**

with other options such as zooming in on particular regions discussed in section 6.5 of the <a href="https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/" target="_blank" rel="noopener noreferrer">MPAS Tutorial - Practice Guide</a>**.** 

### **Regrid output to a lat-lon file and then view**

**The second method** works well for quick visualization and those that are most familiar with using ncview and other fixed-grid processes for data analysis. This method is discussed in detail in Section 3.4 and 4.3 of the MPAS-A Tutorial and uses fortran processing (convert\_mpas) to convert MPAS-grid files to a fixed latitude and longitude file. 

The acquisition and compiling of this tool is described in detail in the tutorial, but the simplified steps are shown here as well for a new installation and use if following the instructions here: 

**mkdir /glade/work/$USER/gocartMPAS/mpas\_tools**  
**cd  /glade/work/$USER/gocartMPAS/mpas\_tools**  
**git clone https://github.com/mgduda/convert\_mpas.git**  
**cd convert\_mpas**  
**make**  
**export PATH=/glade/work/$USER/gocartMPAS/mpas\_tools/convert\_mpas:${PATH}**

These steps will give you a compiled version of the convert\_mpas tool that you can access and run. Once compiled, you can directly add the last line to your .bashrc file and it will be available automatically each time you log on to Derecho. 

The base version of this tool takes an MPAS-gridded file and converts it to a global 0.5 by 0.5 degree netcdf named latlon.nc. If the steps above have been followed, you can simply run the tool targeting the same file above using: 

**convert\_mpas init\_chems\_emissions.nc**  
Which will give you an output file of latlon.nc which has all of the tracers stored in the parent file, just now in the 0.5 by 0.5 degree fixed grid format. This file can now be viewed and plotted using traditional methods using Python or ncview. This tool does not do mass-conservative regridding, so should only be used for reference and data visualization, more complex methods should be used for analysis and generation of publication-ready figures. 

### **JupyterLab notebook Python script**

**The final method** is using JupyterLab notebooks and provides the most interactive plotting method. To use this method, users should be comfortable running JupyterHub or JupyterLab on the Derecho or home environments, and more detail can be found here for the NCAR Derecho environment through OnDemand: 

<a href="https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/ood/" target="_blank" rel="noopener noreferrer">NCAR CISL OnDemand</a>) 

Within a new job started in JupyterHub you should create a new workbook using the NPL-2025b environment and paste the following code into the first block:

import netCDF4 as nc  
import numpy as np  
import matplotlib.pyplot as plt  
import uxarray as ux  
import geoviews.feature as gf  
import holoviews as hv  
import cartopy.crs as ccrs  
import cartopy.feature as cfeature

grid\_path \= '/glade/campaign/acom/MUSICA/MPAS/input/x1.163842.grid.nc'  
stat\_path \= '/glade/campaign/acom/MUSICA/MPAS/input/Example-1/EMIS/x1.163842-2024-anth\_black-carbon.MPAS.nc'

uxds \= ux.open\_dataset(grid\_path, stat\_path, decode\_times=False)

uxds\["bc\_anth\_sum"\].isel(Time=0).plot(  
                height=800,  
                width=1500,  
                clim=(0, 1e-11),  
                clabel="kg m$^{-2}$ sec$^{-1}$",  
                backend="matplotlib",  
                cmap="gist\_heat\_r",  
                projection=ccrs.PlateCarree(),  
                features=\["borders", "coastline"\],  
                title=f"CAMS ANTH EMS: BC",  
            )

This code will ensure the appropriate packages are available and plot one of the MPAS-GOCART2G input emission files, resulting in the following figure in a Holoview frame: 

```{figure} static/MPAS_GOCART2G_Inst_F4.png
:alt: Global CAMS BC Emissions
:align: center
:width: 100%

**Figure 4.** Global 60km CAMS_ANTH_BC Emissions. 
```

Modification of this code follows most standard matplotlib options and you can change plot location, scales, labels and colormaps easily. As one example, here is another block of code that uses the jet colormap and zooms in over India:

uxds\["bc\_anth\_sum"\].isel(Time=0).plot(  
    height=800,  
    width=1500,  
    clim=(0, 5e-11),  
    clabel="kg m$^{-2}$ sec$^{-1}$",  
    backend="matplotlib",  
    cmap="jet",  
    projection=ccrs.PlateCarree(),  
    features=\["borders", "coastline"\],  
    title=f"CAMS ANTH EMS: BC \- India Zoom",  
    \# Add these two lines to set the spatial window:  
    xlim=(68, 98),  \# Longitude bounds  
    ylim=(6, 36),   \# Latitude bounds  
)

Resulting in the following plot:   
```{figure} static/MPAS_GOCART2G_Inst_F5.png
:alt: CAMS BC Emissions over India
:align: center
:width: 100%

**Figure 5.** Global 60km CAMS_ANTH_BC Emissions Zoomed in over India.
```

Three dimensional fields can be plotted as well. Changing to the output file of a simulation, hydrophobic black carbon in the lowest model level is plotted below. 

stat\_path \= '/glade/derecho/scratch/barthm/gocartMPAS/DC3simulations/20120501/163842.output.2012-05-01\_03.00.00.nc'

uxds \= ux.open\_dataset(grid\_path, stat\_path, decode\_times=False)

uxds\["qbcphobic"\].isel(Time=0,nVertLevels=0).plot(  
    height=800,  
    width=1500,  
    clim=(0, 1e-9),  
    clabel="kg kg$^{-1}$",  
    backend="matplotlib",  
    cmap="jet",  
    projection=ccrs.PlateCarree(),  
    features=\["borders", "coastline"\],  
    title=f"Hydrophobic BC \- India Zoom",  
    xlim=(68, 98),  \# Longitude bounds  
    ylim=(6, 36),   \# Latitude bounds  
)

Resulting in the following plot:  
