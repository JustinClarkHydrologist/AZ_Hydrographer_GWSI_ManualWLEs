"""     Python GWSI Water Levels Grapher  -  VERSION 2.3
             Started on 6/04/2019
             Last Updated 11/23/2019 (November 23 2019, I am American)

@author: Justin A. Clark

This program takes data from two excel files and a text file and creates graphs that stand alone as PNG files.
   The excel files contain water level data and well construction data from wells in ADWRs GWSI database.
   The PNG files generated are saved to the main "Path" Folder.
   This program includes a loop to make all the PNG files.
   This version (version 2.3) is a clean version that just makes PNG files with matplotlib, does not use Seaborn.
   matplotlib and Pandas are the primary libraries.

This tool was designed for use by Arizona Department of Water Resources (ADWR) Groundwater Flow 
and Transport Modelers to Process the input data for MODFLOW Models and PEST Calibration Runs.

Approximate Run Time = X minutes XX.X sec      (HP Z240 Tower Workstation
                                               Intel I7-7700, 16 GB Ram
                                               Windows 10 Enterprise)
"""
import pandas as pd
import matplotlib.pyplot as plt
import os, xlsxwriter
from matplotlib.dates import DateFormatter
from matplotlib.dates import YearLocator

#
## Set variables for the filenames
filename1 = "GWSI_WW_LEVELS.xlsx"
filename2 = "GWSI_SITES.xlsx"

#
## Define a list of column names based on GWSI Protocol, to be used reading first xlsx file
ColNames = ["WELL_SITE_ID","ID","Date","DEPTH_TO_WATER","WATER_LEVEL_ELEVATION","SOURCE_CODE","METHOD_CODE","REMARK_CODE"]

#
## Create a Pandas DataFrame with Data from Manually Collected Depth to Water Measurements from GWSI Wells in Arizona
df = pd.read_excel(filename1, names = ColNames, index_col = None)

#
## Create a Pandas DataFrame with Well Construction Data
df2 = pd.read_excel(filename2, index_col = None)

#
##Change the name of a Well ID column in df2 to match df
col_start = "SITE_WELL_SITE_ID"
col = "WELL_SITE_ID"
df2 = df2.rename(columns={col_start:col})

#
## Set Bottom Elevation
df2['WELL_BOT'] = df2['SITE_WELL_ALTITUDE'] - df2['SITE_WELL_DEPTH']

#
##GET A LIST OF UNIQUE WELLS
wells = list(set(df[col]))
#subset1
wells = ([313845111023101,313851111012201,313920111033301,313958111023301,314015111033401,314148111055101,314150111031701])

for location in wells:
     ##THIS FIRST SECTION MAKES THE WELL SPECIFIC DATAFRAME
     df3 = df.loc[df[col] == location].copy()
###     df3 = df.loc[df[col] == location] ##WARNING POPPED UP
###     df3 = df.loc[df[col] == location, :]
     ###THE NEXT STEP COULD PROBABLY BE DONE BY RE-INDEXING "df3.Date"
     df3['UpDate'] = pd.to_datetime(df3.Date)
     df3 = df3.sort_values('UpDate')
     
     ##EXTRACT THE ELEVATION OF THE GROUND AT THIS WELL FROM df2
     ##THIS METHOD GIVES A WARNING, FIX LATER
     elev = df2[df2[col]==location]['SITE_WELL_ALTITUDE']
     df3['LSE'] = elev.iloc[0]
     
     ##EXTRACT THE BOTTOM ELEVATION OF THE WELL FROM df2
     bottom = df2[df2[col]==location]['WELL_BOT']
     df3['Bottom'] = bottom.iloc[0]
     
     ##EXTRACT THE WELL DEPTH FROM df2
     depth = df2[df2[col]==location]['SITE_WELL_DEPTH']
     df3['Depth'] = depth.iloc[0]
     
     ##EXTRACT THE WELL REGISTRY ID (IF AVAILABLE) df2
     RegNo = df2[df2[col]==location]['SITE_WELL_REG_ID']
     df3['Reg_No'] = RegNo.iloc[0]
     RegNo = df3.Reg_No.iloc[0]

     ##CALCULATE THE MAX RISE OF THE WELL
     min_hd_float = df3['WATER_LEVEL_ELEVATION'].min()
     df3['Rise'] = df3['WATER_LEVEL_ELEVATION'] - min_hd_float

     ## This is a sloppy way to avoid errors, should add individual replacers above
     df3.fillna(value = 0, inplace = True)

     #
     ## THIS SECTION DEFINES AXES MIN/MAX
     min_date_str = df3['UpDate'].min()
     min_date_datetime = min_date_str.date()
     min_date_4fig = df3['UpDate'].min()

     max_date_str = df3['UpDate'].max()
     max_date_datetime = max_date_str.date()
     max_date_4fig = df3['UpDate'].max()

     total_days = max_date_datetime - min_date_datetime
     int_days = total_days.days 

     ##THIS SECTION DELETES "ZERO ERRORS"
     df3.drop( df3[ df3['DEPTH_TO_WATER'] == 0 ].index , inplace=True)

     plt.xlabel("Date")

     #####HELP!####
#     yrs=int_days / 365.25
#     freq = 'A'
#     if yrs >= 30:
#          freq = '5A'
          ##I CANNOT GET THE TICK INTERVAL TO CHANGE. I WANT IT TO BE 5 YEARS IF THE TOTAL YEARS IS 30 OR MORE
#     xrange = pd.date_range(min_date_4fig, end=max_date_4fig, freq='A')
#     xrange = pd.date_range(min_date_4fig, end=max_date_4fig, freq='H')
#     xrange = pd.date_range(min_date_4fig, end=max_date_4fig, freq = 'Q')
     plt.rcParams['xtick.labelsize']=8

     x = df3['UpDate']
     y1 = df3['DEPTH_TO_WATER']
     y2 = df3['WATER_LEVEL_ELEVATION']

     fig = plt.figure()
     ax1 = fig.add_subplot(111)

#     ax1.plot(x, y1, xticks=df2.index)#TEST
     ax1.set_ylabel("Depth to Water [ft bgs]")
     plt.gca().invert_yaxis()

     ax2 = ax1.twinx()
#     ax2.plot(x, y2, scalex = xrange, 'b-')
#     ax2.plot(x, y2, scalex = xrange, 'bP')

     ax2.plot(x, y2, 'b-')
     ax2.plot(x, y2, 'bP')

     ax2.set_ylabel("Water Level Elevation [ft amsl]", color='g')

     for tl in ax2.get_yticklabels():
          tl.set_color('g')

     fig.suptitle('GWSI Site: ' + str(location) + ', RegID: 55-' + str(int(df3["Reg_No"].iloc[0])) + ', Depth: ' + str(int(df3["Depth"].iloc[0]))+ ' ft', fontsize=12)

     ax1.grid(b=True, which='major', color='#666666', linestyle='-')

     myFmt = DateFormatter("%Y")
     ax1.xaxis.set_major_formatter(myFmt)
     years = YearLocator()
     ax1.xaxis.set_major_locator(YearLocator())
     ax1.format_xdata = DateFormatter('%Y-%m-%d')
     
     ax1.set_xlim(min_date_datetime, max_date_datetime)
     
     
     for tick in ax1.get_xticklabels():
          tick.set_rotation(90)

     plt.rcParams.update({'font.size': 12})

     plt.show()

     outname = str('Hydrographs_GWSI_') + str(location) + str('__Transducer.png')
     fig.savefig(outname, dpi = 400, bbox_inches='tight', pad_inches=.1)

     outname = str('GWSI_WLE_ZipExtract_SCAMAbc_') + str(location) + str('__Raw_Data_Table.csv')
     df3.to_csv(outname, index=False)


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


##subset2
wells = list([314408111034701, 314406111033701, 314201111023901, 314309111031601, 314230111025701, 314257111033401, 314338111033101, 314436111015001, 314448111023301, 314201111033701, 313836111033001, 313958111023301, 
313820111033301, 313414111100501, 314116111033701, 314230111034501, 314148111030001, 314044111033201, 314411111031001, 314222111025601, 314117111033801, 313920111033301, 314024111030201, 314421111003701, 
314200111023701, 313856111034401, 314258111054501, 314353111001201, 314229111030301, 314015111033401, 314427111023501, 313959111032401, 313851110012303, 314401111031801, 314248111033801, 314357111020301, 
314249111033901, 314347111041101, 314402111025101, 313940111030901, 314446111022801, 314416111015901, 314341111034201, 314224111035401, 314342111025401, 314156111030301, 314058111034301, 314028111042601, 
314359111033701, 314242111025201, 314242111023901, 314335111025001, 314434111025501, 313851111012201, 313915111052001, 314202111034001, 314058111031001, 314336111034101, 314251111045401, 313859111023901, 
314300111060901, 314435111025601, 314148111055101, 313939111032401, 314256111044601, 313832111022801, 314029111023301, 314334111030601, 314302111052901, 314312111030601, 314157111003701, 314150111031701, 
314008111033501, 313849111030001, 314303111032801, 314413111030001, 314214111025601, 314454111023701, 313845111023101])




##
###SET GRAPH STYLE, FORMATTING
#import seaborn as sns
#sns.set_style("darkgrid")

import datetime
Time_Start = datetime.datetime.now()
Time_End = datetime.datetime.now()
Run_Time = Time_End - Time_Start


#
#Find kernel's current directory, update to desired location if necessary
Path = r"C:\GIS\ADWR\PythonOutput"
os.chdir(Path)
cwd = os.getcwd()


"""
###############################################################################
#  ### ### ### ### ### #### ### ### ### ### ### #### ### ### ### ### ### ###  #
##   Websites Visited   ##
"""
https://thispointer.com/python-pandas-how-to-drop-rows-in-dataframe-by-conditions-on-column-values/


GOOD ONES:
https://code-examples.net/en/q/18a788c

https://stackoverflow.com/questions/151199/how-to-calculate-number-of-days-between-two-given-dates

from datetime import date

d0 = date(2008, 8, 18)
d1 = date(2008, 9, 26)
delta = d1 - d0
print(delta.days)



https://stackoverflow.com/questions/25852044/converting-pandas-tslib-timestamp-to-datetime-python

https://www.geeksforgeeks.org/python-pandas-series-astype-to-convert-data-type-of-series/

https://stackoverflow.com/questions/54312802/pandas-convert-from-datetime-to-integer-timestamp
"""