#!/usr/bin/env python
# coding = utf-8

import pandas as pd
import sys
import timeit
import os

'''
data loading and preview
'''
start_time  = timeit.default_timer()

with open(r"F:\tianchi\fresh_comp_offline\fresh_comp_offline\tianchi_fresh_comp_train_user.csv") as data_file_user:
    chunks_user = pd.read_csv(data_file_user,iterator=True)
with open(r"F:\tianchi\fresh_comp_offline\fresh_comp_offline\tianchi_fresh_comp_train_item.csv") as data_file_item:
    chunks_item = pd.read_csv(data_file_item,iterator=True)

chunks_user = chunks_user.get_chunk(5)
chunks_item = chunks_item.get_chunk(5)
print(chunks_user)
print(chunks_item)

'''
data pre_analysis
'''
#################
#calculation of CTR
#################

count_all = 0
count_4 = 0 # the count of behavior_type = 4
for df in pd.read_csv(open(r"F:\tianchi\fresh_comp_offline\fresh_comp_offline\tianchi_fresh_comp_train_user.csv",'r'),
                      chunksize = 100000):
    try:
        count_user = df['behavior_type'].value_counts()
        count_all += count_user[1]+count_user[2]+count_user[3]+count_user[4]
        count_4 +=count_user[4]
    except StopIteration:
        print("Iteration is stopped")
        break
#CTR
ctr = count_4 / count_all
print(ctr)

###################
#visualization month record based on data(11-18->12-18)
###################

count_day = {} #using dictionary for data_count pairs
for i in range(31): #initial dictionary
    if i <= 12:
        data = '2014-11-%d'%(i+18)
    else:
        data = '2014-12-%d'%(i-12)
    count_day[data] = 0

batch = 0
dateparse = lambda dates:pd.datetime.strptime(dates,'%Y-%m-%d %H')
for df in pd.read_csv(open(r"F:\tianchi\fresh_comp_offline\fresh_comp_offline\tianchi_fresh_comp_train_user.csv",'r'),
                      parse_dates=['time'],index_col = ['time'],date_parser=dateparse,
                      chunksize = 100000):
    try:
        for i in range(31):
            if i <= 12:
                date = '2014-11-%d' %(i + 18)
            else:
                date = '2014-12-%d' %(i-12)
            count_day[date] += df[date].shape[0]   #截取每天的数据量
        batch += 1
        print('chunk %d done.'%batch)

    except StopIteration:
        print("finish data process")
        break
from dict_csv import *
row_dict2csv(count_day,r"F:\tianchi\fresh_comp_offline\fresh_comp_offline\count_day.csv")

df_count_day = pd.read_csv(open(r"F:\tianchi\fresh_comp_offline\fresh_comp_offline\count_day.csv"),
                           header = None,
                           names = ['time','count'])

import matplotlib.pyplot as plt

df_count_day = df_count_day.set_index('time')
#df_count_day.index = pd.DatetimeIndex(df_count_day.index)
df_count_day = df_count_day.sort_index()
print(df_count_day)
# x_date =df_count_day.index.get_values()
# y = df_count_day['count'].get_values()

df_count_day['count'].plot(kind = 'bar')
plt.legend(loc = 'best')
plt.title('behavior count of P by date')
plt.grid(True)
plt.show()

############################
#visualization based on hour
############################

count_hour_1217 = {} #using dictionary for hour-count pairs
count_hour_1218 = {} #4 types of behavior formed as {key:counts list of 1/2/3/4}
for i in range(24):
    time_str17 = '2014-12-17 %02.d'%i
    time_str18 = '2014-12-18 %02.d'%i
    count_hour_1217[time_str17] = [0,0,0,0]
    count_hour_1218[time_str18] = [0,0,0,0]

batch = 0
dateparse = lambda dates:pd.datetime.strptime(dates,'%Y-%m-%d %H')
for df in pd.read_csv(open(r"F:\tianchi\fresh_comp_offline\fresh_comp_offline\tianchi_fresh_comp_train_user.csv",'r'),
                      parse_dates = ['time'],
                      index_col = ['time'],
                      date_parser = dateparse,
                      chunksize = 50000):
    try:
        for i in range(24):
            time_str17 = '2014-12-17 %02.d' % i
            time_str18 = '2014-12-18 %02.d' % i
            tmp17 = df[time_str17]['behavior_type'].value_counts()
            tmp18 = df[time_str18]['behavior_type'].value_counts()
            for j in range(len(tmp17)):
                count_hour_1217[time_str17][tmp17.index[j] - 1] += tmp17[tmp17.index[j]]
            for j in range(len(tmp18)):
                count_hour_1218[time_str18][tmp18.index[j] - 1] += tmp18[tmp18.index[j]]
        batch += 1
        print('chunk %d done.'%batch)

    except StopIteration:
        print("finish data process")
        break

#storing the count result
df_1217 = pd.DataFrame.from_dict(count_hour_1217,orient='index')  #convert dict to dataframe
df_1218 = pd.DataFrame.from_dict(count_hour_1218,orient='index')
df_1217.to_csv(r'F:\tianchi\fresh_comp_offline\fresh_comp_offline\count_hour17.csv')  #store as csv file
df_1218.to_csv(r'F:\tianchi\fresh_comp_offline\fresh_comp_offline\count_hour18.csv')

df_1217 = pd.read_csv(r'F:\tianchi\fresh_comp_offline\fresh_comp_offline\count_hour17.csv',index_col = 0)
df_1218 = pd.read_csv(r'F:\tianchi\fresh_comp_offline\fresh_comp_offline\count_hour18.csv',index_col = 0)

# drawing figure
import matplotlib.pyplot as plt
df_1718 = pd.concat([df_1217,df_1218])

#f1 = plt.figure(1)
df_1718.plot(kind='bar')
plt.legend(loc='best')
plt.grid(True)
plt.show()

# f2 = plt.figure(2)
df_1218['3'].plot(kind='bar',color = 'r')
plt.legend(loc='best')
plt.grid(True)
plt.show()


#####################
#user behavior analysis
#####################
user_list = [10001082,
             10496835,
             107369933,
             108266048,
             10827687,
             108461135,
             110507614,
             110939584,
             111345634,
             111699844]
user_count = {}
for i in range(10):
    user_count[user_list[i]] = [0,0,0,0]   # key-value value = count of 4 types of behaviors

batch = 0 #for processing printing
for df in pd.read_csv(open(r"F:\tianchi\fresh_comp_offline\fresh_comp_offline\tianchi_fresh_comp_train_user.csv",'r'),
                      chunksize=100000,
                      index_col=['user_id']):
    try:
        for i in range(10):
            tmp = df[df.index == user_list[i]]['behavior_type'].value_counts()
            for j in range(len(tmp)):
                user_count[user_list[i]][tmp.index[j] -1] += tmp[tmp.index[j]]
        batch += 1
        print ('chunk %d done.' %batch)

    except StopIteration:
        print('Interation is stopped')
        break

#storing the count result
df_user_count = pd.DataFrame.from_dict(user_count,orient='index')
df_user_count.to_csv(r"F:\tianchi\fresh_comp_offline\fresh_comp_offline\user_count.csv")

#################################################
#item performance analysis (excel instead)
#################################################
end_time = timeit.default_timer()
print(('The code for file ' + os.path.split(__file__)[1] +
       ' ran for %.2fm' % ((end_time - start_time) / 60.)), file = sys.stderr)

print('data_preanalysis done!')