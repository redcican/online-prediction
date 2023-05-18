import streamlit as st
from preprocessing import *
from st_pages import Page, show_pages
from datetime import datetime

st.set_page_config(
    layout="wide",
)

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

show_pages(
    [
        Page("app.py", "主页", "🏠"),
        Page("1_support.py", "技术支持", "🙏"),
        Page("2_history.py", "历史数据", "📊"),
        Page("3_contact.py", "联系我们", "📞"),
    ]
)

state = st.session_state

if 'df' not in state:
    state.df = pd.DataFrame(columns=["患者姓名","患者年龄","性别","时间", "左腿", "右腿"])

h1("输入界面信息")

with st.container():
    with st.form("form"):
        col11, col22 = st.columns([1,1], gap="large")
        with col11:
            st.subheader("基本信息(必填)")
            name = st.text_input("患者姓名", value="张三")
            age = st.number_input("患者年龄",value=66)
            gender = st.radio("性别", ["男", "女"], horizontal=True)

        with col22:
            st.subheader("医院信息(可选)")
            doctor_name = st.text_input("医生姓名")
            patience_id = st.text_input("患者住院号")
            hosptial_name = st.text_input("医院名称")
            
        st.divider()
        col33, col44 = st.columns([1,1],gap="large")
        with col33:            
            with st.expander("左腿"):
                l_a = st.number_input('A常数', key="l_a")
                l_al = st.number_input('骨骼长度AL', help="mm" , key="l_al",value=26.34)
                l_k1 = st.number_input('骨骼曲率K1', help="D", key="l_k1",value=43.44)
                l_k2 = st.number_input('骨骼曲率K2', help="D", key="l_k2",value=44.1)
                l_lt = st.number_input('骨骼厚度LT', help="mm", key="l_lt",value=3.53)
                l_acd = st.number_input('骨骼深度ACD', help="mm", key="l_acd",value=4.1)
                l_check = st.checkbox("使用左腿数据?", key="l_check")
        with col44:            
            with st.expander("右腿"):
                r_a = st.number_input('A常数', key="r_a")
                r_al = st.number_input('骨骼长度AL', help="mm" , key="r_al",value=26.36)
                r_k1 = st.number_input('骨骼曲率K1', help="D", key="r_k1", value=43.41)
                r_k2 = st.number_input('骨骼曲率K2', help="D", key="r_k2", value=44.21)
                r_lt = st.number_input('骨骼厚度LT', help="mm", key="r_lt", value=3.49)
                r_acd = st.number_input('骨骼深度ACD', help="mm", key="r_acd", value=4.13)
                r_check = st.checkbox("使用右腿数据?", key="r_check")
                
        gender_convert = 1 if gender=="男" else 0        
            
        submitted  = st.form_submit_button("提交")
        

if submitted:

    if not l_check and not r_check:
        st.warning("请至少选择一条腿的数据")
    else:    
        with st.spinner("正在计算..."):
            
            if l_check and not r_check:
                input_df_l = {'Gender': gender_convert, 'Age': age, 'A1': l_al, 'A2': l_k1, 'A3': l_k2, 'A4': l_lt, 'A5': l_acd}
                l_output = show_result(l_check=l_check, r_check=r_check, input_df_l=input_df_l, input_df_r=None)
                state.df = state.df.append({"患者姓名":name,"患者年龄":age,"性别":gender,"时间": datetime.now() ,"左腿":l_output, "右腿":None}, ignore_index=True)
            elif r_check and not l_check:
                input_df_r= {'Gender':gender_convert, 'Age':age, 'A1':r_al, 'A2':r_k1, 'A3':r_k2, 'A4':r_lt, 'A5':r_acd}
                r_output = show_result(l_check=l_check, r_check=r_check, input_df_l=None, input_df_r=input_df_r)
                state.df = state.df.append({"患者姓名":name,"患者年龄":age,"性别":gender,"时间": datetime.now() ,"左腿":None, "右腿":r_output}, ignore_index=True)
            else:
                input_df_l = {'Gender': gender_convert, 'Age': age, 'A1': l_al, 'A2': l_k1, 'A3': l_k2, 'A4': l_lt, 'A5': l_acd}
                input_df_r= {'Gender':gender_convert, 'Age':age, 'A1':r_al, 'A2':r_k1, 'A3':r_k2, 'A4':r_lt, 'A5':r_acd}
                
                l_output, r_output = show_result(l_check=l_check, r_check=r_check, input_df_l=input_df_l, input_df_r=input_df_r)
                state.df = state.df.append({"患者姓名":name,"患者年龄":age,"性别":gender, "时间": datetime.now() ,"左腿":l_output, "右腿":r_output}, ignore_index=True)




