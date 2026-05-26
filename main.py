# -*- coding: utf-8 -*-
"""
Created on Thu May 21 16:26:10 2026

@author: yunsu.na
"""
import sys
from streamlit.web import cli as stcli
import streamlit as st

import tab1
import tab2
import tab3
import fun_dashboard

try:
    from IPython import get_ipython
    get_ipython().magic('reset -sf')
except:
    pass

# import os
# import streamlit as st
# import pandas as pd
# import sys
# from streamlit.web import cli as stcli
# import fun_dashboard
# import numpy as np


# ── 세션 상태 초기화 ──────────────────────────────────────
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "1. Data Check"

if "tab3_unlocked" not in st.session_state:
    st.session_state["tab3_unlocked"] = False



st.set_page_config(layout="wide", page_title="Reinsurance Portfolio Manager")
st.sidebar.markdown("---")
fun_dashboard.set_title()
st.markdown("---")

# 1. 파일 업로드 섹션
st.sidebar.markdown("---")
st.sidebar.header("📂 File Upload")
yelt_file = st.sidebar.file_uploader("Select YELT (.csv, .xlsx)", type=["csv", "xlsx"], key="yelt_uploader",  on_change=fun_dashboard.reset_calculations)
contract_file = st.sidebar.file_uploader("Select Contract (.csv, .xlsx)", type=["csv", "xlsx"],key="contract_uploader",  on_change=fun_dashboard.reset_calculations)
currency_file = st.sidebar.file_uploader("Select Currency (.csv, .xlsx)", type=["csv", "xlsx"], key="currency_uploader",  on_change=fun_dashboard.reset_calculations)


# ── 탭 목록 ──────────────────────────────────────────────
TAB_NAMES = ["1. Data Check", "2. Assupmtion", "3. EP Calculation"]       


# ── 탭 이동 헬퍼 함수 ─────────────────────────────────────
def move_tab(direction: str):
    current_index = TAB_NAMES.index(st.session_state["active_tab"])

    if direction == "next":
        next_index = current_index + 1
        if next_index < len(TAB_NAMES):
            if TAB_NAMES[next_index] == "3. EP Calculation" and not st.session_state["tab3_unlocked"]:
                st.warning("⚠️ Assumptions have not been saved. Please click 'Save' in the '2. Assumptions' tab")
            else:
                st.session_state["active_tab"] = TAB_NAMES[next_index]

    elif direction == "prev":
        prev_index = current_index - 1
        if prev_index >= 0:
            st.session_state["active_tab"] = TAB_NAMES[prev_index]


# ── 탭 렌더링 ─────────────────────────────────────────────
tabs = st.tabs(    TAB_NAMES,    key="tab_widget",    default=st.session_state["active_tab"],  on_change="rerun",)

if yelt_file and contract_file and currency_file:
    
    with tabs[0]:
        df_yelt, aep_current,aep_all_current = tab1.render(move_tab, yelt_file, contract_file, currency_file)
    
    with tabs[1]:
        result_yelt=tab2.render(move_tab, df_yelt, contract_file, currency_file)
    
    with tabs[2]:
        tab3.render(move_tab,result_yelt,aep_current,aep_all_current)
else:
    st.warning("Please upload YELT, Contract, Currency files.")    

# ── Spyder 등 일반 Python 실행 지원 ───────────────────────
if __name__ == "__main__":
    if st.runtime.exists():
        pass
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())
