import streamlit as st
import pandas as pd
import math

# ---------------------------------------------------------
# Page Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="미생물 지수적 증식 시뮬레이터",
    page_icon="🧫",
    layout="wide"
)

st.title("🧫 미생물/세포 지수적 증식 및 억제제 효능 시뮬레이터")
st.markdown("생명과학의 미생물 생장 수식 모델을 기반으로 개체 수 변화와 항생제(억제제)의 효과를 예측합니다.")
st.divider()

# ---------------------------------------------------------
# Sidebar: 조건 입력 및 예외 처리
# ---------------------------------------------------------
st.sidebar.header("⚙️ 시뮬레이션 조건 설정")

with st.sidebar.form("sim_form"):
    initial_pop = st.number_input("초기 미생물 수 (N₀, CFU)", min_value=1, max_value=100000, value=100, step=10)
    gen_time_min = st.number_input("1회 분열(세대) 소요 시간 (분)", min_value=1.0, max_value=1440.0, value=30.0, step=5.0)
    total_hours = st.number_input("총 시뮬레이션 시간 (시간)", min_value=1, max_value=72, value=12, step=1)
    
    st.divider()
    st.subheader("💊 억제제(항생제) 설정")
    use_inhibitor = st.checkbox("억제제 투여 시뮬레이션 적용")
    inhibit_time_hr = st.number_input("억제제 투여 시점 (시간 후)", min_value=0.0, max_value=72.0, value=4.0, step=0.5)
    inhibit_rate_pct = st.slider("억제제 효능 (증식 억제율 %)", min_value=0, max_value=100, value=80)

    submitted = st.form_submit_button("🧪 시뮬레이션 실행")

# ---------------------------------------------------------
# Main Logic & Exception Handling
# ---------------------------------------------------------
if submitted:
    try:
        # 입력값 유효성 예외 처리
        if initial_pop <= 0 or gen_time_min <= 0 or total_hours <= 0:
            st.error("🚨 모든 입력값(초기 균수, 세대 시간, 시뮬레이션 시간)은 0보다 커야 합니다.")
            st.stop()
            
        if use_inhibitor and inhibit_time_hr > total_hours:
            st.warning("⚠️ 억제제 투여 시점이 총 시뮬레이션 시간보다 큽니다. 시뮬레이션 범위 내로 투여 시점을 조정했습니다.")
            inhibit_time_hr = float(total_hours)

        # 핵심 알고리즘: 시간대별 개체 수 연산
        time_points = []
        pop_control = []     # 대조군 (억제제 미투여)
        pop_treated = []     # 실험군 (억제제 투여)
        
        gen_time_hr = gen_time_min / 60.0  # 분 단위를 시간 단위로 변환
        
        step_hr = 0.5
        steps = int(total_hours / step_hr) + 1

        for i in range(steps):
            t = i * step_hr
            time_points.append(t)
            
            # 1. 대조군 계산: N(t) = N0 * 2^(t / g)
            num_generations_ctrl = t / gen_time_hr
            pop
