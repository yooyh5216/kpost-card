import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="우체국 체크카드 추천시스템",
    page_icon="💳",
    layout="centered"
)

# CSS 꾸미기
st.markdown("""
<style>

.main {
    background-color: #f5f7fb;
}

.stButton>button {
    background-color: #0B5ED7;
    color: white;
    border-radius: 12px;
    height: 50px;
    width: 100%;
    font-size: 18px;
    font-weight: bold;
    border: none;
}

.stButton>button:hover {
    background-color: #084298;
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.title-text {
    font-size: 38px;
    font-weight: bold;
    color: #0B5ED7;
}

.sub-text {
    color: gray;
    font-size: 17px;
}

</style>
""", unsafe_allow_html=True)

# 제목
st.markdown(
    """
    <div class="title-text">
    💳 우체국 체크카드 추천시스템
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="sub-text">
    소비 성향 기반 맞춤형 우체국 체크카드를 추천해드립니다.
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")

# 엑셀 불러오기
card_df = pd.read_excel(
    "카드엑셀디비.xlsx",
    sheet_name="카드DB"
)

score_df = pd.read_excel(
    "카드엑셀디비.xlsx",
    sheet_name="추천점수DB"
)

# 사용자 입력
st.subheader("📝 사용자 정보 입력")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input(
        "나이",
        min_value=10,
        max_value=100,
        value=30
    )

with col2:
    gender = st.selectbox(
        "성별",
        ["남성", "여성"]
    )

amount = st.selectbox(
    "월 카드 사용금액",
    ["10만원", "30만원", "50만원", "100만원 이상"]
)

혜택리스트 = [
    "온라인쇼핑",
    "마트장보기",
    "백화점",
    "생활잡화",
    "카페",
    "배달",
    "OTT",
    "병원",
    "주유",
    "해외",
    "사업자",
    "교통",
    "육아",
    "편의점",
    "통신",
    "생활형"
]

혜택1 = st.selectbox(
    "주사용혜택1",
    혜택리스트
)

혜택2후보 = [
    x for x in 혜택리스트
    if x != 혜택1
]

혜택2 = st.selectbox(
    "주사용혜택2",
    혜택2후보
)

col3, col4 = st.columns(2)

with col3:
    ott = st.radio(
        "OTT 사용",
        ["Y", "N"]
    )

with col4:
    delivery = st.radio(
        "배달앱 사용",
        ["Y", "N"]
    )

col5, col6 = st.columns(2)

with col5:
    overseas = st.radio(
        "해외 사용",
        ["Y", "N"]
    )

with col6:
    business = st.radio(
        "사업자 여부",
        ["Y", "N"]
    )

traffic = st.radio(
    "교통 사용 여부",
    ["Y", "N"]
)

# 추천 버튼
if st.button("🎯 체크카드 추천받기"):

    컬럼1 = 혜택1 + "점수"
    컬럼2 = 혜택2 + "점수"

    # 기본 점수 계산
    score_df["추천총점"] = (
        score_df[컬럼1] * 0.7 +
        score_df[컬럼2] * 0.3
    )

    # 추가 조건 점수
    if ott == "Y":
        score_df["추천총점"] += (
            score_df["OTT점수"] * 0.5
        )

    if delivery == "Y":
        score_df["추천총점"] += (
            score_df["배달점수"] * 0.5
        )

    if overseas == "Y":
        score_df["추천총점"] += (
            score_df["해외점수"] * 0.7
        )

    if business == "Y":
        score_df["추천총점"] += (
            score_df["사업자점수"] * 0.7
        )

    if traffic == "Y":
        score_df["추천총점"] += (
            score_df["교통점수"] * 0.5
        )

    # 월 사용금액 반영
    if amount == "100만원 이상":
        score_df["추천총점"] += (
            score_df["생활형점수"] * 0.3
        )

    # 점수순 정렬
    top_cards = score_df.sort_values(
        by="추천총점",
        ascending=False
    )

    # 추천 카드 선정
    추천카드 = []

    for i, row in top_cards.iterrows():

        카드정보 = card_df[
            card_df["카드ID"] == row["카드ID"]
        ].iloc[0]

        카드명 = str(카드정보["카드명"])

        # 이미 같은 카드명 계열 추천됐는지 확인
        중복 = False

        for saved in 추천카드:

            saved_info = card_df[
                card_df["카드ID"] == saved["카드ID"]
            ].iloc[0]

            saved_name = str(saved_info["카드명"])

            # 영리한 / 동행 / PLUS 등 유사계열 방지
            if (
                카드명[:3] == saved_name[:3]
            ):
                중복 = True

        if 중복 == False:
            추천카드.append(row)

        if len(추천카드) == 2:
            break

    top2 = pd.DataFrame(추천카드)

    # 카드정보 병합
    result = pd.merge(
        top2,
        card_df,
        on="카드ID"
    )

    st.write("")
    st.subheader("🏆 추천 결과")

    for i, row in result.iterrows():

        st.markdown("---")

        image_path = (
            f"card_images/{row.iloc[0]}.png"
        )

        col_img, col_info = st.columns([1,2])

        with col_img:
            st.image(
                image_path,
                width=180
            )

        with col_info:

            st.markdown(
                f"## 💳 {row.iloc[1]}"
            )

            st.metric(
                "추천점수",
                round(row["추천총점"], 1)
            )

            st.write(
                f"💰 월혜택한도 : {row.iloc[5]}"
            )

            st.write(
                f"📌 전월실적 : {row.iloc[4]}"
            )

            st.write(
                f"🔑 추천키워드 : {row.iloc[25]}"
            )

            st.write(
                f"✨ 주요혜택 : {row.iloc[26]}"
            )

        # 추천 이유
        추천이유 = []

        if (
            ott == "Y" and
            row["OTT점수"] >= 7
        ):
            추천이유.append(
                "OTT 혜택 우수"
            )

        if (
            delivery == "Y" and
            row["배달점수"] >= 7
        ):
            추천이유.append(
                "배달 혜택 우수"
            )

        if (
            overseas == "Y" and
            row["해외점수"] >= 7
        ):
            추천이유.append(
                "해외 혜택 우수"
            )

        if (
            business == "Y" and
            row["사업자점수"] >= 7
        ):
            추천이유.append(
                "사업자 혜택 우수"
            )

        if (
            traffic == "Y" and
            row["교통점수"] >= 7
        ):
            추천이유.append(
                "교통 혜택 우수"
            )

        추천문구 = ", ".join(추천이유)

        st.info(
            f"📢 추천 이유 : {추천문구}"
        )

        # 상세 혜택
        with st.expander(
            "상세 혜택 보기"
        ):

            st.write(
                f"☕ 카페혜택 : {row['카페혜택']}"
            )

            st.write(
                f"🛒 쇼핑혜택 : {row['쇼핑혜택']}"
            )

            st.write(
                f"🛍 온라인쇼핑혜택 : {row['온라인쇼핑혜택']}"
            )

            st.write(
                f"🍔 배달혜택 : {row['배달혜택']}"
            )

            st.write(
                f"⛽ 주유혜택 : {row['주유혜택']}"
            )

            st.write(
                f"🏥 병원혜택 : {row['병원혜택']}"
            )

            st.write(
                f"💊 약국혜택 : {row['약국혜택']}"
            )

            st.write(
                f"🌍 해외혜택 : {row['해외혜택']}"
            )

            st.write(
                f"🏣 우체국혜택 : {row['우체국혜택']}"
            )