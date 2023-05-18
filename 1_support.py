import streamlit as st 
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText



def send_email(file_path, filename):

    # set up the SMTP server
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # For starttls
    username = st.secrets["username"]
    password = st.secrets["password"]

    # create a multipart message
    msg = MIMEMultipart()

    # setup the parameters of the message
    msg['From'] = 'tech support'
    msg['To'] = "cican17@gmail.com"  # 18703812923@163.com
    msg['Subject'] = "有用户提交了文件"

    # add in the message body
    msg.attach(MIMEText('Body of the email', 'plain'))
    try:
    # open the file in bynary
        with open(file_path, "rb") as binary_file:
            part = MIMEBase('application', 'octet-stream')
            # To change the payload into encoded form
            part.set_payload(binary_file.read())
            encoders.encode_base64(part)

            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        # add attachment to message
        msg.attach(part)
    except FileNotFoundError:
        st.write("无法添加附件")
    try:
        # log in to the server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)

        # send the message
        server.send_message(msg)

        # close the server
        server.quit()
        os.remove(file_path)
    except Exception as e:
        st.write(f"Error occurred while deleting file: {str(e)}")


def save_uploadfile(uploaded_file):
    if not os.path.exists("tempDir"):
        os.mkdir("tempDir")
    with open(os.path.join("tempDir",uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return st.success("保存成功: {}".format(uploaded_file.name))

st.title("技术支持")
st.write("在线计算公式由xxx技术组维护。")

with st.form("form2", clear_on_submit=True):
    credential = st.text_input("输入口令")
    file = st.file_uploader("上传文件", type=["csv", "xlsx"])
    number_of_files = st.number_input("确认文件数据条目", value=1, min_value=1)
    
    submitted = st.form_submit_button("提交")
    
    if file is not None and submitted:
        save_uploadfile(file)
        send_email(os.path.join("tempDir",file.name), file.name)
        st.success("AI模型正在更新，请稍等")