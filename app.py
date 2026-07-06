import re

import pandas as pd
import streamlit as st

CSV_PATH = "서울특별시_강남구_거리가게 위치정보_20211201.csv"

st.set_page_config(page_title="강남구 거리가게 분석", layout="wide")


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="cp949")

    def extract_dong(addr: str) -> str:
        if not isinstance(addr, str):
            return "기타"
        m = re.search(r"강남구\s+(\S+동)", addr)
        return m.group(1) if m else "기타"

    df["행정동"] = df["소재지지번주소"].apply(extract_dong)
    return df


df = load_data(CSV_PATH)

st.title("서울특별시 강남구 거리가게 위치정보 분석")
st.caption(f"데이터 기준일자: {df['데이터기준일자'].iloc[0]}")

# --- 사이드바 필터 ---
st.sidebar.header("필터")

gubun_options = sorted(df["구분"].dropna().unique())
gubun_sel = st.sidebar.multiselect("구분", gubun_options, default=gubun_options)

item_options = sorted(df["취급물품"].dropna().unique())
item_sel = st.sidebar.multiselect("취급물품", item_options, default=item_options)

dong_options = sorted(df["행정동"].dropna().unique())
dong_sel = st.sidebar.multiselect("행정동", dong_options, default=dong_options)

filtered = df[
    df["구분"].isin(gubun_sel)
    & df["취급물품"].isin(item_sel)
    & df["행정동"].isin(dong_sel)
]

# --- 요약 지표 ---
col1, col2, col3 = st.columns(3)
col1.metric("거리가게 수", f"{len(filtered):,}")
col2.metric("취급물품 종류", filtered["취급물품"].nunique())
col3.metric("행정동 수", filtered["행정동"].nunique())

st.divider()

# --- 차트 ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("취급물품별 거리가게 수")
    item_counts = filtered["취급물품"].value_counts()
    st.bar_chart(item_counts)

with chart_col2:
    st.subheader("행정동별 거리가게 수 (상위 15)")
    dong_counts = filtered["행정동"].value_counts().head(15)
    st.bar_chart(dong_counts)

st.subheader("구분별 거리가게 수")
gubun_counts = filtered["구분"].value_counts()
st.bar_chart(gubun_counts)

st.divider()

# --- 데이터 테이블 & 다운로드 ---
st.subheader("상세 데이터")
st.dataframe(filtered, use_container_width=True)

csv_bytes = filtered.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "필터링된 데이터 CSV 다운로드",
    data=csv_bytes,
    file_name="강남구_거리가게_필터링.csv",
    mime="text/csv",
)
