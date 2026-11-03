import streamlit as st
import pandas as pd
import math

# Page Setup
st.set_page_config(
    page_title="미생물 생장 시뮬레이터",
    page_icon="microscope",
    layout="wide"
)

st.title("미생물 증식 및 억제제 효능 시뮬레이터")
st.markdown("생명과학의 효소 억제 메커니즘을 적용한 미생물 생장 시뮬레이터입니다.")
st.divider()

# Sidebar Setup
st.sidebar.header("조건 설정")

initial_pop = st.sidebar.number_input("초기 미생물 수 (N0, CFU)", min_value=1, max_value=100000, value=100, step=10)
gen_time_min = st.sidebar.number_input("1회 분열 소요 시간 (분)", min_value=1.0, max_value=1440.0, value=30.0, step=5.0)
total_hours = st.sidebar.number_input("총 시뮬레이션 시간 (시간)", min_value=1, max_value=72, value=12, step=1)

st.sidebar.divider()
st.sidebar.subheader("억제제 설정")
use_inhibitor = st.sidebar.checkbox("억제제 적용", value=True)

inhibitor_type = st.sidebar.selectbox(
    "억제제 종류 선택",
    [
        "1. 경쟁적 억제제",
        "2. 비경쟁적 억제제",
        "3. 무경쟁적 억제제",
        "4. 사멸 유도형"
    ]
)

inhibit_time_hr = st.sidebar.number_input("투여 시점 (시간 후)", min_value=0.0, max_value=72.0, value=4.0, step=0.5)
inhibit_conc = st.sidebar.slider("억제제 농도 (%)", min_value=10, max_value=100, value=70)

# Main Logic
if use_inhibitor and inhibit_time_hr > total_hours:
    st.warning("투여 시점이 총 시간을 초과하여 자동 조정되었습니다.")
    inhibit_time_hr = float(total_hours)

time_points = []
pop_control = []
pop_treated = []

gen_time_hr = gen_time_min / 60.0
step_hr = 0.5
steps = int(total_hours / step_hr) + 1

for i in range(steps):
    t = i * step_hr
    time_points.append(t)
    
    # 1. 대조군 연산
    num_generations_ctrl = t / gen_time_hr
    pop_c = initial_pop * (2 ** num_generations_ctrl)
    pop_control.append(round(pop_c, 2))
    
    # 2. 실험군 연산
    if not use_inhibitor or t < inhibit_time_hr:
        pop_t = pop_c
    else:
        time_after = t - inhibit_time_hr
        pop_at_inhibit = initial_pop * (2 ** (inhibit_time_hr / gen_time_hr))
        intensity = inhibit_conc / 100.0
        
        if "1. 경쟁적" in inhibitor_type:
            adjusted_gen_time = gen_time_hr * (1 + (intensity * 1.5))
            pop_t = pop_at_inhibit * (2 ** (time_after / adjusted_gen_time))
        elif "2. 비경쟁적" in inhibitor_type:
            adjusted_gen_time = gen_time_hr * (1 + (intensity * 4.0))
            pop_t = pop_at_inhibit * (2 ** (time_after / adjusted_gen_time))
        elif "3. 무경쟁적" in inhibitor_type:
            adjusted_gen_time = gen_time_hr * (1 + (intensity * 2.5))
            pop_t = pop_at_inhibit * (2 ** (time_after / adjusted_gen_time))
        else:
            pop_t = pop_at_inhibit * math.exp(-0.15 * intensity * time_after)

    pop_treated.append(round(pop_t, 2))

# Data Output
df_result = pd.DataFrame({
    "시간 (시간)": time_points,
    "대조군 (미투여)": pop_control,
    f"실험군 ({inhibitor_type.split(' ')[1]})": pop_treated
})

st.subheader("1. 시뮬레이션 결과 메트릭")

final_ctrl = pop_control[-1]
final_treat = pop_treated[-1]
reduction_rate = ((final_ctrl - final_treat) / final_ctrl) * 100 if final_ctrl > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("최종 개체 수 (대조군)", f"{final_ctrl:,.0f} CFU")
col2.metric("최종 개체 수 (실험군)", f"{final_treat:,.0f} CFU")
col3.metric("개체 수 감소율", f"{reduction_rate:.1f}%")

st.divider()

st.subheader(f"2. 생장 곡선 시각화 [{inhibitor_type}]")
chart_df = df_result.set_index("시간 (시간)")
st.line_chart(chart_df)

st.divider()

st.subheader("3. 생명과학 메커니즘 분석")

if "1. 경쟁적" in inhibitor_type:
    st.info("경쟁적 억제제: 활성 부위에 기질과 경쟁 결합합니다. 세대 시간이 증가합니다.")
elif "2. 비경쟁적" in inhibitor_type:
    st.warning("비경쟁적 억제제: 다른 부위에 결합하여 구조를 변형합니다. Vmax가 감소합니다.")
elif "3. 무경쟁적" in inhibitor_type:
    st.info("무경쟁적 억제제: 효소-기질 복합체에 결합하여 반응을 방해합니다.")
else:
    st.error("사멸 유도형: 세균 분열 중단으로 개체 수가 감소합니다.")

st.divider()
st.subheader("4. 상세 수치 데이터")
st.dataframe(df_result, use_container_width=True)
