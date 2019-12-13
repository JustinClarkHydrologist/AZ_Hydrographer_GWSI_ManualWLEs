"""     Python GWSI Water Levels Grapher  -  VERSION 2.3
             Started on 6/04/2019
             Last Updated 11/27/2019 (November 27 2019, I am American)

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
#from matplotlib import dates

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


#errors = list([343317111504901, 315110110134301])
#wells.remove(errors)

##subset1
#wells = ([313845111023101,313851111012201,313920111033301,313958111023301,314015111033401,314148111055101,314150111031701])
#
#wells = ([313920111033301,314015111033401])
















for location in wells:
     ##THIS FIRST SECTION MAKES THE WELL SPECIFIC DATAFRAME
     df3 = df.loc[df[col] == location].copy()
###     df3 = df.loc[df[col] == location] ##WARNING POPPED UP
###     df3 = df.loc[df[col] == location, :]

#     ###THE NEXT STEP COULD PROBABLY BE DONE BY RE-INDEXING "df3.Date"
#     df3['UpDate'] = pd.to_datetime(df3.Date)
#     df3 = df3.sort_values('UpDate')
     
######     df3['Date'] = pd.to_datetime(df3.Date)
     df3 = df3.sort_values('Date')
     
     ##EXTRACT THE ELEVATION OF THE GROUND AT THIS WELL FROM df2
     ##THIS METHOD GIVES A WARNING, FIX LATER
     elev = df2[df2[col]==location]['SITE_WELL_ALTITUDE']
     df3['LSE'] = elev.iloc[0]
     
     ##CALCULATE THE WLE FOR EACH MEASUREMENT BASED ON LSE AND DTW
     ##THIS STEP SHOULD NOT BE NECESSARY, SHOWS A POTENTIAL ERROR IN THE DATABASE
     df3['WLE_Calc'] = df3['LSE'] - df3['DEPTH_TO_WATER']
     
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

     ##THIS SECTION DELETES "ZERO ERRORS"
     df3.drop( df3[ df3['DEPTH_TO_WATER'] == 0 ].index , inplace=True)
     
     dimensions = df3.shape
     row_count = dimensions[0]
     if row_count == 0:
          bad_wells.append(location)
     
     else:

          #
          ## THIS SECTION DEFINES AXES MIN/MAX
          min_date_str = df3['Date'].min()
          min_date_datetime = min_date_str.date()
          min_date_4fig = min_date_datetime.replace(month = 1)
          min_date_4fig = min_date_4fig.replace(day = 1)
          min_date_4fig = pd.to_datetime(min_date_4fig)
     #     test0 = min_date_4fig - pd.offsets.DateOffset(years=1)
     #     min_datetime_4fig = pd.to_datetime(min_date_4fig)
          min_datetime_4fig = min_date_4fig.to_pydatetime()##BACK AND FORTH
          
          max_date_str = df3['Date'].max()
          max_date_datetime = max_date_str.date()
          max_date_4fig = max_date_datetime + pd.offsets.DateOffset(years=1)
          max_date_4fig = max_date_4fig.replace(month = 1)
          max_date_4fig = max_date_4fig.replace(day = 1)
     
     #     max_date_4fig = max_date_str.date()
     #     max_date_4fig = max_date_datetime.replace(month = 12)
     #     max_date_4fig = max_date_4fig.replace(day = 31)
          max_datetime_4fig = pd.to_datetime(max_date_4fig)
          max_datetime_4fig = max_datetime_4fig.to_pydatetime()
     
     #     total_days = max_date_datetime - min_date_datetime
          total_days = max_date_4fig - min_date_4fig
          int_days = total_days.days
     
          x = df3['Date']
          y1 = df3['DEPTH_TO_WATER']
          y2 = df3['WLE_Calc']
     
          plt.xlabel("Date")
          plt.rcParams['xtick.labelsize']=8
     
          fig = plt.figure()
          ax1 = fig.add_subplot(111)
     
          ax1.plot(x, y1)
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
     #     ax1.format_xdata = DateFormatter('%Y-%m-%d')
     
     
     #     test2 = min_datetime_4fig.to_pydatetime()
     #     test3 = min_date_4fig.to_pydatetime()
     #     test4 = min_datetime_4fig.to_pydatetime()
     
          #SET AXIS xlim
     #     ax1.set_xlim(left = min_date_4fig,right = max_date_4fig)
     #     ax1.set_xlim([datetime.date(1940, 1, 1),datetime.date(2019, 12, 31)])
          ax1.set_xlim([min_datetime_4fig,max_datetime_4fig])
     #     ax1.set_xlim([min_date_4fig,max_date_4fig])
     #     ax2.set_xlim(right = max_date_4fig)
     
     #     ax1.set_xlim([datetime.date(1940, 1, 1), datetime.date(2019, 12, 31)])
     #     test = datetime.date(1940, 1, 1)
     #     ax1.set_xlim(min_date_datetime, max_date_datetime)
     
          yrs=int_days / 365.25
          x_ticks = 1 #ANNUAL X-TICKS
          if yrs > 40:
               x_ticks = 2
     
          ax1.xaxis.set_major_locator(YearLocator(x_ticks))#THIS WORKS
     #     ax1.xaxis.set_major_locator(YearLocator(2))
          
     #     ##TRIED TO ADD IN AN OFFSET FOR GRAPHS STARTING IN ODD YEARS WITH INTERVAL OF 2 YRS
     #     year1 = x_ticks.OffsetYearLocator(2, month=1, day=1, offset=1)
     #     ax1.xaxis.set_major_locator(YearLocator(year1))
     
          for tick in ax1.get_xticklabels():
               tick.set_rotation(90)
     
          plt.rcParams.update({'font.size': 12})
     
          plt.show()
     
          outname = str('Hydrographs_GWSI_') + str(location) + str('__Transducer.png')
          fig.savefig(outname, dpi = 400, bbox_inches='tight', pad_inches=.1)

















print(bad_wells)





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






wells = list(set(df5['S']))
skiplines = 4176-19 ##Files in folder - 19
wells = list(set(df5['S']) - set(bad_wells))

wells = wells[skiplines:]




bad_df = pd.DataFrame(bad_wells)
outname = str('BadWells__GWSI_WLE_ZipExtract_20191205_2PM.csv')
bad_df.to_csv(outname, index=False)

wells_df = pd.DataFrame(wells)
outname = str('Wells_Good__GWSI_WLE_ZipExtract_20191206.csv')
wells_df.to_csv(outname, index=False)

320522110534701 or 32052211053470

#     outname = str('GWSI_WLE_ZipExtract_SCAMAbc_') + str(location) + str('__Raw_Data_Table.csv')
#     df3.to_csv(outname, index=False)






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
t_wells = list([314408111034701, 314406111033701, 314201111023901, 314309111031601, 314230111025701, 314257111033401, 314338111033101, 314436111015001, 314448111023301, 314201111033701, 313836111033001, 313958111023301, 
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
import os
Path = r"C:\GIS\ADWR\PythonOutput"
os.chdir(Path)
cwd = os.getcwd()

outname = str('GWSI_WLE_ZipExtract_LOCATIONS__Raw_Data_Table.csv')
df2.to_csv(outname, index=False)

outname = str('GWSI_WLE_ZipExtract_OBSERVATIONS__Raw_Data_Table.csv')
df.to_csv(outname, index=False)




test_locations = df[col].value_counts()
test_wells = pd.DataFrame(test_locations)

df_wells = pd.DataFrame(wells)

outname = str('GWSI_WLE_ZipExtract_CountLoc.csv')
df_wells.to_csv(outname, index=False)
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


#import pandas as pd
#from simpledbf import Dbf5
#database_name = 'C:\GIS\ADWR\GWSI\WellConstruction_GWSI_Sites_Extract201904_Tucson__zn1.dbf'
#dbf = Dbf5(database_name)
#df4 = dbf.to_dataframe()
#GWSI_ID = "SITE_ID"
#wells = list(set(df4[GWSI_ID].astype('int64')))



wells = list(set(df4[GWSI_ID])) -  set([
          320012111264101])

remove_me = set([331306111074301,315628110430201])
wells = list(set(df4[GWSI_ID].astype('int64')) - remove_me)


outname = str('GWSI_WLE_ZipExtract__TucsonAMA_6089wells.csv')
df4.to_csv(outname, index=False)

print(wells)

for element in wells:
     print(type(element))

location = int(315628110430201)


csv_name = "GWSI_WLE_ZipExtract__TucsonAMA_4557wells.csv"
df5 = pd.read_csv(csv_name, names = "S", index_col = None, header = None)
#wells = list(df5['S'])
remove_me = set([331306111074301,314401111031801])
wells = list(set(df5['S']) - remove_me)


     
     
wells = list(set(df5['S']))

