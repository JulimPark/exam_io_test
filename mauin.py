import streamlit as st
import fitz
from google.cloud import storage
from google.oauth2 import service_account
import os
from supabase import create_client
import pandas as pd
from fnmatch import fnmatch
import unicodedata
from io import BytesIO
import json

bucket_name = 'free_online_math'
st.session_state.signin = 'BB'

## 온라인 게시용
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
    if st.session_state.signin == 'AA':
        exam_num = st.select_slider('시험지당 :red[문항수]를 선택하세요',options=[i+1 for i in range(30)],value=5)
    elif st.session_state.signin == 'BB':
        exam_num = st.select_slider('시험지당 :red[문항수]를 선택하세요',options=[i+1 for i in range(50)],value=5)
    else:
        exam_num = st.select_slider('시험지당 :red[문항수]를 선택하세요',options=[i+1 for i in range(10)],value=5)
        
        
if st.session_state.signin == 'AA':
    with st.expander('기타 옵션(학생용 서비스)'):
        numbering = st.checkbox('시험지에 문항 번호를 추가합니다.',value=True)
        shuffle = st.checkbox('문항 배열의 순서를 섞습니다.')
        register = st.checkbox('응시 시험에 등록합니다.(채점 서비스)')
        difference_set = st.checkbox('풀어본 문제는 제외합니다.')
        incorrect_set = st.checkbox('오답문항으로 시험지를 만듭니다.')
        analysis = st.checkbox('응시 결과를 누적 관리합니다.(인공지능 분석 서비스)')
        watermark = st.checkbox('pdf에 워터마크를 제거합니다.',value=False,disabled=True)
        test_num = st.select_slider('만들 :red[시험지 수]를 선택하세요',options=[i+1 for i in range(5)],value=3)
        
elif st.session_state.signin == 'BB':
    with st.expander('기타 옵션(유료 학원/강사 서비스)'):
        numbering = st.checkbox('시험지에 문항 번호를 추가합니다.',value=True)
        shuffle = st.checkbox('문항 배열의 순서를 섞습니다.')
        register = st.checkbox('응시 시험에 등록합니다.(채점 서비스)')
        difference_set = st.checkbox('풀어본 문제는 제외합니다.')
        incorrect_set = st.checkbox('오답문항으로 시험지를 만듭니다.')
        analysis = st.checkbox('응시 결과를 누적 관리합니다.(인공지능 분석 서비스)')
        watermark = st.checkbox('pdf에 워터마크를 제거합니다.',value=False,disabled=True)
        student_set = st.multiselect('관리하는 학생에게 시험을 배정합니다.',options=['홍길동','홍길미','홍길자','홍길판','홍길돈','홍길홍','홍홍길','홍홍홍'])
        text_field1 = st.checkbox('글자상자1을 입력합니다.')
        if text_field1:
            text_field1_1 = st.text_input('입력할 문구를 기록하세요.')
            rad1 = st.radio('글자상자의 위치를 선택하세요',options=['왼쪽상단','중앙상단','오른쪽상단','왼쪽하단','중앙하단','오른쪽하단'],horizontal=True)
        
        text_field2 = st.checkbox('글자상자2를 입력합니다.')
        if text_field2:
            text_field2 = st.text_input('입력할 문구를 기록하세요.')
            rad2 = st.radio('글자상자의 위치를 선택하세요',options=['왼쪽상단','중앙상단','오른쪽상단','왼쪽하단','중앙하단','오른쪽하단'],horizontal=True)
        test_num = st.select_slider('만들 :red[시험지 수]를 선택하세요',options=[i+1 for i in range(20)],value=3)

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



def call_files_from_storage(choice_pdf_list):
    data = []
    for i in choice_pdf_list:
        data.append(download_memory(bucket_name, i))
    return data

def merge_data(data):
    doc_all = fitz.open()
    for datum in data:
        if len(doc_all) <= exam_num:
            doc = fitz.open(stream=datum,filetype='pdf')
            doc_all.insert_pdf(doc,from_page=0,to_page=len(doc))
            doc.close()
            out = BytesIO()
            doc_all.save(out,deflate=True, garbage=4)
        else:
            pass
    col1, col2, col3 = st.columns(3)
    with col2:
        st.download_button(label=':green[시험지 다운로드]',data=out,file_name='today_exam.pdf',mime='application/pdf',use_container_width=True)       
    doc_all.close()

col1, col2, col3 = st.columns(3)
with col2:
    make_exam = st.button(':orange[시험지 만들기]', use_container_width=True)
if make_exam:
    if len(choice_pdf_list)>0:
        data = call_files_from_storage(choice_pdf_list)
        merge_data(data)
    else:
        st.error('해당 선택에 대한 문항이 없습니다. 옵션을 조절하세요.')
    

