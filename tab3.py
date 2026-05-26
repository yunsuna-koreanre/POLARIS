# -*- coding: utf-8 -*-
import streamlit as st
import os
import streamlit as st
import pandas as pd
import sys
from streamlit.web import cli as stcli
import fun_dashboard
import numpy as np


# def show_download_dialog(excel_data):
#     st.write("Please input file name")    
#     # 사용자로부터 파일명 입력 받기 (확장자 제외하고 입력하도록 유도)
#     user_filename = st.text_input("File Name", value="polaris_report")    
#     # 빈 값 입력 방지 및 확장자(.xlsx) 붙이기
#     if not user_filename.strip():
#         final_filename = "polaris_report.xlsx"
#     else:
#         final_filename = f"{user_filename.strip()}.xlsx"
        
#     st.caption(f"ℹ️ File name: {final_filename}")

#     st.download_button(
#         label="📥 Download file",
#         data=excel_data,
#         file_name=final_filename,
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         type="primary",
#         use_container_width=True,
#         on_click=st.rerun # 다운로드 시작 시 팝업을 닫기 위해 리런시킵니다.
#     )
    
    
def render(move_tab_fn, result_yelt,aep_current,aep_all_current):
    st.header("3. EP Calculation")    
    
    
    if st.session_state.get("tab3_unlocked", True):    
        st.error("🚫  Please click 'Save' in the Assumption tab to proceed with the EP calculation")
    else:        

        df=result_yelt                    
        df['key']=df['ProgramID']+"_"+ df['TreatyID']
        conlst = df['key'].unique()
        
        df=df.set_index(df['key'])
        aep_projection = pd.DataFrame();         aep_all_projection = pd.DataFrame()
            
        aep_all_projection = fun_dashboard.EP_ALL(df, 'Target Loss', sum)
        
        for i in conlst:            
            aep_projection = pd.concat([aep_projection, fun_dashboard.EP_SEP(i, df.loc[i], 'Target Loss', sum)], axis=1)
        
        with st.container(border=True):    
            col1, col2, col3 = st.columns(3)
    
            with col1:
                st.markdown("Current PF AEP")          
                styled_df = (aep_all_current.style
                             .set_properties(**{'text-align': 'center !important', 'min-width': '80px'})
                                .format(lambda x: "{:,.0f}".format(x) if isinstance(x, (int, float)) else x)
                                .set_table_styles([
                                    {'selector': 'thead th', 'props': [('text-align', 'center'), ('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]},
                                    {'selector': 'th.row_heading', 'props': [('text-align', 'center')]},
                                    # {'selector': 'tbody tr:nth-child(1) td', 'props': [('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]},
                                    # {'selector': 'tbody tr:nth-child(1) th.row_heading', 'props': [('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]}
                                ]))                                    
                st.table(styled_df)            
                
            with col2:
                st.markdown("Target PF AEP")                        
                styled_df = (aep_all_projection.style
                             .set_properties(**{'text-align': 'center !important', 'min-width': '80px'})
                                .format(lambda x: "{:,.0f}".format(x) if isinstance(x, (int, float)) else x)
                                .set_table_styles([
                                    {'selector': 'thead th', 'props': [('text-align', 'center'), ('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]},
                                    {'selector': 'th.row_heading', 'props': [('text-align', 'center')]},
                                    # {'selector': 'tbody tr:nth-child(1) td', 'props': [('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]},
                                    # {'selector': 'tbody tr:nth-child(1) th.row_heading', 'props': [('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]}
                                ]))    
                st.table(styled_df)            
            with col3:
                st.markdown("Chagnes")            
                
                val1 = pd.to_numeric(aep_all_current.iloc[:, 0], errors='coerce')
                val2 = pd.to_numeric(aep_all_projection.iloc[:, 0], errors='coerce')
                
                change_ratio = np.where((val1 != 0) & val1.notna() & val2.notna(),      (val2 / val1) - 1,    np.nan    )                
                df_change = pd.DataFrame(change_ratio, index=aep_all_current.index, columns=["Change"])
                
                # 4. 스타일 지정 및 % 형식 포맷팅 (결측치 NaN은 빈 문자열로 표시)
                styled_df3 = (
                    df_change.style
                    .set_properties(**{'text-align': 'center !important', 'min-width': '80px'})
                    .format(lambda x: f"{x:+.1%}" if isinstance(x, (int, float)) and not np.isnan(x) else "") # +23.5% 또는 -5.1% 형식                          
                    .set_table_styles([  
                        {'selector': 'thead th', 'props': [('text-align', 'center'), ('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]},
                        {'selector': 'th.row_heading', 'props': [('text-align', 'center')]},
                        # {'selector': 'td', 'props': [('text-align', 'center'), ('min-width', '120px')]},                
                        # {'selector': 'tbody tr:nth-child(1) td', 'props': [('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]},      
                        # {'selector': 'tbody tr:nth-child(1) th.row_heading', 'props': [('font-weight', 'bold !important'), ('background-color', '#f2f2f2 !important')]}
                    ]))
                st.table(styled_df3)                    
     

        with st.container(border=True):              
            st.subheader("📊 Downlaod Result")                
            user_filename = st.text_input("Type file name:", value="reinsurance_report")
        
            # 파일명 뒤에 .xlsx 확장자가 없는 경우 자동으로 붙여주는 로직
            if not user_filename.endswith('.xlsx'):
                final_filename = f"{user_filename}.xlsx"
            else:
                final_filename = user_filename                
        
            try:    
                excel_data =fun_dashboard.create_excel_download(aep_all_current, aep_all_projection, aep_current, aep_projection)    
                
                if excel_data and len(excel_data) > 0:
                    import base64
                    b64 = base64.b64encode(excel_data).decode()
                    mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    href = f'''
                         <a href="data:{mime};base64,{b64}" download="{final_filename}"
                         style="
                             display: inline-block;
                             padding: 0.5em 1.2em;
                             background-color: #4CAF50;
                             color: white;
                             text-decoration: none;
                             border-radius: 6px;
                             font-weight: bold;
                             font-size: 16px;
                         ">
                         📥 Download File
                         </a>
                     '''
                    st.markdown(href, unsafe_allow_html=True)
                else:
                        st.error("⚠️ Failed to generate Excel data. Please check your data source.")
            except Exception as e:
                st.error(f"⚠️ Failed to generate Excel data: {e}")
                import traceback
                st.code(traceback.format_exc())
                
                
            # st.download_button(
            #     label="Download File",
            #     data=excel_data,
            #     file_name=final_filename, # 사용자가 입력한 이름이 적용됨
            #     mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")    

   
    col1, col2 = st.columns(2)   
    with col1:
        if st.button("⬅️ Move to Prev Tab", use_container_width=True, key="prev_tab3"):
            move_tab_fn("prev")
            st.rerun()
