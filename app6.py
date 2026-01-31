import streamlit as st
import pickle
from gensim.utils import simple_preprocess
import fitz
import joblib
import pandas as pd
from datetime import datetime
import email
from email import policy
from email.parser import BytesParser

# # Email Detection


Tf = pickle.load(open('tf_idf.pkl', 'rb'))
model = joblib.load('svc.pkl')


# prediction input text email
def detect_email(email_text):
    text_preprocess = ' '.join(simple_preprocess(email_text))
    #text transform
    transform_text = Tf.transform([text_preprocess]).toarray()
    #text prediction
    prediction_text = model.predict(transform_text)[0]
    result = 'SPAM' if prediction_text == 1 else 'NOT-SPAM'
    return result


# prediction file text email
def detect_uplode_email(email_text):
    file_type = email_text.type
    
    # pdf format
    if 'pdf' in file_type or email_text.name.endswith('.pdf'):
        email_data = fitz.open(stream=email_text.read(), filetype='pdf')
        email_content = ''
        for page in email_data:
            email_content += page.get_text()

    # email format
    elif 'eml' in file_type or email_text.name.endswith('.eml'):
        raw_bytes = email_text.read()
        msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
        plain_text = msg.get_body(preferencelist=('plain'))
        if plain_text:
            email_content = plain_text.get_content()
        else:
            email_content = str(msg.get_payload())

    else:
        email_content = email_text.read().decode('utf-8', error='ignore')

    #text preprocessing
    filetext_preprocess = ' '.join(simple_preprocess(email_content))
    #text transform
    transform_file_text = Tf.transform([filetext_preprocess]).toarray()
    #text prediction
    prediction_file_text = model.predict(transform_file_text)[0]
    result_file_text = 'SPAM' if prediction_file_text == 1 else 'NOT-SPAM'
    return result_file_text


#display prediction
def Display_input_text_result():
    if email_input:
            text = email_input if email_input else "Uploaded file content "
            text_result = detect_email(text)
            if text_result == 'NOT-SPAM':
                st.success(f"Detection: {text_result}")
            else:
                st.error(f"Detection: {text_result}")

            #Add to history
            if text_result:
                st.session_state.history.append({
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Detection": text_result,
                "Type": 'input text'
                 })
            else:
                st.error("Please provide email content.")


# input text reset function
def reset_text():
    st.session_state['email'] = ''


# Initialize session state for history and email
if "history" not in st.session_state:
    st.session_state.history = []

if 'email' not in st.session_state:
    st.session_state['email'] = ''

# Header
st.title("Email Detection Dashboard")
st.markdown("Analyze emails for spam. ")

# Sidebar
st.sidebar.header("Quick Actions")
if st.sidebar.button("New Analysis"):
    st.rerun()

#Slider filter
st.sidebar.header("Filters")
detection_type = st.sidebar.selectbox("Detection Type", ["All", "Spam"])


# Main Content with Tabs
tab1, tab2 = st.tabs(["Analyze", "History"])

# Analyze tab
with tab1:
    st.header("Email Analysis")
    # input data process
    email_input = st.text_area("Paste email content here ", height=200, key='email')
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Detect", use_container_width=True):
            Display_input_text_result()
    with col2:
        if st.button('Reset', on_click=reset_text, use_container_width=True):
            pass
    

    # upload file data process
    uploaded_file = st.file_uploader("Upload .eml or pdf file", type=["eml", 'pdf'])      

    if uploaded_file is not None:
        # Display results
        file_result = detect_uplode_email(uploaded_file)
        if file_result == 'NOT-SPAM':
            st.success(f"Detection: {file_result}")
        else:
            st.error(f"Detection: {file_result}")
        
        # Add to history
        if file_result:
            st.session_state.history.append({
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Detection": file_result,
                "Type": 'file text'
            })
        else:
            st.error("Please provide email content.")


# History tab
with tab2:
    st.header("Analysis History")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df)
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.write("No history yet.")

