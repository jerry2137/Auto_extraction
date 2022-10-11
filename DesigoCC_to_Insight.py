import pandas as pd
import os
from datetime import datetime
import sys


def to_insight(source_filename, output_filename):

    dataframe = pd.read_csv(source_filename, sep = ';')

    dataframe = dataframe[dataframe.DateTime != "DateTime"]
    dataframe.loc[dataframe['Value'] == 'ON', 'Value'] = 1
    dataframe.loc[dataframe['Value'] == 'OFF', "Value"] = 0
    dataframe = dataframe[dataframe['Data Source'].notna()]
    dataframe['Value'] = dataframe['Value'].astype(float)
    dataframes = dataframe.groupby('Data Source')

    wanted_df = pd.DataFrame(columns=['DateTime'])
    point_dict = {}
    for i, name_data in enumerate(dataframes):
        name = name_data[0]
        data = name_data[1]
        point = 'Point_' + str(i + 1) + ':'
        point_dict[point] = name

        data.rename(columns = {'Value':point}, inplace = True)
        data.drop_duplicates(point)

        wanted_df = wanted_df.merge(data[['DateTime', point]], on='DateTime', how='outer')
    wanted_df = wanted_df.fillna(0)

    wanted_df['DateTime'] = pd.to_datetime(wanted_df.DateTime)
    wanted_df = wanted_df.sort_values('DateTime')

    wanted_df['<>Date'] = pd.to_datetime(wanted_df['DateTime']).dt.date
    wanted_df.insert(0, '<>Date', wanted_df.pop('<>Date'))

    wanted_df['DateTime'] = pd.to_datetime(wanted_df['DateTime']).dt.time
    wanted_df.rename(columns = {'DateTime':'Time'}, inplace = True)

    time_dict = {}
    time_dict['Time Interval:'] = str(wanted_df['Time'][1].minute - wanted_df['Time'][0].minute) + ' Minutes'
    first_time = datetime.combine(wanted_df['<>Date'][0], wanted_df['Time'][0]).strftime("%m/%d/%Y %H:%M:%S")
    last_time = datetime.combine(wanted_df['<>Date'].iloc[-1], wanted_df['Time'].iloc[-1]).strftime("%m/%d/%Y %H:%M:%S")
    time_dict['Date Range:'] = first_time + ' - ' + last_time
    time_dict['Report Timings:'] = 'All Hours'

    point_info_df = pd.DataFrame(point_dict.items())
    point_info_df[['blank1', 'blank2']] = ''
    time_info_df = pd.DataFrame(time_dict.items())
    
    first_row_df = pd.DataFrame(['Key            Name:Suffix                                Trend Definitions Used'])
    last_row_df = pd.DataFrame([' ******************************** End of Report *********************************'])

    
    with open(output_filename,'a') as output_file:
        first_row_df.to_csv(output_file, index=None, header=None)
        point_info_df.to_csv(output_file, index=None, header=None)
        time_info_df.to_csv(output_file, index=None, header=None)
        output_file.write('\n')
        wanted_df.to_csv(output_file, index=None)
        last_row_df.to_csv(output_file, index=None, header=None)

if __name__ == '__main__':
    to_insight(sys.argv[1], sys.argv[2])
    #to_insight('test_input.csv', 'test_output.csv')
