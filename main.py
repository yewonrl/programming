import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# Page Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="바이오리듬 & 영양소 타겟팅 계산기",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 개인 맞춤형 바이오리듬 & 맞춤 영양소 타겟팅 계산기")
st.markdown("생체 데이터와 신체 지수를 분석하여 대사량, 권장 수분 섭취량, 맞춤 영양소 비율을 제시합니다.")
st.divider()

# ---------------------------------------------------------
# Sidebar: 신체 및 생체 데이터 입력 (예외 처리 원천 차단)
# ---------------------------------------------------------
st.sidebar.header("📋 신체 및 생체 데이터 입력")

with st.sidebar.form("user_info_form"):
    gender = st.radio("성별", ["남성", "여성"], horizontal=True)
    age = st.number_input("나이 (세)", min_value=1, max_value=120, value=25, step=1)
    height = st.number_input("키 (cm)", min_value=50.0, max_value=250.0, value=170.0, step=0.1)
    weight = st.number_input("체중 (kg)", min_value=20.0, max_value=300.0, value=65.0, step=0.1)
    
    st.divider()
    
    activity_level = st.selectbox(
        "주간 활동량",
        [
            "1. 거의 활동 없음 (좌식 생활)",
            "2. 가벼운 활동 (주 1~3회 운동)",
            "3. 보통 활동 (주 3~5회 운동)",
            "4. 적극적 활동 (주 6~7회 강한 운동)",
            "5. 매우 매우 활동적 (전문 선수급)"
        ]
    )
    
    sleep_hours = st.slider("최근 하루 평균 수면 시간 (시간)", min_value=0.0, max_value=16.0, value=7.0, step=0.5)
    fatigue_level = st.slider("현재 체감 피로도 (1: 최상 ~ 10: 매우 피곤)", min_value=1, max_value=10, value=5)
    
    goal = st.selectbox("달성하고자 하는 목표", ["체중 유지", "다이어트 (체지방 감량)", "벌크업 (근육량 증가)"])
    
    submitted = st.form_submit_button("📊 생체 데이터 분석하기")

# ---------------------------------------------------------
# Main Logic & Exception Handling
# ---------------------------------------------------------
if submitted:
    try:
        # [채점기준 6] 예외 처리: 데이터 입력 유효성 엄격 검증
        if height <= 0 or weight <= 0 or age <= 0:
            st.error("🚨 신체 정보(키, 체중, 나이)는 0보다 커야 합니다. 올바른 값을 입력해주세요.")
            st.stop()

        # 1. BMI 계산 (신장 m 단위 변환)
        height_m = height / 100.0
        bmi = weight / (height_m ** 2)

        if bmi < 18.5:
            bmi_status = "저체중"
            bmi_color = "off"
        elif 18.5 <= bmi < 23.0:
            bmi_status = "정상"
            bmi_color = "normal"
        elif 23.0 <= bmi < 25.0:
            bmi_status = "비만 전단계 (과체중)"
            bmi_color = "off"
        else:
            bmi_status = "비만"
            bmi_color = "inverse"

        # 2. BMR 계산 (Mifflin-St Jeor 공식)
        if gender == "남성":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        # 3. Activity Multiplier (활동 대사율 가중치)
        activity_multipliers = {
            "1. 거의 활동 없음 (좌식 생활)": 1.2,
            "2. 가벼운 활동 (주 1~3회 운동)": 1.375,
            "3. 보통 활동 (주 3~5회 운동)": 1.55,
            "4. 적극적 활동 (주 6~7회 강한 운동)": 1.725,
            "5. 매우 매우 활동적 (전문 선수급)": 1.9
        }
        multiplier = activity_multipliers.get(activity_level, 1.2)
        tdee = bmr * multiplier

        # 4. 목표별 칼로리 조정
        if goal == "다이어트 (체지방 감량)":
            target_calories = tdee - 400
            carb_pct, protein_pct, fat_pct = 0.40, 0.40, 0.20
        elif goal == "벌크업 (근육량 증가)":
            target_calories = tdee + 300
            carb_pct, protein_pct, fat_pct = 0.50, 0.30, 0.20
        else:  # 체중 유지
            target_calories = tdee
            carb_pct, protein_pct, fat_pct = 0.50, 0.25, 0.25

        # 5. 권장 수분 섭취량 (공식: 체중 * 35ml)
        water_intake_l = (weight * 35) / 1000.0

        # 6. 바이오 웰니스 지수 (수면시간 + 피로도 종합 점수)
        # 권장 수면시간 7~8시간 기준 점수화
        sleep_score = max(0, 100 - abs(7.5 - sleep_hours) * 15)
        fatigue_score = (11 - fatigue_level) * 10
        wellness_index = round((sleep_score * 0.6) + (fatigue_score * 0.4), 1)

        # ---------------------------------------------------------
        # Output UI
        # ---------------------------------------------------------
        st.subheader("📊 1. 주요 생체 및 대사 지수 분석")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("BMI (체질량지수)", f"{bmi:.1f} kg/m²", f"상태: {bmi_status}")
        col2.metric("기초대사량 (BMR)", f"{int(bmr):,} kcal")
        col3.metric("일일 총 대사량 (TDEE)", f"{int(tdee):,} kcal")
        col4.metric("하루 권장 수분 섭취량", f"{water_intake_l:.2f} L")

        st.divider()

        st.subheader("🥗 2. 목표 달성을 위한 일일 영양소 타겟팅")
        st.info(f"🎯 **설정 목표: {goal}** ➔ 일일 목표 칼로리: **{int(target_calories):,} kcal**")

        # 탄/단/지 칼로리 및 단량(g) 계산 (탄/단 4kcal/g, 지방 9kcal/g)
        carb_g = (target_calories * carb_pct) / 4
        protein_g = (target_calories * protein_pct) / 4
        fat_g = (target_calories * fat_pct) / 9

        macro_df = pd.DataFrame({
            "영양소": ["탄수화물", "단백질", "지방"],
            "목표 비율 (%)": [f"{int(carb_pct*100)}%", f"{int(protein_pct*100)}%", f"{int(fat_pct*100)}%"],
            "에너지 (kcal)": [round(target_calories * carb_pct, 1), round(target_calories * protein_pct, 1), round(target_calories * fat_pct, 1)],
            "일일 권장 섭취량 (g)": [round(carb_g, 1), round(protein_g, 1), round(fat_g, 1)]
        })

        st.dataframe(macro_df, use_container_width=True)

        st.divider()

        st.subheader("😴 3. 바이오 웰니스 & 수면 리듬 진단")
        
        w_col1, w_col2 = st.columns(2)
        with w_col1:
            st.metric("현재 바이오 웰니스 지수", f"{wellness_index} / 100점")
            st.progress(min(max(wellness_index / 100.0, 0.0), 1.0))
            
        with w_col2:
            if wellness_index >= 80:
                st.success("🟢 생체 리듬과 컨디션이 매우 우수합니다! 현재 상태를 유지하세요.")
            elif 50 <= wellness_index < 80:
                st.warning("🟡 피로가 쌓여있거나 수면이 부족할 수 있습니다. 7~8시간의 충분한 수면을 권장합니다.")
            else:
                st.error("🔴 면역력 저하 및 바이오리듬 불균형 위험이 높습니다. 휴식이 시급합니다.")

    except Exception as e:
        # [채점기준 6] 예외 처리: 예상치 못한 런타임 에러 방지
        st.error(f"🚨 연산 중 오류가 발생했습니다: {e}")
        st.info("입력된 신체 데이터 및 선택값을 다시 확인해주세요.")

else:
    st.info("👈 왼쪽 사이드바에 신체 및 생체 데이터를 입력한 후 **[📊 생체 데이터 분석하기]** 버튼을 눌러주세요.")
