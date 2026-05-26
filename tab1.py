# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import fun_dashboard

def render(move_tab_fn, yelt_file, contract_file, currency_file):
    
    st.header("1. Data Check")        
    df_yelt = fun_dashboard.load_data(yelt_file)    
    df_yelt.rename(columns={'ntloss': 'Current Loss'}, inplace=True)    
     
    df=df_yelt
    df['key']=df['ProgramID']+"_"+ df['TreatyID']
    conlst = df['key'].unique()
    
    df=df.set_index(df['key'])
    aep_current = pd.DataFrame(); aep_all_current = pd.DataFrame(); 
    aep_all_current = fun_dashboard.EP_ALL(df, 'Current Loss', sum)
    
    for i in conlst:
        aep_current= pd.concat([aep_current,fun_dashboard.EP_SEP(i, df.loc[i], 'Current Loss', sum)], axis=1)
        

    with st.container(border=True):        
        st.subheader("Current PF AEP")          
        col1, col2 = st.columns(2)
        with col1:
            styled_df = (aep_all_current.style
                         .set_properties(**{'text-align': 'center !important', 'min-width': '80px'})
                            .format(lambda x: "{:,.0f}".format(x) if isinstance(x, (int, float)) else x)
                            .set_table_styles([
                                {'selector': 'thead th', 'props': [('text-align', 'center !important'),('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]},
                                {'selector': 'th.row_heading', 'props': [('text-align', 'center !important')]},
                                # {'selector': 'tbody tr:nth-child(1) td', 'props': [('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]},
                                # {'selector': 'tbody tr:nth-child(1) th.row_heading', 'props': [('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]}
                            ]))                                    
            st.table(styled_df)  
            
    with st.container(border=True):
        st.subheader("Current AEP by Contract")          
        styled_df = (aep_current.T.style
                     .set_properties(**{'text-align': 'center !important', 'min-width': '80px'})
                     # .hide(axis="index") 
                        .format(lambda x: "{:,.0f}".format(x) if isinstance(x, (int, float)) else x)
                        .set_table_styles([
                                         { 'selector': 'thead th', 'props': [('font-weight', 'bold !important'),  ('background-color', '#f2f2f2 !important'), # 원하는 음영 색상 (예: 연한 회색)
                                           ('text-align', 'center !important'),('color', '#333333 !important')  ] },           
                                         { 'selector': 'td', 'props': [('text-align', 'center !important')] } ]))                                           
        st.table(styled_df)  
        # st.sidebar.json(st.session_state)
        
    st.write("---")
    col1, col2 = st.columns(2)
    with col2:
        if st.button("Move to Next Tab ➡️", use_container_width=True, key="next_tab1"):
            move_tab_fn("next")
            st.rerun()
            
    return df_yelt, aep_current,aep_all_current