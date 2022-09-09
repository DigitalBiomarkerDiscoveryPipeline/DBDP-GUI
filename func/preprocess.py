# additional libraries for preprocessing 
import pandas as pd
import numpy as np
import lxml.etree
import seaborn as sns
from datetime import *
import datetime 
from pytz import timezone
import os
import sys
import json
import re
import mne


# garmin preprocessing


# will create a separate py file



def garmin(user_input):
    
    def read_tcx(fname):
        tree = lxml.etree.parse(fname)
        NAMESPACES = {
        'ns': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
        'ns2': 'http://www.garmin.com/xmlschemas/UserProfile/v2',
        'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
        'ns4': 'http://www.garmin.com/xmlschemas/ProfileExtension/v1',
        'ns5': 'http://www.garmin.com/xmlschemas/ActivityGoals/v1'
    }
        root = tree.getroot()
        activity = root.find('ns:Activities', NAMESPACES)[0]
        track = activity[1][8]
        time = []
        distancemeters = []
        HR = []
        #tracks = 0
        for t in track.findall('ns:Trackpoint', NAMESPACES):
            #tracks+=1
            #print(tracks+1)
            time.append(t.find('ns:Time', NAMESPACES).text)
            distancemeters.append(t.find('ns:DistanceMeters', NAMESPACES).text)
            if t.find('ns:HeartRateBpm', NAMESPACES) != None:
                HR.append(float((t.find('ns:HeartRateBpm', NAMESPACES).find('ns:Value', NAMESPACES).text)))
            else:
                HR.append(np.nan)

        df = pd.DataFrame({"TimeStamp_(sec)": time, "Distancemeters": distancemeters, "Hrcur_(bpm)": HR})
        
        return df
        

    df = read_tcx(user_input)
    df['TimeStamp_(sec)'] = pd.to_datetime(df['TimeStamp_(sec)'])
    df['Elapsed_time_(sec)'] = (df['TimeStamp_(sec)'] - df['TimeStamp_(sec)'][0]).dt.total_seconds()
    df = df.rename(columns ={'TimeStamp_(sec)': 'Actual_time',
                                    'Hrcur_(bpm)' : 'HR_Garmin'})
    df['HR_Garmin'] = pd.to_numeric(df['HR_Garmin'], errors = 'coerce')                                
    df = df[['Actual_time', 'Elapsed_time_(sec)','HR_Garmin']]

    return(df)

def apple(user_input):

    def dict_df(df):
        for i in range(0,len(df)):
            in_strip = df[df[0].str.contains("Time")].index[0]
            dictdf = df.loc[:(in_strip-1), :]
            dictdf = dictdf.set_index(0).T.to_dict('list')
            df = df.loc[in_strip:, :]
            return dictdf, df
    
    def pre_process_apple(df):
        df = df.reset_index()
        df = df.drop('index', axis = 1)
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header
        return df
    
    def add_time(df, start_time):
        delta = []
        df['Actual_time'] = 'NaN'
        for i in range(len(df)):
            df.iloc[i]['Time_(seconds)'] = df.iloc[i]['Time_(seconds)'].replace(" ", "")
            delta_sec = float(df.iloc[i]['Time_(seconds)'])
            delta_time = timedelta(seconds = delta_sec)
            delta.append(delta_time)
            df['Actual_time'].iloc[i] = start_time + delta[i]
        return df
    
 
    df = pd.read_csv(user_input, header = None)
    dictdf, df = dict_df(df)
    start_time = dictdf['Workout date'][0]
    start_time = datetime.datetime.strptime(start_time, ' %Y-%m-%d %H:%M:%S ')

    df = pre_process_apple(df)

    df.columns = df.columns.str.lstrip(' ')
    df.columns = df.columns.str.replace(' ','_')
    df = add_time(df, start_time)

    df["Time_(seconds)"] = pd.to_numeric(df["Time_(seconds)"], errors = 'coerce')
    df["Rate_(beats_per_minute)"] = pd.to_numeric(df["Rate_(beats_per_minute)"], errors = 'coerce')
    
    df = df.rename(columns = {"Rate_(beats_per_minute)": 'HR_Apple', "Time_(seconds)": 'Elapsed_time_(sec)'})
    return df


def ecg(user_input):
    
    data = mne.io.read_raw_edf(user_input)
    raw_data = data.get_data()
    info = data.info
    channels = data.ch_names
    ECG_array = raw_data[0]
    
    def get_data(data):
        header = ','.join(data.ch_names)
        np.savetxt('ECG.csv', data.get_data().T, delimiter=',', header=header)
        ECG_df = pd.read_csv("./ECG.csv")
        info = data.info
        return ECG_df, info
    
    def pre_process_ECG(df):
        df = df.drop('Marker', axis = 1)
        df = df.drop('HRV', axis = 1)
        return df
    
    def add_time(df, info):
        start_time = info['meas_date']
        sfreq = info['sfreq']
        delta_sec = 1/sfreq
        delta_sec = datetime.timedelta(seconds = delta_sec)
        ECG_time = [start_time]
        df['Elapsed_time_(sec)'] = np.nan
        for i in range(1,len(df)):
            time = ECG_time[i-1] + delta_sec
            ECG_time.append(time)
        df['Actual_time'] = ECG_time
        df['Elapsed_time_(sec)'] = df['Actual_time'].apply(lambda x : (x-start_time).total_seconds())
        return df

    no_patient = 1
    df, info = get_data(data)
    df = pre_process_ECG(df)
    df.columns = df.columns.str.lstrip(' ')
    df.columns = df.columns.str.replace(' ','_')
    df = add_time(df, info)
    df = df.rename(columns ={'#_ecg' : 'ECG_(mV)'})

    return(df)



def fitbit(user_input):
    
  
    def add_time(df, start_time):
        df['Elapsed_time_(sec)'] = 'NaN'
        start_time = datetime.datetime.strptime(df['Time'][0], '%H:%M:%S')
        for i in range(len(df)):
            df['Elapsed_time_(sec)'].iloc[i] = (datetime.datetime.strptime(df.iloc[i][0], '%H:%M:%S')-start_time).total_seconds()
        return df
   
    df = pd.read_csv(user_input)
    df.columns = df.columns.str.lstrip(' ')
    df.columns = df.columns.str.replace(' ','_')
    start_time = df.iloc[0][0]
    df = add_time(df, start_time)
    df = df.rename(columns ={'Time' : 'Actual_time', 'Heart_Rate' : 'HR_Fitbit'})
    df["Elapsed_time_(sec)"] = pd.to_numeric(df["Elapsed_time_(sec)"], errors = 'coerce')
    df["HR_Fitbit"] = pd.to_numeric(df["HR_Fitbit"], errors = 'coerce')
    
    return df



def empatica(user_input, data_type = []):
    def preprocess_empatica(dataframe):
        time = dataframe.values[0]
        freq = dataframe.values[1]
        dataframe = dataframe.iloc[2:]
        dataframe = dataframe.reset_index()
        dataframe = dataframe.drop('index', axis = 1)
        return dataframe, time, freq

    def get_filenames(user_input):
        newnames = []
        files = os.listdir(user_input)    
        filenames = list(filter(lambda f: f.endswith('.csv'), files))
        return filenames

    def add_time_empatica(dataframe, time, freq, filename):
        dataframe['Timestamp' + '_' + str(filename)] = time[0]
        delta = 1/freq[0]
        delta = datetime.timedelta(seconds = delta)
        start_time = datetime.datetime.utcfromtimestamp(time[0]).strftime('%Y-%m-%d %H:%M:%S')
        start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        actual_time = [start_time]
        for i in range(1, len(dataframe)):
            time = actual_time[i-1] + delta
            actual_time.append(time)
        dataframe['Actual_time'+ '_' + str(filename)] = actual_time
        dataframe['Elapsed_time_(sec)'+ '_' + str(filename)] = dataframe['Actual_time'+ '_' + str(filename)].apply(lambda x : (x-start_time).total_seconds())
        return dataframe

    def read_data(user_input, filenames, preprocess_empatica, add_time_empatica):
        dataframes = []
        for file in filenames:
            dataframe = pd.read_csv(user_input + '/' + str(file), header = None)
            file = file.split(".")[0]
            file = file.upper()

            if 'ACC' in file:

                dataframe, time, freq = preprocess_empatica(dataframe)
                dataframe = dataframe.rename(columns = {0 : 'x_acc', 1: 'y_acc', 2: 'z_acc'})

                dataframe['Actual_time_x'] = np.nan
                dataframe['Actual_time_y'] = np.nan
                dataframe['Actual_time_z'] = np.nan

                dataframe['Timestamp_x'] = time[0]
                dataframe['Timestamp_y'] = time[1]
                dataframe['Timestamp_z'] = time[2]

                delta_x = 1/freq[0]
                delta_x = datetime.timedelta(seconds = delta_x)
                delta_y = 1/freq[1]
                delta_y = datetime.timedelta(seconds = delta_y)
                delta_z = 1/freq[2]
                delta_z = datetime.timedelta(seconds = delta_z)   

                start_timex = datetime.datetime.utcfromtimestamp(time[0]).strftime('%Y-%m-%d %H:%M:%S')
                start_timex = datetime.datetime.strptime(start_timex, '%Y-%m-%d %H:%M:%S')
                start_timey = datetime.datetime.utcfromtimestamp(time[1]).strftime('%Y-%m-%d %H:%M:%S')
                start_timey = datetime.datetime.strptime(start_timey, '%Y-%m-%d %H:%M:%S')
                start_timez = datetime.datetime.utcfromtimestamp(time[2]).strftime('%Y-%m-%d %H:%M:%S')
                start_timez = datetime.datetime.strptime(start_timez, '%Y-%m-%d %H:%M:%S')

                accx_time = [start_timex]
                accy_time = [start_timey]
                accz_time = [start_timez]

                for i in range(1, len(dataframe['x_acc'])):
                    time_x = accx_time[i-1] + delta_x
                    accx_time.append(time_x)
                dataframe['Actual_time_x'] = accx_time
                dataframe['Elapsed_timex_(sec)'] = dataframe['Actual_time_x'].apply(lambda x : (x-start_timex).total_seconds())

                for i in range(1, len(dataframe['y_acc'])):
                    time_y = accy_time[i-1] + delta_y
                    accy_time.append(time_y)
                dataframe['Actual_time_y'] = accy_time
                dataframe['Elapsed_timey_(sec)'] = dataframe['Actual_time_x'].apply(lambda x : (x-start_timex).total_seconds())

                for i in range(1, len(dataframe['z_acc'])):
                    time_z = accz_time[i-1] + delta_z
                    accz_time.append(time_z)
                dataframe['Actual_time_z'] = accz_time
                dataframe['Elapsed_timez_(sec)'] = dataframe['Actual_time_x'].apply(lambda x : (x-start_timex).total_seconds())

            if 'BVP' in file:
                dataframe, time, freq = preprocess_empatica(dataframe)
                dataframe = dataframe.rename(columns = {0 : 'BVP'})
                dataframe = add_time_empatica(dataframe, time, freq, 'BVP')            

            if 'EDA' in file:
                dataframe, time, freq = preprocess_empatica(dataframe)
                dataframe = dataframe.rename(columns = {0 : 'EDA(microsiemens)'})
                dataframe = add_time_empatica(dataframe, time, freq, 'EDA')

            if 'HR' in file:
                dataframe, time, freq = preprocess_empatica(dataframe)
                dataframe = dataframe.rename(columns = {0 : 'HR'})
                dataframe = add_time_empatica(dataframe, time, freq, 'HR')

            if 'IBI' in file:
                ibi_time = dataframe.iloc[0][0]
                dataframe = dataframe.iloc[1:]
                dataframe = dataframe.rename(columns = {0 : 'Time(sec)', 1: 'IBI'})
                dataframe = dataframe.reset_index()
                dataframe = dataframe.drop('index', axis = 1)

            if 'TEMP' in file:
                dataframe, time, freq = preprocess_empatica(dataframe)
                dataframe = dataframe.rename(columns = {0 : 'Temp(celsius)'})
                dataframe = add_time_empatica(dataframe, time, freq, 'Temp')

            if 'TAGS' in file:
                dataframe = dataframe.rename(columns = {0 : 'Timestamp_buttonpress'})
                dataframe['Time'] = dataframe['Timestamp_buttonpress'].apply(lambda a : datetime.datetime.utcfromtimestamp(a).strftime('%Y-%m-%d %H:%M:%S'))
            dataframes.append(dataframe)
        return dataframes

    def all_dfs(dataframes):
        df = pd.concat(dataframes, axis = 1)
        return df

    
    filenames = get_filenames(user_input)

    dataframes = read_data(user_input, filenames, preprocess_empatica, add_time_empatica)
    df = all_dfs(dataframes)

    if data_type == "HR":
        df = df[['Actual_time_HR', 'Elapsed_time_(sec)_HR','HR']]
        df.rename(columns = {'Actual_time_HR': 'Actual_time', 
                            'Elapsed_time_(sec)_HR': 'Elapsed_time_(sec)', 
                            'HR': 'HR_Empatica'}, inplace = True)
        df = df.dropna(how='all')
    
    return(df)

def resample_and_interpolate(df, interpolate_col, resample_step = 1, interpolate = True):
    
    temp = df.copy()
    temp = temp[[interpolate_col,'Elapsed_time_(sec)']]
    
    temp['Elapsed_time_(sec)'] = np.ceil(temp['Elapsed_time_(sec)'])
    resampled_df = pd.DataFrame({'Elapsed_time_(sec)': np.arange(0,temp['Elapsed_time_(sec)'].max(), resample_step)})
    resampled_df = resampled_df.merge(temp, on = 'Elapsed_time_(sec)', how = 'left')
    
    if interpolate:
        resampled_df[interpolate_col].interpolate(inplace = True)
    else:
        resampled_df[interpolate_col].fillna(method = 'ffill', inplace = True)
    
    return resampled_df