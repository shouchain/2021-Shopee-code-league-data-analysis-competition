#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')
df = pd.read_json("contacts.json",encoding="utf-8", orient='records')

featuretouse = ['Email','Phone','OrderId']

def match_the_feature(df, x):
    part = df[['Id',x]]
    part[x] = part[x].replace('', np.nan) # 從json讀取的檔案當中，缺失值會是空字串的形式，所以先轉成nan
    part.dropna(axis = 0, subset = [x], inplace = True)
    part.reset_index(inplace = True, drop = True)

    id_dict = {k: list(v) for k, v in part.groupby(x)['Id']}
    
    part_df = pd.DataFrame()
    part_df[x] = id_dict.keys()
    part_df['{}_related_id'.format(x).lower()] = id_dict.values()
    
    df = pd.merge(df, part_df, how = 'left', on = x)
    return df

# Match the Email, Phone, OrderId
for i in featuretouse:
    df = match_the_feature(df, i)
    
# COMBINE & TRANSFER

df['phone_related_id'] = df['phone_related_id'].fillna("").apply(list)
df['email_related_id'] = df['email_related_id'].fillna("").apply(list)
df['orderid_related_id'] = df['orderid_related_id'].fillna("").apply(list)

df['total_related_id'] = df['phone_related_id'] + df['email_related_id'] + df['orderid_related_id']
df['total_related_id'] = df['total_related_id'].apply(lambda x: list(set(x)))

## COMPARE THE EACH ID RESULT
def sum_the_id(x):
    tt = []
    for i in x:
        tt += df['total_related_id'][i]
    tt = list(set(tt))
    return tt

# to match the whole ID for 3 times
for _ in range(3):
    df['total_related_id'] = df['total_related_id'].apply(lambda x: sum_the_id(x))
    
df['total_related_id'].apply(lambda x: x.sort())


## DICT OF THE CONTACTS
contacts = df['Contacts'].to_dict()

def contacts_sum(x):
    a=0
    for i in x:
        a += contacts[i]
        
    return a
# Count_the_contacts
df['Contact_total'] = df['total_related_id'].apply(lambda x: contacts_sum(x))


#transfer to the submission format
df['total_related_id_2'] = df['total_related_id'].apply(lambda x: '-'.join(str(i) for i in x))
df['Contact_total'] = df['Contact_total'].apply(lambda x: str(x))
df['final_answer'] = df['total_related_id_2'] + ', ' + df['Contact_total']

#SUBMISSION

submission = pd.DataFrame()
submission['ticket_id'] = df['Id']
submission['ticket_trace/contact'] = df['final_answer']
# submission.to_csv('Submission.csv', index = False)

