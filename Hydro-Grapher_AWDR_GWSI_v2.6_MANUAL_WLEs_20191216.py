"""     Python Manual GWSI Water Levels Grapher  -  VERSION 2.6
             Started on 6/04/2019
             Last Updated 12/16/2019 (Dec. 16 2019, I am American)

@author: Justin A. Clark
@contibutor(s): Michael T. Giansiracusa

This program takes data from two excel files and creates graphs that stand alone as PNG files.
   The first excel file contain depth to water data collected from manually sampled wells in ADWR's GWSI database.
   The second excel file has well construction data from wells in ADWRs GWSI database.
   The PNG files generated are saved to same "Path" folder as the program is run.
   This program includes a for loop to generate the PNG files.
   This version (version 2.6) is a clean version that just makes PNG files with matplotlib, does not use Seaborn or fancy graphics.
   Pandas and matplotlib are the primary libraries used.
   ~70 Lines of active code are used (the rest is just comments and blank lines.

All data referenced can be downloaded here:
https://new.azwater.gov/sites/default/files/GWSI_ZIP_10182019.zip

This tool was designed for use by Arizona Department of Water Resources (ADWR) Groundwater Flow 
and Transport Modelers to Process the input data for MODFLOW Models and PEST Calibration Runs.

Approximate Run Time = X minutes XX.X sec      (HP Z240 Tower Workstation
                                               Intel I7-7700, 16 GB Ram
                                               Windows 10 Enterprise)
"""
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from matplotlib import dates

##MAKE VARIABLES FOR THE FILENAMES
filename1 = "GWSI_WW_LEVELS.xlsx"
filename2 = "GWSI_SITES.xlsx"

##DEFINE A LIST OF COLUMN NAMES based on GWSI Protocol, to be used reading first xlsx file
ColNames = ["WELL_SITE_ID","ID","Date","DEPTH_TO_WATER","WATER_LEVEL_ELEVATION","SOURCE_CODE","METHOD_CODE","REMARK_CODE"]

## CREATE A PANDAS DataFrame with Observations from Manually Collected Depth to Water Measurements from GWSI Wells in Arizona
df = pd.read_excel(filename1, names = ColNames, index_col = None)

## CREATE DataFrame WITH WELL CONSTRUCTION DATA
df2 = pd.read_excel(filename2, index_col = None)

##CHANGE THE NAME OF THE Well Idenitification column in df2 to match df
col_start = "SITE_WELL_SITE_ID"
col = "WELL_SITE_ID"
df2 = df2.rename(columns={col_start:col})

## Set Bottom Elevation
df2['Well_Bot_Elev'] = df2['SITE_WELL_ALTITUDE'] - df2['SITE_WELL_DEPTH']

##GET A LIST OF UNIQUE WELLS
wells = list(set(df[col]))
wells = set(df[col])        ##Mike G said to use this one, sets are better to pass through a for loop
        ##SKIP BELOW TO REMOVE ERRONEOUS LOCATIONS

for location in wells:
    ##Use Merge to make a DataFrame with all data. Mike G Showed Me this one.
    ##Really fast, data does not get analyzed till later
    df3 = pd.merge(df,df2, on="WELL_SITE_ID")

    ##APPLY THE MERGE HERE, MAKE A NEW DataFrame, SORTED BY DATE. 56 COLUMNS
    df4 = df3.loc[df3[col]==location].sort_values('Date')

    ##CALCULATE THE ELEVATION of the Obsersed Water Level using the 'SITE_WELL_ALTITUDE'. 57 COLUMNS.
    df4['WLE_Calc'] = df4['SITE_WELL_ALTITUDE'] - df4['DEPTH_TO_WATER']

    ##CALCULATE RISE OF EACH OBSERVATION, BASED ON MININIMUM VALUE OBSERVED. 58 COLUMNS.
    min_hd_float = df4['WATER_LEVEL_ELEVATION'].min()
    df4['Rise'] = df4['WATER_LEVEL_ELEVATION'] - min_hd_float

    ## DROP NA VALUES. A SLOPPY ERROR REMOVAL STEP, SHOULD BE ABLE TO USE A LIST OF ERROR TO FIX DATA
    df4.fillna(value = 0, inplace = True)

    ##THIS SECTION DELETES ROWS WITH "ZERO ERRORS"
    df4.drop( df4[ df4['DEPTH_TO_WATER'] == 0 ].index , inplace=True)

    dimensions = df4.shape
    row_count = dimensions[0]
    if row_count == 0:
        bad_wells.append(location)

    else:
        ## THIS SECTION DEFINES AXES MIN/MAX
        min_date_datetime = df4['Date'].iloc[0]
        max_date_datetime = df4['Date'].iloc[len(df4['Date'])-1]

        max_date_4fig = max_date_datetime + pd.offsets.DateOffset(years=1)
        max_date_4fig = max_date_4fig.replace(month = 1)
        max_date_4fig = max_date_4fig.replace(day = 1)
        max_date_4fig = pd.to_datetime(max_date_4fig)

        min_date_4fig = min_date_datetime.replace(month = 1)
        min_date_4fig = min_date_4fig.replace(day = 1)
        min_date_4fig = pd.to_datetime(min_date_4fig)

        total_years_float = (max_date_datetime - min_date_datetime).days/365.25

        x = df4['Date']
        y1 = df4['DEPTH_TO_WATER']
        y2 = df4['WLE_Calc']

        plt.xlabel("Date")
        plt.rcParams['xtick.labelsize']=8

        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        ax1.plot(x, y1)
        ax1.set_ylabel("Depth to Water [ft bgs]")
        plt.gca().invert_yaxis()

        ax2 = ax1.twinx()

        ax2.plot(x, y2, 'b-')
        ax2.plot(x, y2, 'bP')

        ax2.set_ylabel("Water Level Elevation [ft amsl]", color='g')

        fig.suptitle('GWSI Site: ' + str(location) + ', RegID: 55-' + str(int(df4["SITE_WELL_REG_ID"].iloc[0])) + ', Depth: ' + str(int(df3["SITE_WELL_DEPTH"].iloc[0]))+ ' ft', fontsize=12)
        ax1.grid(b=True, which='major', color='#666666', linestyle='-')

        for tl in ax2.get_yticklabels():
            tl.set_color('g')

        myFmt = dates.DateFormatter("%Y")
        ax1.xaxis.set_major_formatter(myFmt)

        #SET X-AXIS LIMITS (xlim)
        ax1.set_xlim([min_date_4fig,max_date_4fig])

        x_ticks = 1 #ANNUAL X-TICKS
        if total_years_float > 40:
            x_ticks = 2

        ax1.xaxis.set_major_locator(dates.YearLocator(x_ticks))#THIS WORKS

        for tick in ax1.get_xticklabels():
            tick.set_rotation(90)

        plt.rcParams.update({'font.size': 12})

        plt.show()

        outname = str('Hydrographs_GWSI_Manual__') + str(location) + str('.png')
        fig.savefig(outname, dpi = 400, bbox_inches='tight', pad_inches=.1)

##############################################################################
##############################################################################
##############################################################################
#  ### ### ### ### ### #### ### ### ### ### ### #### ### ### ### ### ### ###  #
##   Example and Test Code Used for This Program   ##
"""
##
### Attempt to automate the website extraction (directly from .zip file at ADWR)
#import zipfile
## Direct read failed:
##zf = zipfile.ZipFile('https://new.azwater.gov/sites/default/files/GWSI_ZIP_10182019_0.zip') # having First.csv zipped file.
##df5 = pd.read_csv(zf.open('GWSI_ZIP_10182019/Data_Tables/GWSI_TRANSDUCER_LEVELS.txt'))
## Reading data extracted locally from a zip file works:
#zf = zipfile.ZipFile('C:\GIS\ADWR\GWSI_ZIP_10182019_0.zip') # having First.csv zipped file.
#df5 = pd.read_csv(zf.open('GWSI_ZIP_10182019/Data_Tables/GWSI_TRANSDUCER_LEVELS.txt'))

###SET GRAPH STYLE, FORMATTING
#import seaborn as sns
#sns.set_style("darkgrid")
"""
###############################################################################
#  ### ### ### ### ### #### ### ### ### ### ### #### ### ### ### ### ### ###  #
##   Websites Visited   ##
"""

bad_wells = [
322148111171701,321632110543201,321518110442101,322228110590601,324923111260901,315451110573001,320522110534701,320802110555201,320522110534701,321553110533201,323144110523501,
315814111053101,323155111150901,315952111011201,324104111032001,324619110090601,320707111143401,315304110573701,321546110535901,324623111113001,320152111040901,323604111280701,
320145110371001,322410111323501,315707110543301,320247111045201,322108111065301,313607111021101,321618110534401,322016111043001,322738111160801,323413111235101,313256111170101,
313256111170101,321546110523101,321512110593701,314629110503101,320854110443201,320346110433301,322517111085201,321636110555301,322543111133401,320943111133702,321535110535801,
322041110584001,321735111023501,320552110513101,312527111003201,321453111123201,321555110534401,321523110485301,321547110505801,323245111254401,323704111292001,313551110545001,
312115110551301,312359110532901,315848110580301,322730111181401,315346111095401,321344110535701,323035111105601,320338110572101,322622110525001,323431111304901,330457110423201,
321900111014001,321208110491801,312360110533001,314447111023001,320739110562301,322506110560801,315920110414501,321629110545101,321619110570701,315540110404701,315920110415201,
323552111275401,321202110541201,321118110592801,314749111283501,315400110583801,320523110543401,321954111041701,321436110565601,312623110500601,321912110575901,321237110534601,
321521110512201,321236110521201,323041110520701,321028111070101,313551111140401,322044111041901,313851110012301,313851110012302,312241110513301,323302111180501,320404110571301,
315557111314301,320525111113601,315137110571201,321539110533401,321633110555101,324643111254501,321055110593001,323616111295201,321622110550801,322555111095102,322909111073602,
321119110593601,315304110570701,323213110590701,322125111180601,321235110510001,313002110483901,321639111015901,320053111045601,321816111005401,321552110534401,315811111042901,
315811111042901,321021111140301,323332111143701,312445110571901]

outname = str('TestOut_DataFrame_20191216.csv')
df4.to_csv(outname, index=False)
"""
