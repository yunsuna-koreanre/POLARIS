import sys
import os  # <-- 파일 경로 탐색을 위해 os 모듈 추가
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


# ── [추가] 샘플 데이터 다운로드 섹션 ───────────────────────
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Download Sample Data")

# 파일 경로 정의 (프로젝트 내 sample_data 폴더 기준)
sample_dir = "sample_data"
sample_files = {
    "YELT": "1. YELT SAMPLE.csv",
    "Contract": "2. contract.xlsx",
    "Currency": "3. currency_202601.xlsx"
}

for label, file_name in sample_files.items():
    file_path = os.path.join(sample_dir, file_name)
    
    # 로컬이나 배포 서버에 실제로 파일이 존재하는지 체크 후 다운로드 버튼 생성
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        st.sidebar.download_button(
            label=f"Download {label} Sample",
            data=file_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # xlsx용 MIME 타입 (csv일 경우 text/csv 사용)
        )
    else:
        st.sidebar.info(f"💡 no sample data ({file_name})")


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
