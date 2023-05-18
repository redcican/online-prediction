import numpy as np
from sklearn.preprocessing import PolynomialFeatures, MinMaxScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
import pandas as pd
import streamlit as st
from pycaret.regression import load_model, predict_model


def IQR_Outliers (X, features):    
    out_indexlist = []
        
    for col in features:
       
        # Using nanpercentile instead of percentile because of nan values
        Q1 = np.nanpercentile(X[col], 25.)
        Q3 = np.nanpercentile(X[col], 75.)
        
        cut_off = (Q3 - Q1) * 2.5 # parameter 2.5 is to remove the most extreme outliers.
        upper, lower = Q3 + cut_off, Q1 - cut_off
                
        outliers_index = X[col][(X[col] < lower) | (X[col] > upper)].index.tolist()        
        out_indexlist.extend(outliers_index)
        
    # Using set to remove duplicates
    out_indexlist = list(set(out_indexlist))
    out_indexlist.sort()

    
    return out_indexlist


def preprocessing(df_train, df_test, target_name, drop_col, non_numeric_features, outlier_rem_func, deg_poly,
                  oversampling=False, oversampling_name=None, oversampling_range=None,
                  add_reciprocal_features=False, features_for_reciprocal=None):
    
    # Drop certain columns
    if drop_col:
        df_train = df_train.drop(drop_col, axis=1)
        df_test = df_test.drop(drop_col, axis=1)
        
    # Oversampling    
    if oversampling:
        # Split the minnority for oversampling 
        df_train["class"] = 0
        ind_oversampling = np.where(np.logical_and(df_train[oversampling_name]>oversampling_range[0], 
                                                   df_train[oversampling_name]<oversampling_range[1]))
        num_samples = ind_oversampling[0].shape[0]
                                                
        df_train["class"].iloc[ind_oversampling] = 1
            
        # Oversampling with SMOTE

        oversamp_data, oversamp_class = df_train.drop("class", axis=1), df_train["class"]

        oversamp_class = LabelEncoder().fit_transform(oversamp_class)

        print(ind_oversampling[0].shape)
        
        samp_strategy = {1: int(num_samples*1.5)} # Increase the minority by a factor 1.5
        oversampler = SMOTE(sampling_strategy=samp_strategy)

        oversamp_data, oversamp_class = oversampler.fit_resample(oversamp_data, oversamp_class)

        df_train = oversamp_data.copy()
        
    # Add reciprocal features:
    if add_reciprocal_features:
        for feature in features_for_reciprocal:
            df_train["1/{}".format(feature)] = 1.0 / df_train[feature].values
            df_test["1/{}".format(feature)] = 1.0 / df_test[feature].values
            
    # Extract the target
    y = df_train[target_name]
    
    # Remove outliers on training set for numerical features as well as target
    col_numeric_features_plus_target = list(df_train.columns)
    if non_numeric_features:
        for feature in non_numeric_features:
            col_numeric_features_plus_target.remove(feature)
    
    if outlier_rem_func:
    
        outlier_index = outlier_rem_func(df_train, col_numeric_features_plus_target)

        df_train = df_train.drop(index=outlier_index)
        y = y.drop(index=outlier_index)
        
    # Columns for numerical features for further polynomial transformation
    col_numeric_features_plus_target.remove("Target")
    col_numeric = col_numeric_features_plus_target.copy()

    df_numeric_train = df_train[col_numeric]
    df_numeric_test = df_test[col_numeric]
    
    # Polynomial transformation and append back to original dataframe
    
    p = PolynomialFeatures(degree=deg_poly, interaction_only=False).fit(df_numeric_train)
    
    df_train_X_withpoly = pd.DataFrame(p.transform(df_numeric_train), columns=p.get_feature_names_out(df_numeric_train.columns))
    df_test_X_withpoly = pd.DataFrame(p.transform(df_numeric_test), columns=p.get_feature_names_out(df_numeric_test.columns))
    
    if non_numeric_features:
        
        df_train_X_withpoly[non_numeric_features] = df_train[non_numeric_features].values
        df_test_X_withpoly[non_numeric_features] = df_test[non_numeric_features].values
    
    # Normalization on the polynomially transformed features

    n = MinMaxScaler().fit(df_train_X_withpoly)
    
    df_out_train = pd.DataFrame(n.transform(df_train_X_withpoly), columns=df_train_X_withpoly.columns)
    df_out_test = pd.DataFrame(n.transform(df_test_X_withpoly), columns=df_test_X_withpoly.columns)
    
    df_out_train[target_name] = y.values 
    
    return df_out_train, df_out_test


model = load_model("model_huber_withAgeA5_poly5noAge_v2")
df_train_original  = pd.read_excel("train.xlsx")
df_train_original.columns = ["Id","Gender","Age","A1","A2","A3","A4","A5","Target"]
df_train_original["Gender"] = df_train_original["Gender"].map({"男":1.0,"女":0.0})
df_train_original = df_train_original.drop("Id", axis=1)



def predict(model, input_df):
    predictions_df = predict_model(model, input_df)
    predictions = predictions_df["prediction_label"][0]
    return predictions

def h1(info:str):
    return st.markdown(f"<h1 style='text-align: center; color: red;'>{info}</h1>", unsafe_allow_html=True)

def show_result(l_check=False, r_check=False, input_df_l=None, input_df_r=None):
    if l_check and not r_check:
        output = construct_pred(input_df_l)
        h1(f"左腿预测结果: {output}")
        return output
    if r_check and not l_check:
        output = construct_pred(input_df_r)
        h1(f"右腿预测结果: {output}")
        return output
    if l_check and r_check:
        output_l = construct_pred(input_df_l)
        output_r = construct_pred(input_df_r)
        col1, col2 = st.columns([1,1], gap="large")
        with col1:
            h1(f"左腿预测结果: {output_l}")
        with col2:
            h1(f"右腿预测结果: {output_r}")   
            
        return output_l, output_r     
            
def construct_pred(input_df):
    df_pred = pd.DataFrame([input_df])
    _, df_test = preprocessing(df_train_original, df_pred, target_name=["Target"],
                            drop_col=None, non_numeric_features=["Gender", "Age"],
                        outlier_rem_func=IQR_Outliers, deg_poly=5)
    output = predict(model=model, input_df=df_test)
    output = round(output, 2)
    return output
