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

with st.sidebar.form("sim_form"):
    initial_pop = st.number_input("초기 미생물 수 (N₀, CFU)", min_value=1, max_value=100000, value=100, step=10)
    gen_time_min = st.number_input("1회 분열(세대) 소요 시간 (분)", min_value=1.0, max_value=1440.0, value=30.0, step=5.0)
    total_hours = st.number_input("총 시뮬레이션 시간 (시간)", min_value=1, max_value=72, value=12, step=1)
    
    st.divider()
    st.subheader("💊 억제제(Inhibitor) 설정")
    use_inhibitor = st.checkbox("억제제 투여 적용", value=True)
    
    # 억제제 종류 선택 기능 추가
    inhibitor_type = st.selectbox(
        "억제제 작용 메커니즘 종류",
        [
            "1. 경쟁적 억제제 (Competitive)",
            "2. 비경쟁적 억제제 (Non-competitive)",
            "3. 무경쟁적 억제제 (Uncompetitive)",
            "4. 사멸 유도형 (Bactericidal / 100% 억제)"
        ]
    )
    
    inhibit_time_hr = st.number_input("억제제 투여 시점 (시간 후)", min_value=0.0, max_value=72.0, value=4.0, step=0.5)
    inhibit_conc = st.slider("억제제 농도 / 강도 (%)", min_value=10, max_value=100, value=70)

    submitted = st.form_submit_button("🧪 시뮬레이션 실행")

# ---------------------------------------------------------
# Main Logic & Exception Handling
# ---------------------------------------------------------
if submitted:
    try:
        # 입력값 유효성 예외 처리
        if initial_pop <= 0 or gen_time_min <= 0 or total_hours <= 0:
            st.error("🚨 모든 입력값은 0보다 커야 합니다.")
            st.stop()
            
        if use_inhibitor and inhibit_time_hr > total_hours:
            st.warning("⚠️ 억제제 투여 시점이
