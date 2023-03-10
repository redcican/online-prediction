import streamlit as st
import pandas as pd
from autosklearn.regression import AutoSklearnRegressor
import base64
import json
import pickle
import uuid
import re
from io import BytesIO
import numpy as np

def to_excel(df:pd.DataFrame):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def download_button(object_to_download, download_filename, button_text, file_extension,pickle_it=False):
    """
    Generates a link to download the given object_to_download.

    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.

    Returns:
    -------
    (str): the anchor tag to download object_to_download

    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')

    """
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            if file_extension == ".csv":
                object_to_download = object_to_download.to_csv(index=False)
            else:
                object_to_download = to_excel(object_to_download)
        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: .5rem .75rem;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """
        
    dl_link = custom_css + f'<a download="{download_filename+file_extension}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'
    #dl_link = custom_css + f'<a download="{download_filename+file_extension}" id="{button_id}" data:application/octet-stream;base64,{b64}">{button_text}</a><br></br>'

    return dl_link


file_upload = st.file_uploader("Upload a csv file", type="csv")
if file_upload is not None:
    data = pd.read_csv(file_upload)
    column = data["S11"].iloc[1:].values
    with open("automl.pkl", "rb") as f:
        model = pickle.load(f)
    pred_clip = model.predict([column])
    pred_clip = np.clip(pred_clip, [0.2,0.4,3.9,0.2,13.9,13.8,13.2],[1.01,1.21,4.71,0.8,14.701,14.201,14.001])
    predictions = pd.DataFrame(pred_clip.tolist(), columns = ["w1","w2","w3","s1","l1","l2","l3"])
    
    is_download = st.checkbox("Download predictions", value=False)
    if is_download:
        href = download_button(predictions, "predictions", "Download", ".csv")
        st.markdown(href, unsafe_allow_html=True)
        


        
    