import streamlit as st
import requests
import PyPDF2
import docx2txt
from io import BytesIO
import os
from dotenv import load_dotenv
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

load_dotenv()

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page].extract_text()
    return text

def read_docx(file):
    return docx2txt.process(file)

def read_text_file(file):
    return file.read()

def summarize_text(text):
    # System message containing instructions
    system_string = "you are a helpful assistant. you help summarize text. The summarization must be categorize into sections according to their topics. The summarization must be in bullet point -- it cannot be one single plain paragraph! Don't put a title -- only the bullet points! The summarization shall be in Chinese; of length 1/4 of the original article. try to keep all the numbers; they are very important! do not simply shorten each sentence. try to understand the entire paragraph and provide a coherent summary."

    # User message with input text from the form
    user_string = f"please help me summarize the below text. The summarization must be categorize into sections according to their topics. The summarization must be in bullet point -- it cannot be one single plain paragraph! Don't put a title -- only the bullet points! The summarization shall be in Chinese; of length 1/4 of the original article. try to keep all the numbers; they are very important! do not simply shorten each sentence. try to understand the entire paragraph and provide a coherent summary. \
        {text}"

    # API request data
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_string},
            {"role": "user", "content": user_string},
        ]
    }

    # API endpoint URL
    url = 'https://api.openai.com/v1/chat/completions'

    API_KEY = os.getenv("OPENAI_API_KEY")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    }

    # Make API request
    response = requests.post(url, json=data, headers=headers)

    # Get response text from API response
    response_text = response.json()['choices'][0]['message']['content']

    return response_text

# Streamlit app
def app():
    user_name = os.getenv("USER_NAME")
    password = os.getenv("PASSWORD")
    # verification_code = st.text_area("请在这里输入您的邀请验证码：", height=40)
        
    # if st.button("Verify"):
    #     if verification_code == VERI_CODE:

    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    config['credentials']['usernames']['CICC-Software']['name'] = user_name
    config['credentials']['usernames']['CICC-Software']['password'] = password

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status:
        authenticator.logout('Logout', 'main')
        
        st.title("中金计算机 - 纪要/文章速读整理器")
        st.write(":exclamation: 本工具仅为一个演示用品，目的为展示人工智能技术的部分功能，非日常工作所必需。请用户合法、依规使用，不要上传敏感信息；中金计算机不承担相关法律责任。    \n :exclamation: 仅供测试体验，谢绝商用。我们团队个人付费，资源可能随时被耗尽。    \n :exclamation: 此功能意在为大家提供一个便利的小工具，可能有bug，还请多多谅解。")

        # File uploader
        uploaded_file = st.file_uploader("Upload a PDF or Word document", type=["pdf", "docx", "txt"])

        # Input form
        if uploaded_file is not None:
            file_type = uploaded_file.type
            if file_type == "application/pdf":
                text = read_pdf(uploaded_file)
            elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text = read_docx(uploaded_file)
            elif file_type == "text/plain":
                text = read_text_file(uploaded_file)
            else:
                st.error("Unsupported file type")
                return
            st.text_area("Enter your text here", value=text, height=200)
        else:
            text = st.text_area("Enter your text here", height=200)

        # Submit button
        if st.button("Summarize"):
            all_summary = ''
            cnt = 1
            while len(text):
                with st.spinner(f"Summarizing...part {cnt}"):
                    print('cur text len is', len(text))

                    max_len = min(2000, len(text))
                    cur_text = text[:max_len]
                    text = text[max_len:]

                    summary = summarize_text(cur_text)
                    all_summary += summary

                    cnt += 1

            # Display output
            st.markdown(all_summary, unsafe_allow_html=True)

    elif authentication_status == False:
        st.error('用户名或密码不正确')
    elif authentication_status == None:
        st.warning('请输入您的用户名和密码（同为您收到的邀请码）')

    # else:
    #     st.write("您的验证码不正确；请您刷新应用，并输入正确的验证码。")

if __name__ == "__main__":
    app()
