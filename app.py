import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. 페이지 레이아웃 및 제목 설정
st.set_page_config(page_title="Marketing ROI Dashboard", layout="wide")
st.title("🚀 마케팅 캠페인 성과 분석 대시보드 (Final)")

# 2. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data():
    # 깃허브에 올린 파일명과 일치해야 합니다.
    file_path = 'marketing_data.parquet'
    
    if os.path.exists(file_path):
        df = pd.read_parquet(file_path)
        
        # [데이터 전처리] 문자열(String)로 인식된 숫자를 숫자형으로 강제 변환
        # Acquisition_Cost 열에 $나 ,가 포함된 경우 제거 후 실수형(float) 변환
        if df['Acquisition_Cost'].dtype == 'object':
            df['Acquisition_Cost'] = df['Acquisition_Cost'].replace(r'[\$,]', '', regex=True).astype(float)
        else:
            df['Acquisition_Cost'] = pd.to_numeric(df['Acquisition_Cost'], errors='coerce')

        # ROI와 Conversion_Rate도 안전하게 숫자형으로 변환
        df['ROI'] = pd.to_numeric(df['ROI'], errors='coerce')
        df['Conversion_Rate'] = pd.to_numeric(df['Conversion_Rate'], errors='coerce')
        
        # 결측치(NaN)가 발생한 행은 계산에서 제외
        df = df.dropna(subset=['Acquisition_Cost', 'ROI', 'Conversion_Rate'])
        
        return df
    else:
        st.error(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        st.info(f"현재 폴더 내 파일 목록: {os.listdir()}")
        return None

df = load_data()

# 데이터가 성공적으로 로드된 경우에만 대시보드 출력
if df is not None:
    # 3. 사이드바 필터 구성
    st.sidebar.header("🔍 필터 설정")
    target_filter = st.sidebar.multiselect("타겟 고객 선택", sorted(df['Target_Audience'].unique()), default=df['Target_Audience'].unique())
    channel_filter = st.sidebar.multiselect("채널 선택", sorted(df['Channel_Used'].unique()), default=df['Channel_Used'].unique())

    # 데이터 필터링 적용
    filtered_df = df[(df['Target_Audience'].isin(target_filter)) & (df['Channel_Used'].isin(channel_filter))]

    # 4. 상단 핵심 지표 (Metrics)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("평균 ROI", f"{filtered_df['ROI'].mean():.2f}")
    # 원본 데이터의 Conversion_Rate가 0.1 형태면 *100을, 10% 형태면 그대로 사용 (여기서는 0.1 가정)
    m2.metric("평균 전환율(CVR)", f"{filtered_df['Conversion_Rate'].mean() * 100:.2f}%")
    m3.metric("평균 획득 비용(CPA)", f"${filtered_df['Acquisition_Cost'].mean():,.0f}")
    m4.metric("고성과 캠페인(ROI 7+)", f"{len(filtered_df[filtered_df['ROI'] >= 7]):,}건")

    # 5. 시각화 섹션
    st.divider()
    tab1, tab2 = st.tabs(["📊 채널 및 타겟 분석", "📈 상세 트렌드"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ 채널별 평균 ROI")
            roi_chart = filtered_df.groupby('Channel_Used')['ROI'].mean().reset_index().sort_values('ROI', ascending=False)
            fig1 = px.bar(roi_chart, x='ROI', y='Channel_Used', orientation='h', 
                          color='ROI', color_continuous_scale='Blues', 
                          range_x=[roi_chart['ROI'].min()*0.98, roi_chart['ROI'].max()*1.02])
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            st.subheader("🎯 타겟 고객별 전환율")
            cvr_chart = filtered_df.groupby('Target_Audience')['Conversion_Rate'].mean().reset_index().sort_values('Conversion_Rate', ascending=False)
            fig2 = px.bar(cvr_chart, x='Target_Audience', y='Conversion_Rate', 
                          color='Conversion_Rate', color_continuous_scale='Greens')
            st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("🌍 언어별 성과 교차 분석")
        lang_cvr = filtered_df.groupby('Language')['Conversion_Rate'].mean().reset_index().sort_values('Conversion_Rate', ascending=False)
        fig3 = px.line(lang_cvr, x='Language', y='Conversion_Rate', markers=True, 
                       title="언어 설정별 평균 전환율 추이")
        st.plotly_chart(fig3, use_container_width=True)

    # 6. 전문가 인사이트 섹션
    st.divider()
    with st.expander("💡 10년 차 마케팅 전문가의 전략적 제언 (Strategic Insight)"):
        st.write(f"""
        - **비용 최적화:** 현재 전체 평균 CPA는 **${filtered_df['Acquisition_Cost'].mean():,.0f}**입니다. 
          특정 인지도(Awareness) 캠페인의 높은 비용을 저비용 채널로 분산하여 효율을 높이십시오.
        - **고효율 타겟팅:** ROI 7.0 이상의 캠페인이 **{len(filtered_df[filtered_df['ROI'] >= 7])}건** 포착되었습니다. 
          주로 Instagram과 Google Ads 채널에서 발생하는 '골든 조합'에 예산을 집중하십시오.
        """)