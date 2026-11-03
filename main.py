import streamlit as st
import pandas as pd

# Page Setup
st.set_page_config(
    page_title="하디-바인베르크 평형 시뮬레이터",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 집단유전학 하디-바인베르크 평형 & 진화 시뮬레이터")
st.markdown("대립유전자 빈도와 자연선택(도태율) 조건을 설정하여 세대별 유전자형 빈도 변화를 추적합니다.")
st.divider()

# Sidebar Setup
st.sidebar.header("⚙️ 유전학 조건 설정")

p_freq = st.sidebar.slider("초기 우성 대립유전자 빈도 (p)", min_value=0.01, max_value=0.99, value=0.50, step=0.01)
q_freq = round(1.0 - p_freq, 2)
st.sidebar.info(f"초기 열성 대립유전자 빈도 (q = 1 - p): **{q_freq:.2f}**")

generations = st.sidebar.number_input("추적할 세대 수 (Generations)", min_value=5, max_value=200, value=50, step=5)

st.sidebar.divider()
st.sidebar.subheader("🍃 진화 요인 설정 (자연선택)")
apply_selection = st.sidebar.checkbox("열성 순종(aa) 도태율 적용", value=False)
selection_coeff = st.sidebar.slider("열성 순종(aa) 도태율 (%)", min_value=0, max_value=100, value=20, step=5) if apply_selection else 0

# Main Logic
p_current = p_freq
q_current = q_freq
s = selection_coeff / 100.0

gen_list = []
p_list = []
q_list = []
AA_list = []
Aa_list = []
aa_list = []

for g in range(generations + 1):
    gen_list.append(g)
    
    # 하디-바인베르크 유전자형 빈도 계산
    AA = p_current ** 2
    Aa = 2 * p_current * q_current
    aa = q_current ** 2
    
    AA_list.append(round(AA, 4))
    Aa_list.append(round(Aa, 4))
    aa_list.append(round(aa, 4))
    p_list.append(round(p_current, 4))
    q_list.append(round(q_current, 4))
    
    # 다음 세대의 대립유전자 빈도 연산 (도태율 적용)
    if apply_selection and s > 0:
        # 도태 적용 후 적응도 기반 새 빈도 연산
        mean_fitness = 1.0 - (s * aa)
        if mean_fitness > 0:
            p_next = (AA + (0.5 * Aa)) / mean_fitness
            p_current = max(0.0, min(1.0, p_next))
            q_current = 1.0 - p_current
    else:
        # 평형 상태 유지
        pass

# Data Output
df_result = pd.DataFrame({
    "세대 (Gen)": gen_list,
    "우성 유전자 (p)": p_list,
    "열성 유전자 (q)": q_list,
    "AA (우성 순종)": AA_list,
    "Aa (잡종)": Aa_list,
    "aa (열성 순종)": aa_list
})

st.subheader("📊 1. 초기 vs 최종 세대 유전자형 빈도 비교")

col1, col2, col3, col4 = st.columns(4)
col1.metric("초기 p / q 빈도", f"{p_freq:.2f} / {q_freq:.2f}")
col2.metric("최종 p / q 빈도", f"{p_list[-1]:.4f} / {q_list[-1]:.4f}")
col3.metric("최종 AA 빈도", f"{AA_list[-1]*100:.2f}%")
col4.metric("최종 aa 빈도", f"{aa_list[-1]*100:.2f}%")

st.divider()

st.subheader("📈 2. 세대 경과에 따른 유전자형 빈도 변화 (Line Chart)")
chart_df = df_result.set_index("세대 (Gen)")[["AA (우성 순종)", "Aa (잡종)", "aa (열성 순종)"]]
st.line_chart(chart_df)

st.divider()

st.subheader("🧪 3. 하디-바인베르크 평형 진단 및 생물학적 해석")

if not apply_selection or selection_coeff == 0:
    st.info("💡 **하디-바인베르크 평형 유지:** 선택압이 존재하지 않아 세대가 지나도 대립유전자 빈도(p, q) 및 유전자형 비율이 일정하게 유지됩니다. (이상적인 멘델 집단)")
else:
    st.warning(f"💡 **진화 발생 (자연선택 개입):** 열성 순종(aa)에 {selection_coeff}%의 도태율이 적용되어 세대가 진행됨에 따라 열성 대립유전자(q)의 빈도가 감소하고 집단 내 생존 적응도가 변화합니다.")

st.divider()
st.subheader("📋 4. 세대별 상세 수치 데이터")
st.dataframe(df_result, use_container_width=True)
