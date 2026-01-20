import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 레이아웃 및 제목
st.set_page_config(page_title="Marketing Dashboard", layout="wide")
st.title("📊 마케팅 캠페인 성과 분석 대시보드")

# 2. 데이터 불러오기
@st.cache_data
def load_data():
    # 파일명을 본인의 파일명과 일치시키세요
    df = pd.read_csv('2026_01_19.marketing_campaign_d.csv')
    return df

df = load_data()

# 3. 사이드바 필터 구성
st.sidebar.header("🔍 필터 설정")
target_filter = st.sidebar.multiselect("타겟 고객 선택", df['Target_Audience'].unique(), default=df['Target_Audience'].unique())
channel_filter = st.sidebar.multiselect("채널 선택", df['Channel_Used'].unique(), default=df['Channel_Used'].unique())

# 데이터 필터링 적용
filtered_df = df[(df['Target_Audience'].isin(target_filter)) & (df['Channel_Used'].isin(channel_filter))]

# 4. 상단 핵심 지표 (Metrics)
m1, m2, m3 = st.columns(3)
m1.metric("평균 ROI", f"{filtered_df['ROI'].mean():.2f}")
m2.metric("평균 전환율(CVR)", f"{filtered_df['Conversion_Rate'].mean()*100:.2f}%")
m3.metric("평균 획득 비용(CPA)", f"${filtered_df['Acquisition_Cost'].mean():,.0f}")

# 5. 시각화 섹션
col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ 채널별 평균 ROI")
    roi_chart = filtered_df.groupby('Channel_Used')['ROI'].mean().reset_index()
    fig1 = px.bar(roi_chart, x='ROI', y='Channel_Used', orientation='h', 
                  color='ROI', color_continuous_scale='Blues')
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("🎯 타겟별 전환율 비교")
    cvr_chart = filtered_df.groupby('Target_Audience')['Conversion_Rate'].mean().reset_index()
    fig2 = px.bar(cvr_chart, x='Target_Audience', y='Conversion_Rate', 
                  color='Conversion_Rate', color_continuous_scale='Greens')
    st.plotly_chart(fig2, use_container_width=True)

# 6. 전문가 인사이트 (텍스트 상자)
st.divider()
st.warning("💡 **전문가 권고:** Awareness 캠페인의 CPA($70)가 너무 높습니다. 이 예산을 Social Media로 이전하여 ROI를 극대화하세요.")