# -*- coding: utf-8 -*-
"""
Created on Wed May 20 09:38:02 2026

@author: yunsu.na
"""
import numpy as np
import pandas as pd
import io
import streamlit as st

def set_title():
    st.sidebar.markdown("""
        <style>
            @import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css");
            /* 1) 전체 페이지 상단 여백(Padding) 제거 */
            .block-container {
                padding-top: 1rem;    /* 기본 6rem에서 1rem으로 축소 */
                padding-bottom: 0rem;            padding-left: 2rem;            padding-right: 2rem;
                font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;}
            
            /* 2) 커스텀 타이틀 스타일 정의 */
            .main-title {
                font-family: 'Pretendard', sans-serif !important;
                font-size: 28px !important; /* 폰트 크기 (원하는 대로 조절) */
                font-weight: bold;
                color: #63E5CE;            /* 글자 색상 */
                margin-top: 2px;         /* 타이틀 위쪽 여백 추가 조정 */
                margin-bottom: 0px;       /* 타이틀 아래쪽 여백 */  }
            .sub-title {
                font-family: 'Pretendard', sans-serif !important;
                font-size: 16px !important; /* 작은 폰트 크기 */
                font-weight: bold;
                color: #666666;            /* 약간 흐린 회색으로 세련되게 표현 */
                margin-top: 2px;
                margin-bottom: 5px;       /* 제목 섹션 아래 여백 */
                display: block;
        </style>
        
        <!-- 3) HTML 태그로 타이틀 출력 -->    
        <div class="main-title">🌟 POLARIS</div>
        <div class="sub-title">(Portfolio Oriented Loss & Accumulation Risk Intelligence System)</div>
    """, unsafe_allow_html=True)    

def highlight_columns(x):
    df = pd.DataFrame(  '',        index=x.index,        columns=x.columns    )
    highlight_cols = ['Target Net Share(%)',  'FX Rate(%)','Growth Rate(%)', 'Inflation Rate(%)'    ]
    for col in highlight_cols:
        df[col] = 'background-color: #FFF2CC'
    return df

def load_data(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)
    
    
# EP 함수
def EP_ALL(df, perspec, aepoep):
    data = pd.DataFrame([], columns=[perspec], index=['STD','AAL','5','10','20','50','100','200','250','500','1000'])
    try:
        if aepoep == sum:
            df_EP = df.pivot_table(values=[perspec], index=['YearID'], aggfunc=aepoep).fillna(0)
        else:
            df_YELT = df.pivot_table(values=[perspec], index=['YearID','EventID'], aggfunc=sum).fillna(0)
            df_EP = df_YELT.pivot_table(values=[perspec], index=['YearID'], aggfunc=aepoep).fillna(0)
        
        df2 = df_EP.sort_values(by=perspec, ascending=False)      
       
        summary = [np.sqrt(df2[perspec].dot(df2[perspec])/10000 - (df2[perspec].sum()/10000)**2),df2[perspec].sum()/10000,
                   df2.iloc[1999,0], df2.iloc[999,0], df2.iloc[499,0],
                   df2.iloc[199,0], df2.iloc[99,0], df2.iloc[49,0],
                   df2.iloc[39,0], df2.iloc[19,0], df2.iloc[9,0]]
        data = pd.DataFrame(summary, columns=[perspec], index=['STD','AAL','5','10','20','50','100','200','250','500','1000'])
        data.index.name='Return Period'
        data_reserved = data.iloc[::-1].copy()
        data_reserved.perspec = data_reserved.perspec.astype(float)
    except:
        pass
    return data_reserved

def EP_SEP(conlst, df, perspec, aepoep):
    data = pd.DataFrame([], columns=[conlst], index=['STD','AAL','5','10','20','50','100','200','250','500','1000'])
    try:
        if aepoep == sum:
            df_EP = df.pivot_table(values=[perspec], index=['YearID'], aggfunc=aepoep).fillna(0)
        else:
            df_YELT = df.pivot_table(values=[perspec], index=['YearID','EventID'], aggfunc=sum).fillna(0)
            df_EP = df_YELT.pivot_table(values=[perspec], index=['YearID'], aggfunc=aepoep).fillna(0)
            
        df1 = df_EP.sort_values(by=perspec, ascending=False)
        d = pd.DataFrame(0, columns=df.columns, index=np.arange(10000-len(df)))
        df2 = pd.concat([df1, d], axis=0).reset_index(drop=True)
       
        summary = [np.sqrt(df2[perspec].dot(df2[perspec])/10000 - (df2[perspec].sum()/10000)**2),df2[perspec].sum()/10000,
                   df2.iloc[1999,0], df2.iloc[999,0], df2.iloc[499,0],
                   df2.iloc[199,0], df2.iloc[99,0], df2.iloc[49,0],
                   df2.iloc[39,0], df2.iloc[19,0], df2.iloc[9,0]]
        data = pd.DataFrame(summary, columns=[conlst], index=['STD','AAL','5','10','20','50','100','200','250','500','1000'])        
        data.index.name='Contract Name'
        data_reserved = data.iloc[::-1].copy()        
        data_reserved.conlst=data_reserved.conlst.astype(float)
    except:
        pass
    return data_reserved

PERSISTENT_KEYS = {
    "yelt_uploader",
    "contract_uploader", 
    "currency_uploader",
    "active_tab",
    "tab3_unlocked",
}

def reset_calculations():
    # if "active_tab" not in st.session_state:
    #     st.session_state["active_tab"] = "1. Data Check"

    # if "tab3_unlocked" not in st.session_state:
    #     st.session_state["tab3_unlocked"] = False
        
    # # 만약 각 탭 내부의 렌더링 결과나 데이터프레임을 session_state에 캐싱하고 있다면 여기서 제거
    # if "df_yelt" in st.session_state:
    #     del st.session_state["df_yelt"]
    # if "result_yelt" in st.session_state:
    #     del st.session_state["result_yelt"]
        
    # # 알림을 띄우기 위해 플래그 설정 가능
    # st.toast("🔄 New file detected! Resetting calculations...", icon="ℹ️")
    keys_to_delete = [k for k in st.session_state if k not in PERSISTENT_KEYS]
    for k in keys_to_delete:
        del st.session_state[k]
    
    # active_tab, tab3_unlocked 초기값으로 리셋
    st.session_state["active_tab"] = "1. Data Check"
    st.session_state["tab3_unlocked"] = False
    
    st.toast("🔄 New file detected! Resetting calculations...", icon="ℹ️")

def create_excel_download(df1, df2, df3, df4):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # 첫 번째 시트 (Summary)
        df1.to_excel(writer, sheet_name='AEP ALL', index=True, startcol=0)
        df2.to_excel(writer, sheet_name='AEP ALL', index=True, startcol=len(df1.columns) + 2)
        
        # 두 번째 시트 (AEP BY CONT)
        df3_idx_name = df3.index.name if df3.index.name else "Contract Name"
        df4_idx_name = df4.index.name if df4.index.name else "Contract Name"
        
        df4_row_start = len(df3.columns) + 2 
        df3.T.to_excel(writer, sheet_name='AEP BY CONT', index=True, startcol=1, index_label=df3_idx_name)
        df4.T.to_excel(writer, sheet_name='AEP BY CONT', index=True, startcol=1, startrow = df4_row_start, index_label=df4_idx_name)
        
        # ==========================================
        # 2. XlsxWriter 포맷 정의 및 적용
        # ==========================================
        workbook  = writer.book
        
        # 포맷 정의      
        center_text_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'num_format': '@'}) 
        num_comma_format = workbook.add_format({'num_format': '#,##0',  'align': 'right', 'valign': 'vcenter'})
        title_format = workbook.add_format({'bold': True, 'align': 'left', 'valign': 'vcenter'})
        
        ws1 = writer.sheets['AEP ALL']        
        # 첫 번째 테이블 (A열: 인덱스, B열: 데이터)
        ws1.set_column('A:A', 15, center_text_format) # 인덱스 열 가운데 정렬
        ws1.set_column('B:B', 15, num_comma_format)   # 데이터 열 천단위 콤마                
        ws1.set_column('D:D', 15, center_text_format) # 인덱스 열 가운데 정렬
        ws1.set_column('E:E', 15, num_comma_format)   # 데이터 열 천단위 콤마
        
        # --- [시트 2] AEP BY CONT 서식 적용 ---
        ws2 = writer.sheets['AEP BY CONT']                
        ws2.write(0, 0, "CURRENT LOSS", title_format)
        ws2.write(df4_row_start - 1, 0, "TARGET LOSS", title_format)
        
        ws2.autofit()
        # ws2.set_column('A:A', 20, center_text_format)                
        
        ws2.set_column('C:Z', 15, num_comma_format)
        max_idx_len_df3 = max([len(str(x)) for x in df3.T.index] + [len(str(df3_idx_name))])
        max_idx_len_df4 = max([len(str(x)) for x in df4.T.index] + [len(str(df4_idx_name))])
        max_len = max(max_idx_len_df3, max_idx_len_df4)

        
        ws2.set_column('B:B', max(20, max_len + 5), center_text_format)


    output.seek(0)
    return output.getvalue()