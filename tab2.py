# -*- coding: utf-8 -*-
import streamlit as st
import fun_dashboard
import pandas as pd

def render(move_tab_fn, df_yelt, contract_file, currency_file):
    st.header("2. Assupmtion")
    
    
    df_contract = fun_dashboard.load_data(contract_file)
    df_currency = fun_dashboard.load_data(currency_file)
    
    summary_df = df_yelt[['ProgramID', 'TreatyID']].drop_duplicates().reset_index(drop=True)

    summary_df = pd.merge(summary_df, df_contract[['ProgramID', 'TreatyID', 'ReinsuranceTypeCode','CurrencyCode','ParticipationNet']], 
                          on=['ProgramID', 'TreatyID'], how='left')
    
    summary_df = pd.merge(summary_df, df_currency[['CurrencyCode', 'FX Rate(%)']], on=['CurrencyCode'], how='left')
    summary_df['FX Rate(%)'] = summary_df['FX Rate(%)'].fillna(0)
    
    summary_df.rename(columns={'ParticipationNet': 'Current Net Share(%)','CurrencyCode':'Currency','ReinsuranceTypeCode':'Reinsurance Type'}, inplace=True)
   
    
    if 'editor_df' not in st.session_state:
        summary_df['Target Net Share(%)'] = summary_df['Current Net Share(%)']        
        summary_df['Growth Rate(%)'] = 0.0
        summary_df['Inflation Rate(%)'] = 0.0
        summary_df = summary_df[['ProgramID', 'TreatyID', 'Reinsurance Type','Current Net Share(%)', 'Target Net Share(%)', 'Currency','FX Rate(%)','Growth Rate(%)','Inflation Rate(%)']]
        st.session_state.editor_df = summary_df
    
     
    st.subheader("📝 Portfolio Parameter Setting")
    st.info("Please manually edit the values for 'Target Net Share', 'FX Rate', 'Growth Rate', and 'Inflation Rate' in the table below.")
    
    styled_df = (st.session_state.editor_df.style.apply(fun_dashboard.highlight_columns, axis=None))
    
    edited_df = st.data_editor(
        # st.session_state.editor_df,
        styled_df,  key="my_editor_key",
        column_config={
            "ProgramID": st.column_config.Column("Contract", disabled=True),
            "TreatyID": st.column_config.Column("Layer",disabled=True),            
            "Reinsurance Type": st.column_config.Column(disabled=True),            
            "Currency": st.column_config.Column(disabled=True),            
            "Current Net Share(%)": st.column_config.NumberColumn(format="%.4f", disabled=True),
            "Target Net Share(%)": st.column_config.NumberColumn(format="%.4f"),            
            "FX Rate(%)": st.column_config.NumberColumn(format="%.2f"),
            "Growth Rate(%)": st.column_config.NumberColumn(format="%.2f"),
            "Inflation Rate(%)": st.column_config.NumberColumn(format="%.2f"),
        },
        hide_index=True,
        width='stretch'
    )
    with st.container(border=True):        
        st.markdown("Bulk Settings")    
        
        col1, col2 = st.columns(2)
        
        with col1:
            bulk_growth = st.number_input("Set all Growth Rate(%)", value=0.0, step=0.1)
        with col2:
            bulk_inflation = st.number_input("Set all Inflation Rate(%)", value=0.0, step=0.1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🪄 Apply to All", use_container_width=True,type="secondary"):
                if "my_editor_key" in st.session_state:
                    current_df = st.session_state.editor_df.copy()
                    changes = st.session_state["my_editor_key"].get("edited_rows", {})
                    for row_idx, edits in changes.items():
                        for col_name, new_val in edits.items():
                            current_df.at[row_idx, col_name] = new_val
                    st.session_state.editor_df = current_df        # 3) 현재 화면 상태(수정 반영)를 원본(session_state)으로 업데이트
                    
                st.session_state.editor_df['Growth Rate(%)'] = bulk_growth
                st.session_state.editor_df['Inflation Rate(%)'] = bulk_inflation                
                st.session_state["bulk_apply_success"] = True                   
                st.rerun()
                
        if st.session_state.get("bulk_apply_success", False):
            st.warning("✅ Successfully applied to all rows!")        
            st.session_state["bulk_apply_success"] = False
                
                    

    result_yelt = pd.merge(df_yelt, edited_df, on=['ProgramID', 'TreatyID'], how='left')
 
    result_yelt['Target Loss'] = ((result_yelt['Current Loss'] / result_yelt['Current Net Share(%)'])*result_yelt['Target Net Share(%)'] 
                              *(1+result_yelt['FX Rate(%)']/100) *(1+result_yelt['Growth Rate(%)']/100)*(1+result_yelt['Inflation Rate(%)']/100))    
    
            
    if st.button("💾 Save Assumptions", type="primary", key="unlock_tab3_btn"):                       
        st.session_state["tab3_unlocked"] = True        
        st.rerun()
        
    if st.session_state.get("tab3_unlocked", False):    
        st.warning("✅ You can now proceed to the next tab.")    
        
        col1, col2 = st.columns(2)       
        with col1:
            if st.button("⬅️ Move to Prev Tab", use_container_width=True, key="prev_tab2"):
                move_tab_fn("prev")
                st.rerun()
        with col2:
            if st.button("Move to Next Tab ➡️", use_container_width=True, key="next_tab2"):
                move_tab_fn("next")
                st.rerun()
        st.rerun()
     
  
            
    return result_yelt