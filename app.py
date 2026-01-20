import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 레이아웃 및 제목 설정
st.set_page_config(page_title="Marketing ROI Dashboard", layout="wide")
st.title("📊 마케팅 캠페인 성과 분석 대시보드 (Optimized)")

# 2. 데이터 로드 함수 (Parquet 대응)
@st.cache_data
def load_data():
    # 파일명이 'marketing_data.parquet'이라고 가정합니다. 
    # 실제 깃허브에 올린 파일명과 정확히 일치해야 합니다.
    file_path = 'marketing_data.parquet'
    
    if os.path.exists(file_path):
        return pd.read_parquet(file_path)
    else:
        st.error(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        st.info(f"현재 서버 경로의 파일들: {os.listdir()}")
        return None

df = load_data()

if df is not None:
    # 3. 사이드바 필터 구성
    st.sidebar.header("🔍 필터 설정")
    target_filter = st.sidebar.multiselect("타겟 고객 선택", df['Target_Audience'].unique(), default=df['Target_Audience'].unique())
    channel_filter = st.sidebar.multiselect("채널 선택", df['Channel_Used'].unique(), default=df['Channel_Used'].unique())

    # 데이터 필터링 적용
    filtered_df = df[(df['Target_Audience'].isin(target_filter)) & (df['Channel_Used'].isin(channel_filter))]

    # 4. 상단 핵심 지표 (Metrics)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("평균 ROI", f"{filtered_df['ROI'].mean():.2f}")
    m2.metric("평균 전환율(CVR)", f"{filtered_df['Conversion_Rate'].mean()*100:.2f}%")
    m3.metric("평균 획득 비용(CPA)", f"${filtered_df['Acquisition_Cost'].mean():,.0f}")
    m4.metric("고성과 캠페인(ROI 7+)", len(filtered_df[filtered_df['ROI'] >= 7]))

    # 5. 시각화 섹션
    tab1, tab2 = st.tabs(["채널 및 타겟 성과", "언어 및 관심사 분석"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ 채널별 평균 ROI")
            roi_chart = filtered_df.groupby('Channel_Used')['ROI'].mean().reset_index()
            fig1 = px.bar(roi_chart, x='ROI', y='Channel_Used', orientation='h', 
                          color='ROI', color_continuous_scale='Blues', range_x=[4.9, 5.05])
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("🎯 타겟별 전환율 비교")
            cvr_chart = filtered_df.groupby('Target_Audience')['Conversion_Rate'].mean().reset_index()
            fig2 = px.bar(cvr_chart, x='Target_Audience', y='Conversion_Rate', 
                          color='Conversion_Rate', color_continuous_scale='Greens')
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("🌍 언어별 전환 성과 (Women 35-44 Focus)")
        # 특정 타겟 필터링 예시
        women_35_44 = filtered_df[filtered_df['Target_Audience'] == 'Women 35-44']
        lang_cvr = women_35_44.groupby('Language')['Conversion_Rate'].mean().reset_index()
        fig3 = px.line(lang_cvr, x='Language', y='Conversion_Rate', markers=True, title="Women 35-44 언어별 선호도")
        st.plotly_chart(fig3, use_container_width=True)

    # 6. 전문가 인사이트
    st.divider()
    st.info("💡 **전략적 제언:** Awareness 캠페인의 CPA($70) 예산을 Social Media 채널로 재배분하여 ROI 하락 방어 필요.")