###########################################
# Suppress matplotlib user warnings
# Necessary for newer version of matplotlib
import warnings
warnings.filterwarnings("ignore", category = UserWarning, module = "matplotlib")
#
# Display inline matplotlib plots with IPython
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')
###########################################

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import datetime
import seaborn as sns
        
def form_labels(min_value, max_value, bin_size = 10):
	age_list = iter(list(range(min_value, max_value, bin_size)))
	
	age_labels = []
	next(age_list)
	for age in age_list:
		age_labels.append(age-1)
		
	return age_labels
    
def filter_data(data, condition):

    field, op, value = condition.split(" ")
    
    # convert value into number or strip excess quotes if string
    try:
        value = float(value)
    except:
        value = value.strip("\'\"")
    
    # get booleans for filtering
    if op == ">":
        matches = data[field] > value
    elif op == "<":
        matches = data[field] < value
    elif op == ">=":
        matches = data[field] >= value
    elif op == "<=":
        matches = data[field] <= value
    elif op == "==":
        matches = data[field] == value
    elif op == "!=":
        matches = data[field] != value
    else: # catch invalid operation codes
        raise Exception("Invalid comparison operator. Only >, <, >=, <=, ==, != allowed.")
    
    # filter data and outcomes
    data = data[matches].reset_index(drop = True)
    return data
    

def plot_appointment_no_show_stats_age(data, title, xlabel, ylabel):
    age_labels = form_labels(0, data['Age'].max() + 2, 1)
    bins = np.arange(0, data['Age'].max() + 2, 1)
    data['AgeGroup'] = pd.cut(data.Age, bins, right=False, labels=age_labels)
    
    age_noshow_count = pd.crosstab(data['No-show'],data['AgeGroup'])
    
    sorted_list = sorted(data['AgeGroup'].unique(), key=lambda x: float(x))
    
    tmp_df_list = []
    for age_label in sorted_list :
        tmp_df_list.append([age_label, age_noshow_count[age_label]['Yes'], age_noshow_count[age_label]['No']])
        
    group_by_age_data = pd.DataFrame(tmp_df_list,columns=['AgeGroup', 'AbsentCount', 'PresentCount'])
    group_by_age_data['Total'] = group_by_age_data['AbsentCount'] + group_by_age_data['PresentCount']
    group_by_age_data['AbsentPercent'] = (group_by_age_data['AbsentCount']/ group_by_age_data['Total']) * 100
    
    
    plt.scatter(group_by_age_data['AgeGroup'], group_by_age_data['AbsentPercent'])
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
def add_dayOfWeek_to_dataset(data):
    days = {0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'}
    
    data['AppointmentDay'] = data['AppointmentDay'].apply(np.datetime64)
    data['DayOfWeek'] = data['AppointmentDay'].dt.weekday
    data['DayOfWeek'] = data['DayOfWeek'].apply(lambda x: days[x])
    
    
    
def calculate_appointment_no_show_stats(data, params):
    tmp_df_list = []
    for param in params:
        for level in data[param].unique():
            tmp_df_list.append([param, level, len(data[(data[param] == level) & (data['No-show'] == 'Yes')]), len(data[(data[param] == level) & (data['No-show'] == 'No')])])
            
    group_by_params_data = pd.DataFrame(tmp_df_list, columns=['Param', 'Level', 'AbsentCount', 'PresentCount'])
    group_by_params_data['Total'] = group_by_params_data['AbsentCount'] + group_by_params_data['PresentCount']
    group_by_params_data['AbsentPercent'] = (group_by_params_data['AbsentCount']/ group_by_params_data['Total']) * 100
    
    print (group_by_params_data)
    return group_by_params_data
    
def draw_graph(dataset, x_feature, y_feature, hue, title, xlabel, ylabel, hue_order = None):

    data_plot = sns.barplot(data = dataset, x = x_feature, y = y_feature, hue = hue, palette = 'Set3', hue_order = hue_order)
    plt.legend(bbox_to_anchor=(1, 1), loc=2)
    
    plt.title(title)
    data_plot.set(xlabel=xlabel, ylabel=ylabel)
    plt.show()
    
def plot_appointment_no_show_stats(data, key, filters = []):

    for condition in filters:
        data = filter_data(data, condition)
        
    if key == 'Age':
        plot_appointment_no_show_stats_age(data, 'No-Show Rate depending on Age', 'Patient’s Age', 'Percentage of No-Shows')
    elif key == 'DayOfWeek':
        add_dayOfWeek_to_dataset(data)
        group_by_dayOfWeek_data = calculate_appointment_no_show_stats(data, ['DayOfWeek'])
        draw_graph(group_by_dayOfWeek_data, 'Param', 'AbsentPercent', 'Level', 'No-Show Rate depending on DayOfWeek', 
                  'Day of Week', 'Percentage of No-Shows', hue_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    elif key == 'Handcap':
        group_by_handicap_data = calculate_appointment_no_show_stats(data, ['Handcap'])
        draw_graph(group_by_handicap_data, 'Param', 'AbsentPercent', 'Level', 'No-Show Rate depending on Handicap Level', 
                  'Handicap Levels', 'Percentage of No-Shows')
    elif key == 'sms':
        group_by_sms_data = calculate_appointment_no_show_stats(data, ['SMS_received'])
        draw_graph(group_by_sms_data, 'Param', 'AbsentPercent', 'Level', 'No-Show Rate depending on SMS received', 
                  'SMS state', 'Percentage of No-Shows')
    elif key == 'other':
        group_by_diseases_data = calculate_appointment_no_show_stats(data, ['Diabetes', 'Alcoholism', 'Hipertension', 'Scholarship'])
        draw_graph(group_by_diseases_data, 'Param', 'AbsentPercent', 'Level', 'No-Show Rate depending on diseases/behaviors and scholarship', 
                  'Disease/Behavior/Scholarship', 'Percentage of No-Shows')

def plot_appointment_turnup_by_gender(data):
    data = data[data['No-show'] == 'No']
    age_df = pd.DataFrame()
    age_df['Age'] = range(data['Age'].max() + 2)
    men = age_df.Age.apply(lambda x: len(data[(data.Age == x) & (data.Gender == 'M')]))
    women = age_df.Age.apply(lambda x: len(data[(data.Age == x) & (data.Gender == 'F')]))
    plt.plot(range(data['Age'].max() + 2),men, 'b')
    plt.plot(range(data['Age'].max() + 2),women, color = 'r')
    plt.legend(['M','F'])
    plt.xlabel('Age of patient')
    plt.ylabel('Number of visits')
    plt.title('Number of Doctor Visits by Gender')
    plt.show()