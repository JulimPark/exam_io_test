import streamlit as st
import fitz
from google.cloud import storage
import os
from supabase import create_client
import pandas as pd
from fnmatch import fnmatch
import unicodedata
from io import BytesIO
import json
from google.oauth2 import service_account


# db = firestore.Client(credentials=creds, project="test-project-6e03a")



bucket_name = 'free_online_math'


@st.cache_resource
def google_storage():
    key_dict = json.loads(st.secrets["textkey"])
    creds = service_account.Credentials.from_service_account_info(key_dict)
    storage_client = storage.Client(credentials=creds)
    return storage_client
storage_client = google_storage()





def list_blobs(bucket_name):
    file_name_list = []
    blobs = storage_client.list_blobs(bucket_name)

    for blob in blobs:
        file_name_list.append(blob.name)
    return file_name_list

file_list = list_blobs(bucket_name)
for i in file_list:
    i = unicodedata.normalize('NFC',i)
    
@st.cache_data
def download_memory(bucket_name,blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()
    return contents

def download_blob(bucket_name, source_blob_name, destination_file_name):
    
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    return destination_file_name

# def input_slicing(user_input):
#     if fnmatch(user_input, '*,*'):
#         user_input = user_input.replace(' ','')
#         result = user_input.split(',')
#     elif fnmatch(user_input, '* *'):
#         result = user_input.split(' ')
#     else:
#         result = user_input
#     return result

def extractor(file_list):
    subject = []
    year = []
    theme = []
    score = []
    for i in file_list:
        aa = i.split('_')
        try:
            subject.append(aa[0])
        except:
            pass
        try:
            year.append(aa[1])
        except:
            pass
        try:
            theme.append(aa[2])
        except:
            pass
        try:
            score.append(aa[3])
        except:
            pass
        subject = sorted(set(subject))
        year = sorted(set(year))
        theme = sorted(set(theme))
        score = sorted(set(score))
        
    return subject, year, theme, score
subject, year, theme, score = extractor(file_list)




with st.expander('컨텐츠 선택'):
    user_subject = st.multiselect(':red[과목]을 선택하세요',options=subject)
    st.write('')
    period1,period2 = st.select_slider(label=':red[기간]을 선택하세요', options= year,value=(min(year),max(year)))
    st.write('')
    year2 = []
    
    for i in year:
        if i >= period1 and i<=period2:
            year2.append(i)
            
    user_input = st.multiselect(':red[단원]을 선택하세요',options=theme)
    st.write('')
    st.write(':red[난이도]를 선택하세요')
    col = st.columns(4)
    with col[0]:
        level1 = st.checkbox(label='하(2점)')
    with col[1]:  
        level2 = st.checkbox(label='중(3점)')
    with col[2]:
        level3 = st.checkbox(label='상(4점)')
    with col[3]:
        level4 = st.checkbox(label='킬러')
    
    user_score = []
    if level1:
        user_score.append(unicodedata.normalize('NFC','2점'))
    if level2:
        user_score.append(unicodedata.normalize('NFC','3점'))
    if level3:
        user_score.append(unicodedata.normalize('NFC','4점'))
    if level4:
        user_score.append(unicodedata.normalize('NFC','킬러'))
    

choice_filename_list = []
for i in user_subject:
    for j in year2:
        for k in user_input:
            for s in user_score:
                if s!='킬러':
                    file_name = f"{i}_{j}_{k}_{s}"
                else:
                    file_name = f"{i}_{j}_{s}"
                choice_filename_list.append(file_name)


choice_pdf_list = []
for i in file_list:
    for j in choice_filename_list:
        if fnmatch(i, f"{j}*") and fnmatch(i, '*.pdf'):
            choice_pdf_list.append(i)
        else:
            pass
choice_pdf_list


# contents = download_blob(bucket_name,choice_pdf_list[4],choice_pdf_list[4])
# doc = fitz.open(contents)
# st.write(len(doc))
data = []
for i in choice_pdf_list:
    data.append(download_memory(bucket_name, i))

data


doc_all = fitz.open()
def merge_data(data):
    pdf = fitz.open(stream=data,filetype='pdf')
    doc_all.insert_pdf(pdf,from_page=0,to_page=0)
    out = BytesIO()
    doc_all.save(out)
    
    # doc_all.save('ababab.pdf')
    # doc_all.save('test.pdf',deflate=True, garbage=4)
    # doc = fitz.open('pdf',data)
    # doc_all.insert_pdf(doc,from_page=0,to_page=0)
    # doc_all.save(stream='BytesIO',filename='cdcd.pdf')
    st.download_button(label='down',data=out,file_name='abab.pdf',mime='application/pdf')       
    
    
merge_data(data[0])

