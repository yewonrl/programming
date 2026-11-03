import streamlit as st
import pandas as pd
import math

# ---------------------------------------------------------
# Page Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="미생물 지수적 증식 및 억제제 시뮬레이터",
    page_icon="🧫",
    layout="wide"
)

st.title("🧫 미생물 증식 및 억제제 종류별 효능 시뮬레이터")
st.markdown("생명과학의 **효소 억제 메커니즘(경쟁적/비경쟁적/무경쟁적)**을 적용하여 억제제 종류별 미생물 생장 곡선을 비교 분석합니다.")
st.divider()

# ---------------------------------------------------------
# Sidebar: 조건 입력 및 억제제 종류 선택
# ---------------------------------------------------------
st.sidebar.header("⚙️ 시뮬레이션 조건 설정")

initial_pop = st.sidebar.number_input("초기 미생물 수 (N₀, CFU)", min_value=1, max_value=100000, value=100, step=10)
gen_time_min = st.sidebar.number_input("1회 분열(세대) 소요 시간 (분)", min_value=1.0, max_value=1440.0, value=30.0, step=5.0)
total_hours = st.sidebar.number_input("총 시뮬레이션 시간 (시간)", min_value=1, max_value=72, value=12, step=1)

st.sidebar.divider()
st.sidebar.subheader("💊 억제제(Inhibitor) 설정")
use_inhibitor = st.sidebar.checkbox("억제제 투여 적용", value=True)

inhibitor_type = st.sidebar.selectbox("억제제 작용 메커니즘 종류", ["1. 경쟁적 억제제 (Competitive)", "2. 비경쟁적 억제제 (Non-competitive)", "3. 무경쟁적 억제제 (Uncompetitive)", "4. 사멸 유도형 (Bactericidal / 100% 억제)"])

inhibit_time_hr = st.sidebar.number_input("억제제 투여 시점 (시간 후)", min_value=0.0, max_value=72.0, value=4.0, step=0.5)
inhibit_conc = st.sidebar.slider("억제제 농도 / 강도 (%)", min_value=10, max_value=100, value=70)

# ---------------------------------------------------------
# Main Logic & Computation
# ---------------------------------------------------------
try:
    if initial_pop <= 0 or gen_time_min <= 0 or total_hours <= 0:
        st.error("🚨 모든 입력값은 0보다 커야 합니다.")
    else:
        if use_inhibitor and inhibit_time_hr > total_hours:
            st.warning("⚠️ 억제제 투여 시점이 총 시뮬레이션 시간보다 커 범위를 자동으로 조정했습니다.")
            inhibit_time_hr = float(total_hours)

        # 시간 및 생장 알고리즘 연산
        time_points = []
