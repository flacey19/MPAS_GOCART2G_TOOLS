# MPAS-GOCART2G Instructions

The instructions are tailored for running MPAS-GOCART2G on the NSF NCAR HPC system called Derecho.

These instructions combine information from both the [MPAS Tutorial \- Practice Guide](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/) and the specific instructions for running with GOCART-2G aerosols. Be sure to go to the [MPAS Home page](https://mpas-dev.github.io/) and [MPAS-Atmosphere webpage](https://www2.mmm.ucar.edu/projects/mpas/site/index.html) where there is a lot more information and documentation.

## **Table of Contents**

[**Background chapter**](#bookmark=kix.sicppxv9hx6) provides a brief description of the MPAS-GOCART-2G model. 

[**Chapter 1**](#bookmark=kix.rxyhj8v1l1ab) gives instructions on running a case where all the input files are provided. It allows the new user to become familiar with the workflow in preparing a MPAS-GOCART2G simulation and is great for ensuring that the user has configured their system properly. 

[**Chapter 2**](#chapter-2-setting-up-a-different-case) provides information on setting up your own case using the same grid mesh as in chapter 1 but running a different time period, including where to obtain input files and running the program *init\_atmosphere* which sets up the MPAS-GOCART2G simulation. 

**Chapter 3** provides information on running with a variable resolution grid mesh and setting up different variable resolution grids. 

**Chapter 4** provides instructions for viewing MPAS-GOCART2G output using uxarray in Python scripts. 

**Appendix A** explains how to download MERRA2 files.

**Appendix B** describes ways to visualize MPAS-GOCART2G output.

## **Background chapter Familiarizing yourself with the physics suite to run a MPAS-GOCART2G simulation**

The MPAS-GOCART2G model has been developed as part of the NSF NCAR’s vision to move towards a unified modeling framework and links the MPAS-A dynamical core (Skamarock et al., 2012) to the GOCART2G chemical mechanism (Collow et al., 2024). The GOCART2G module adds 30 new scalars to represent seven tropospheric aerosol species and their precursors. Major aerosol species represented by GOCART2G include black carbon (BC), brown carbon (BrC), organic carbon (OC), sulfate, nitrate, dust, and sea-salt. BC, BrC, and OC are assumed to be present in hydrophobic and hydrophilic modes with an e-folding lifetime of 2.5 days for conversion of hydrophobic mode to hydrophilic mode. All the aerosol species are subjected to gravitational settling, dry and wet deposition processes except that in-cloud wet deposition processes do not affect hydrophobic mode mass mixing ratios. Dry deposition velocity of aerosol and precursor species is estimated using the Wesely (1989) scheme. Resolved scale wet deposition of aerosols is calculated using aerosol-aware Thompson-Edihammer scheme. Convective transport of all chemical constituents is simulated using nTiedtke scheme.  

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

Dust aerosols are represented using five size bins (radii of 0.73, 1.4, 2.4, 4.5, and 8.0 µm) and their emissions are calculated online within the model utilizing the Ginoux et al. (2001) parameterization. Static geographical fields such as “erod” (erodibility representing the areas from where dust aerosols can be emitted), clayfrac and sandfrac required for dust emissions are mapped to the MPAS-GOCART domain along with the processing of other static geographical fields (see Section 1.3 of [MPAS tutorial guide](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Howard2024/index.html) for processing these fields). Sea-salt aerosols also use five size bins, specifically with radii of 0.079, 0.316, 1.119, 2.818, and 7.772 µm. Emissions for sea-salt are calculated using the Gong (2003) wind-driven parameterization, but this includes two key modifications: first, friction velocity has replaced the 10m wind speed, which is required for tuning the parameterization's constants; and second, a correction term dependent on sea surface temperature was added. This temperature-dependent modification is similar to the approach by Jaegle et al. (2011) but was specifically tuned to improve agreement between the simulated sea-salt AOD and MODIS-retrieved AOD.

### **References**

- Collow, A. B., Colarco, P. R., da Silva, A. M., Buchard, V., Bian, H., Chin, M., Das, S., Govindaraju, R., Kim, D., and Aquila, V.: Benchmarking GOCART-2G in the Goddard Earth Observing System (GEOS), Geosci. Model Dev., 17, 1443–1468, https://doi.org/10.5194/gmd-17-1443-2024, 2024. 
- Gong, S. L.: A parameterization of sea-salt aerosol source function for sub- and super-micron particles, Glob. Biogeochem. Cycles, 17, https://doi.org/10.1029/2003GB002079, 2003.
- Ginoux, P., Chin, M., Tegen, I., Prospero, J. M., Holben, B., Dubovik, O., and Lin, S.-J.: Sources and distributions of dust aerosols simulated with the GOCART model, J. Geophys. Res. Atmos., 106, 20255–20273, https://doi.org/10.1029/2000JD000053, 2001.
- Jaeglé, L., Quinn, P. K., Bates, T. S., Alexander, B., and Lin, J.-T.: Global distribution of sea salt aerosols: new constraints from in situ and remote sensing observations, Atmos. Chem. Phys., 11, 3137–3157, https://doi.org/10.5194/acp-11-3137-2011, 2011.
- Skamarock, W. C., Klemp, J. B., Duda, M. G., Fowler, L. D., Park, S.-H., and Ringler, T. D.: A Multiscale Nonhydrostatic Atmospheric Model Using Centroidal Voronoi Tesselations and C-Grid Staggering, https://doi.org/10.1175/MWR-D-11-00215.1, 2012.
- Soulie, A.; Granier, C.; Darras, S.; Zilbermann, N.; Doumbia, T.; Guevara, M.; Jalkanen, J.-P.; Keita, S.; Liousse, C.; Crippa, M.; Guizzardi, D.; Hoesly, R.; Smith, S. Global Anthropogenic Emissions (CAMS-GLOB-ANT) for the Copernicus Atmosphere Monitoring Service Simulations of Air Quality Forecasts and Reanalyses. Earth System Science Data Discussions 2023, 1–45. https://doi.org/10.5194/essd-2023-306.
- Wesely, M. L.: Parameterization of surface resistances to gaseous dry deposition in regional-scale numerical models, Atmos. Environ. 1967, 23, 1293–1304, https://doi.org/10.1016/0004-6981(89)90153-4, 1989.
- Wiedinmyer, C.; Kimura, Y.; McDonald-Buller, E. C.; Emmons, L. K.; Buchholz, R. R.; Tang, W.; Seto, K.; Joseph, M. B.; Barsanti, K. C.; Carlton, A. G.; Yokelson, R. The Fire Inventory from NCAR Version 2.5: An Updated Global Fire Emissions Model for Climate and Chemistry Applications. Geoscientific Model Development 2023, 16 (13), 3873–3891. https://doi.org/10.5194/gmd-16-3873-2023.


### **Physics Configuration with MPAS-GOCART2G**

MPAS-GOCART2G has been tested with the “convection\_permitting” MPAS-A physics suite. Please see the physics component of the namelist.atmosphere below. The PBL mixing of chemical constituents is calculated inside the MYNN PBL scheme. Note that deposition velocity of chemical constituents is still calculated by GOCART-2G and is passed to MYNN for deposition along with the turbulent mixing. Convective transport of tracers is performed using the nTiedtke scheme. In addition to setting these options in the physics part of the namelist, additional variables need to be set in the “chemistry” part of the namelist (see in bold font below under “chemistry” components). GOCART-2G aerosols also interact with the Thompson cloud microphysics and RRTMG radiation schemes.  

\&physics  
    config\_sst\_update \= false  
    config\_sstdiurn\_update \= false  
    config\_deepsoiltemp\_update \= false  
    config\_radtlw\_interval \= '00:30:00'  
    config\_radtsw\_interval \= '00:30:00'  
    config\_bucket\_update \= 'none'  
    config\_physics\_suite \= 'convection\_permitting'  
    config\_microp\_scheme \= 'mp\_thompson\_gocart2G'  
    config\_pbl\_scheme \= 'bl\_mynn'        
    config\_mynn\_mixchems \= true  
    config\_convection\_scheme \= 'cu\_ntiedtke'Detail  
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

MPAS-A requires that your Derecho environment is set up with available capabilities, such as MPI-2, NetCDF-4, PnetCDF, and PIO libraries. To learn how to set up your environment, please see the instructions in Chapter 0 of the [MPAS-A Tutorial Practice Guide](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/). 

Note: If you are using tcsh instead of bash, the PATH can be set as:  
setenv PATH /glade/campaign/mmm/wmr/mpas\_tutorial/metis/bin:${PATH}

### Download MPAS-GOCART2G from Github:

First, go to a directory where you would like to store the MPAS-GOCART2G source code, such as the /glade/work/$USER directory where $USER is your login name on Derecho.  
cd  /glade/work/$USER

Depending on the version and host repository of the model, especially for development branches, you may need to set up an SSH key for the Derecho environment. Instructions for this can be found on this page [Populating GitHub SSH Keys and Agents](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).

Next, clone the code from Github or copy a version from campaign storage.   
git clone [https://github.com/TBD\_Name](https://github.com/TBD_Name) gocartMPAS 

Or copy the code from the ACOM campaign storage location:

cp \-rp /glade/campaign/acom/MUSICA/MPAS/gocartMPAS .  
   
   
The *gocartMPAS* directory should be created with the MPAS-GOCART2G source code. The directory should include the following:  
ls \-l gocartMPAS/  
total 74  
drwxrwxr-x+  4 USER acom-weather 16384 Sep 15 11:33 cmake/  
\-rwxrwxr-x+  1 USER acom-weather  8128 Sep 15 11:33 CMakeLists.txt\*  
drwxrwxr-x+  3 USER acom-weather 16384 Sep 15 11:33 docs/  
\-rwxrwxr-x+  1 USER acom-weather  3131 Sep 15 11:33 INSTALL\*  
\-rwxrwxr-x+  1 USER acom-weather  2311 Sep 15 11:33 LICENSE\*  
\-rwxrwxr-x+  1 USER acom-weather 55424 Sep 15 11:33 Makefile\*  
\-rwxrwxr-x+  1 USER acom-weather  2811 Sep 15 11:33 README.md\*  
drwxrwxr-x+ 14 USER acom-weather 16384 Sep 15 11:33 src/  
drwxrwxr-x+  5 USER acom-weather 16384 Sep 15 11:33 testing\_and\_setup/

### Compile MPAS-GOCART2G:

Compiling MPAS-GOCART2G follows the same steps as that for MPAS-A compilation. Please follow the steps outlined in chapter 1.2 of the [MPAS-A Tutorial Practice Guide](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/). For those who are familiar with compiling MPAS-A, the commands are the following:

cd gocartMPAS  
qcmd \-A $PROJ \-- make gnu CORE=init\_atmosphere GOCART2G=true AUTOCLEAN=true  
qcmd \-A $PROJ \-- make gnu CORE=atmosphere GOCART2G=true AUTOCLEAN=true

where $PROJ is the NCAR HPC Derecho project account key that your work is charged to. If you don’t have access to Derecho, please refer to job submission guidelines for your local HPC. If you want to debug your simulation because of an error, you can compile the code with the DEBUG option turned on:

qcmd \-A $PROJ \-- make gnu CORE=init\_atmosphere GOCART2G=true AUTOCLEAN=true DEBUG=true  
qcmd \-A $PROJ \-- make gnu CORE=atmosphere GOCART2G=true AUTOCLEAN=true DEBUG=true

When the compilation of both init\_atmosphere and atmosphere are successful, the directory now has several input files needed to run MPAS-A (see the [MPAS-A Tutorial Practice Guide](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/) for more information). There are also now the following executable, namelist, and streams files.

init\_atmosphere\_model\*  
atmosphere\_model\*  
build\_tables\*

namelist.init\_atmosphere  
namelist.atmosphere

stream\_list.atmosphere.diagnostics  
stream\_list.atmosphere.diag\_ugwp  
stream\_list.atmosphere.output  
stream\_list.atmosphere.surface  
streams.atmosphere  
streams.init\_atmosphere

For more information about these files, see the [MPAS-A Tutorial Practice Guide](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/). 

**The next step** is to create the look-up tables used by the Thompson microphysics scheme by issuing the following command. 

./build\_tables

It will take 10-15 minutes to complete this job. Once it is finished, the following files now reside in the directory.  
   MP\_THOMPSON\_QRacrQG\_DATA.DBL  
   MP\_THOMPSON\_QRacrQS\_DATA.DBL  
   MP\_THOMPSON\_freezeH2O\_DATA.DBL  
   MP\_THOMPSON\_QIautQS\_DATA.DBL  
As suggested by the program output, copy these files to the src/core\_atmosphere/physics/physics\_wrf/files/ directory.

### MPAS-GOCART2G I/O: 

Similar to MPAS-A, the reading and writing of model fields MPAS-GOCART2G is handled by user-configurable streams. We refer the users to MPAS-A User’s guide to familiarize themselves with these streams ([https://www2.mmm.ucar.edu/projects/mpas/site/documentation/users\_guide/configuring\_io.html](https://www2.mmm.ucar.edu/projects/mpas/site/documentation/users_guide/configuring_io.html)). In addition to the standard MPAS output, the MPAS-GOCART2G I/O requires input streams for anthropogenic, biomass burning, and biogenic emissions and output streams for three-dimensional output of aerosols and related variables, diagnostic variables (e.g., total PM2.5, total and individual species AOD at 550 nm, Angstrom exponent, etc.). Example stream files are provided with the MPAS-GOCART2G release.    

### Running MPAS-GOCART2G: Example 1

The practice example (Example-1) is a global 60-km uniform grid mesh with a start date of 15 October 2024 at 00:00 UTC. The simulation can be run for 5 days, but for testing whether MPAS-GOCART2G works or not, **this example will perform a 3-hour simulation** which should take about 10 minutes of wallclock time. Note, it is okay to run a 5-day simulation, but be aware of the computational costs. We find that the 5-day simulation takes about 8 hours of wallclock time for the number of CPUs requested in the submission script. 

It is best to run MPAS\_GOCART2G on the Derecho scratch directory. Begin by creating a run directory and moving to that directory.

mkdir \-p /glade/derecho/scratch/$USER/gocartMPAS/Example-1  
cd /glade/derecho/scratch/$USER/gocartMPAS/Example-1

For this example, we have provided a shell script that will set up and build your simulation directory and submit the jobs. You can copy this script into your new directory using the following command.

cp /glade/campaign/acom/MUSICA/MPAS/scripts/submit\_mpas\_gocart.bash .

This will copy a script to aid in job submission.The script is configurable and can be modified for other case studies (e.g., what is presented in Chapter 2). 

In the script, you will need to change line 11 (“proj=P19010000”) to use the Derecho Account Key that you can use to submit your jobs. If you don’t have access to Derecho, please refer to job submission guidelines for your local HPC.

*What does the script do?*  
The script creates a new directory in which the *init\_atmosphere* and *atmosphere* executables are run. The directory’s name is based on the start date of the simulation. In this example, the script creates the directory, 20241015/.

The commands within the script are documented in the file. There are eight sections within the script that are outlined here.

1. Set flags and input arguments (i.e., start date) for the simulation.  
2. Set the path of the run script.  
3. Set paths for the location of the 1\) MPAS-GOCART2G source code, 2\) the directory for the forecast files, including the output, 3\) GFS meteorology input files, 4\) MERRA-2 trace gas and aerosol input files, 5\) emissions input files, and 6\) background concentration files for the GOCART2G prescribed oxidants.  
4. Create the MPAS forecast directory, which is a sub-directory of the path\_fcst directory and defines the location of the default namelists for the init\_atmosphere and atmosphere executables. The namelists are then modified to the start and end dates and times of the simulation.   
5. Link the grid mesh, static, and streams files to the local directory (as described in the MPAS Tutorial Practice Guide), link to the meteorology and GOCART2G initialization and data files, and link to the executables init\_atmosphere and atmosphere.   
6. Build and submit init\_atmosphere\_model.  
7. Build and submit atmosphere\_model. Note that “submit atmosphere\_model” is a dependent job that will only run after the “submit init\_atmosphere\_model” job is successfully completed. 

   
Review the script to ensure the project number, start date, length of simulation, and paths for the source code and output files (path\_fcst) are correct. Then submit the script on Derecho:

./submit\_mpas\_gocart.bash

The init\_atmosphere code creates the init\_chems\_emissions.nc file, which contains initial conditions for meteorology, static geographical fields, and all GOCART2G chemical (both gas and aerosol) species as well as emissions from anthropogenic, biomass burning, and biogenic sources. 

As the atmosphere code integrates through the simulation, the following hourly output files are created:

* 163842.output.2024-10-15\_0\*.00.00.nc — These files contain selected variables (including aerosol concentrations) specified in “stream\_list.output” .   
* 163842.diagnostics.2024-10-15\_0\*.00.00.nc – These files contain the variables listed in the “stream\_list.diagnostics” 

You will not generate the 163842.restart.2024-10\*.nc files with this example run as the defined restart timestep is 12:00 hours, and the simulation run time is only 3 hours. Restart files are checkpoints of the model state and can be used to restart a simulation from the point they are written.  

Chapter 2 (Section 5\) discusses the definition of output in the streams file in more detail allowing for more control and flexibility in MPAS-GOCART2G simulations. 

### Quick Viewing of the Model Results

For viewing model output to confirm that the model is running correctly, we recommend converting the model output to a regular latitude-longitude grid using the *convert\_mpas* tool. The converted output (on a latitude-longitude grid) can then be viewed using the *ncview* command or with plotting scripts. 

Section 3.4 of the [MPAS-A Tutorial Practice Guide](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/) describes how to obtain the *convert\_mpas* tool and compile it. An example command line for running *convert\_mpas* (we recommend adding the full path of convert\_mpas to your $PATH so that you can use it in any directory) is given here.

convert\_mpas x1.163842.static\_chems.nc 163842.output.2024-10-15\_03.00.00.nc

When *convert\_mpas* is run, it creates a file called *latlon.nc*. Note, if you wish to convert other MPAS-GOCART2G files to a latitude-longitude grid, then you must rename or delete the current latlon.nc file.

More information about plotting MPAS-GOCART2G output is given in [Appendix B](#appendix-b:-visualization-of-mpas-output). Specifically, we recommend using the uxarray within python to plot results on the native grid mesh. 

## **Chapter 2 Setting Up a Different Case**  {#chapter-2-setting-up-a-different-case}

### Introduction

This chapter provides information on setting up a different case using the same grid mesh as in chapter 1 but running a different time period. A description is given on where to obtain input files for running the program *init\_atmosphere* which sets up the MPAS-GOCART2G simulation. The chapter is structured by the four types of input files needed to run a new case:

1. Preparation of meteorology fields  
2. Getting MERRA-2 data for the initial concentrations of the species  
3. Preparation of the emissions (anthropogenic, biogenic, biomass burning)  
4. Linking to data for the prescribed oxidant fields 

Two case studies are presented because obtaining the MERRA2 data used for initializing GOCART2G trace gases and aerosols has different procedures for before and after 2020\. 

1. ### Preparation of Meteorology Fields

**For case studies after 2020-01-01:** A 1-month spin-up of the GOCART-2G fields is needed before running the case study. Therefore, *obtain meteorology input data starting 2 weeks before the start of the case study*. The end date should be the same as the end date for the case study. 

When following these instructions for the first time, we recommend using the same 60-km uniform grid mesh as that used in Chapter 1, but for a different time period. Once you are comfortable with the pre-processing steps, then testing other grid meshes is encouraged. The instructions to set up the grid mesh and static fields can be found in chapter 1.3 of the [MPAS-A Tutorial Practice Guide](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/),

The steps to obtain meteorology datasets (either GFS or ERA) and converting them to an intermediate file format that *init\_atmosphere\_model* are presented in the [MPAS-A Tutorial Practice Guide](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/) in Section 2\. After following the instructions in the MPAS-A tutorial, several met\_data files (either “GFS:yyyy-mm-dd-hh” or “ERA5:yyyy-mm-dd-hh”) should be in a newly created met\_data/ directory. 

2. ### Getting MERRA data and convert to MPAS intermediate files

MERRA2 files provide initial concentrations for the predicted fields as well as HNO3, NH3, CO, and isoprene. The HNO3 and NH3 are used for the thermodynamics calculation of the SO4-NH4-NO3 system. Isoprene and CO are used for the simplified SOA production. 

The [appendix below](#appendix-a:-generating-downloading-and-merra2-intermediate-files) provides information on how to download MERRA data from the NASA Earthdata site. You will need to have an NASA Earthdata user name and password to download the data when running the python script. 

Once the MERRA input files are in a local directory, converting the MERRA data to the MPAS-A grid mesh can be done with the python MERRA processing script, *run\_processing.py*. The script and instructions for running the script can be found on the [MERRA IC github page](https://github.com/PACE-DAAQ/MPAS-GOCART2G_MERRA_IC.git).

**Preparation of Chemistry Input Fields for Cases Before 2020**  
All the species are available in the MERRA2 files and one should be able to proceed according to the instructions. 

**Preparation of Chemistry Input Fields for Cases 2020 and Later**  
The MERRA2 files for cases after 2019 do not include initialization of nitrate aerosols or ammonia. Therefore it is best to spin-up their concentrations in the atmosphere by running a spin-up simulation for one month. Be sure to prepare your case study to include the 1-month spin-up time. 

3. ### Preparation of the Emissions via UPTEMPO

The emissions preprocessor, UPTEMPO, is a python script. To get the UPTEMPO scripts, clone the code from Github:  
git clone [https://github.com/PACE-DAAQ/UPTEMPO](https://github.com/PACE-DAAQ/UPTEMPO) UPTEMPO

To run UPTEMPO you can either use your Terminal or submit a job to Derecho’s PBS system. 

Go to the [UPTEMPO github page](https://github.com/PACE-DAAQ/UPTEMPO/tree/main) and follow the instructions in the README files.   
For processing **anthropogenic emissions** from the CAMS inventory: README\_CAMS.md

The *config\_cams\_anth\_regrid.yaml* file lists directories pointing to the CAMS v6.2 emissions for January 2001 to 2024 and the MPAS uniform 60-km grid mesh. In case the directories on Derecho do not have emissions for the year of your study, you can download those from the ECCAD database. Here is the ECCAD user’s guide: [https://eccad.aeris-data.fr/user\_guide/](https://eccad.aeris-data.fr/user_guide/). Make sure you download all the sectors because GOCART-2G requires sectoral information for different species.

For processing **biogenic emissions** from the CAMS inventory: README\_CAMS\_BIOG.md

The pre-processing for biogenic emissions uses a climatological dataset, so it is not necessary to specify the year. In the code that is provided, we use 2019 as a placeholder. Note, that the resulting biogenic emissions are climatology and do not represent a specific year.

For processing **biomass burning emissions** from the FINN2.5 inventory: README\_FINN.md

Getting FINNv2.5 data input files:  
For 2012-2023 the FINNv2.5 data input files are available on the Geoscience Data Exchange (GDEX) website [GDEX Fire Inventory from NCAR database](https://gdex.ucar.edu/datasets/d312009/). After reading the description of the data, click on Data Access. On Derecho, you can make use of the NCAR Data Storage System Holdings. You will want the “eachfire modisviirs: Global daily emissions for each file at 1 km resolution, the base and speciated VOCS based on MODISVIIRS data” (last row of the table) data. For annual text files you will need to use the file\_type: ‘annual’ in the YAML file. 

For 2024-present, you will need to get the daily near real time data files from [https://www.acom.ucar.edu/acresp/MODELING/finn\_emis\_txt/](https://www.acom.ucar.edu/acresp/MODELING/finn_emis_txt/).   
Important: You will need to set the YAML flag to file\_type: ‘daily’ as the configuration. 

Copy the text files downloaded either from GDEX (/gdex/data/d312009/2012\_eachfire\_modisviirs/FINNv2.5\_modvrs\_MOZART\_\*.[txt.gz](http://txt.gz)) or the website to your local directory where you can uncompress the file (using the “gunzip” command on linux). 

4. ### Background Oxidants Data and Aerosol Optical Properties Data

Background oxidant data is currently produced using climatological GMI simulations, similar to WRF-Chem. These background oxidant data files are located in the following directory:

/glade/campaign/acom/MUSICA/MPAS/input/BACKGROUND

The *submit\_mpas\_gocart.bash* script links to this directory, so no changes by the user are needed.

Aerosol optical properties are from Chin et al., 2002\. These data files are located in the following directory:

/glade/campaign/acom/MUSICA/MPAS/input/optics\_files

The submit\_mpas\_gocart.bash script links to this directory, so no changes by the user are needed.

If you would like to use different background or aerosol optical property data files, then simply create those files in the same format as those provided in the directory and modify the *submit\_mpas\_gocart.bash* script to link to the new files.   
*Note:* In the near future obtaining the background oxidants data from WACCM output will become available.  

5. ### Modification of streams.init\_atmosphere and streams.atmosphere

When MPAS-GOCART2G is compiled, two streams files, *streams.init\_atmosphere* and *streams.atmosphere*, are created. More information on what these two files are and what information is contained in them is given in [Chapter 5 of the MPAS User’s Guide](https://www2.mmm.ucar.edu/projects/mpas/site/documentation/users_guide/configuring_io.html). For MPAS-GOCART2G and as noted in [Chapter 1](https://docs.google.com/document/d/122fPMFRE7-R-C53rPbVrAkL_NUjAZc8WCPjhhH0ru4s/edit?tab=t.0#bookmark=id.7pmv7eg2ok80) of these instructions, MPAS-GOCART2G I/O requires input streams for anthropogenic, biomass burning, and biogenic emissions. 

When creating a new case, the file names for the emissions changes from the default streams files that are provided. Therefore, the user needs to review the information in these two files and modify any file names to match what was generated in the emissions pre-processing step above.  

Also ensure that the *submit\_mpas\_gocart.bash* script will link to the streams files correctly.  

For adding in user defined streams, follow the instructions found in Section 6.2 of the [MPAS-A Tutorial Practice Guide](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2025/). In short, output streams can be defined using either variable names or a text file (stream\_list) containing a list of desired output variables. Here is an example of each method: 

Using variable definition add this as a new code block to the stream.atmosphere file: 

**\<stream name="sfc\_winds"**  
        **type="output"**  
        **filename\_template="surface\_winds.$Y-$M-$D\_$h.nc"**  
        **filename\_interval="output\_interval"**  
        **output\_interval="60:00" \>**

        **\<var name="u10"/\>**  
        **\<var name="v10"/\>**  
**\</stream\>**

Or, using a file called “stream\_list.sfc\_winds” that contains the following: 

**u10**  
**v10**

You can add in a new stream (identical to the one above) into streams.atmosphere using the following code block: 

**\<stream name="sfc\_winds"**  
        **type="output"**  
        **io\_type="pnetcdf,cdf5"**  
        **filename\_template="surface\_winds.$Y-$M-$D\_$h.nc"**  
        **output\_interval="00\_01:00:00"\>**  
        **\<file name="stream\_list.sfc\_winds"/\>**  
**\</stream\>**

When MPAS-GOCART2G is compiled, a number of *streams\_list.atmosphere\** files are created. The standard files are:  
stream\_list.atmosphere.diagnostics  
stream\_list.atmosphere.output  
stream\_list.atmosphere.surface  
And contain information about what fields to output during the simulation. 

## **Appendix A:  Generating Downloading and MERRA2 Intermediate Files** {#appendix-a:-generating-downloading-and-merra2-intermediate-files}

This section describes the procedure for (1) downloading, (2) preparing, and (3) generating the MPAS required MERRA2 fields for GOCART simulations using aerosol and nitrate precursor concentrations. 

Note: The MERRA2 reanalysis product contains all fields needed to run through the end of 2019\. For Runs past this point, the files can be used, but a two-week spinup is recommended to correct for use of prior year nitrate concentrations. 

1) Two different sets of MERRA2 files are needed to populate the chemical fields needed for GOCART, this first being for aerosol species “inst3\_3d\_aer\_Nv” and the second being for the gaseous species “inst0\_3d\_ovp\_Nv”. 

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

[Back to MERRA processing instructions](#bookmark=kix.1aikzrhboh1a)

## **Appendix B: Visualization of MPAS output** {#appendix-b:-visualization-of-mpas-output}

MPAS-GOCART2G uses a variable-resolution, unstructured spherical centroidal Voronoi mesh for simulation and therefore traditional lat/lon visualization methods (i.e. NCVIEW) do not work with input and output files. Therefore simplified tools have been developed for quick visualization of MPAS files. 

### **MPAS-A tutorial python script**

**The first method** is explained in detail in Section 6.5 of the [MPAS-A Tutorial](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/) and uses a python script within the terminal to create images that visualize the native MPAS files. 

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

with other options such as zooming in on particular regions discussed in section 6.5 of the [MPAS-A Tutorial](https://www2.mmm.ucar.edu/projects/mpas/tutorial/Virtual2026/)**.** 

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

The base version of this tool takes an MPAS-gridded file and converts it to a global 0.5 by 0.5 degree netcdf named [latlon.nc](http://latlon.nc). If the steps above have been followed, you can simply run the tool targeting the same file above using: 

**convert\_mpas init\_chems\_emissions.nc**  
Which will give you an output file of [latlon.nc](http://latlon.nc) which has all of the tracers stored in the parent file, just now in the 0.5 by 0.5 degree fixed grid format. This file can now be viewed and plotted using traditional methods using Python or ncview. This tool does not do mass-conservative regridding, so should only be used for reference and data visualization, more complex methods should be used for analysis and generation of publication-ready figures. 

### **JupyterLab notebook Python script**

**The final method** discussed here is using JupyterLab notebooks and provides the most interactive plotting method. To use this method, users should be comfortable running JupyterHub or JupyterLab on the Derecho of home environments, and more detail can be found here for the NCAR Derecho environment: 

[https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/jupyterhub/](https://ncar-hpc-docs.readthedocs.io/en/latest/compute-systems/jupyterhub/) 

Within a new job started in [JupyterHub](https://jupyterhub.hpc.ucar.edu/) you should create a new workbook using the NPL-2026a environment and paste the following code into the first block:

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
