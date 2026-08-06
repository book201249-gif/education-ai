import re

import streamlit as st

from ai.gemini import read_documents
from word_writer import create_word_document

st.set_page_config(
    page_title="AI 教育價建檔系統",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 AI 教育價申請自動建檔系統")
st.write("上傳學生證與發票，AI 將辨識資料並自動產生 Word。")

st.divider()

# -----------------------
# Session State
# -----------------------

if "student_result" not in st.session_state:
    st.session_state.student_result = None

if "invoice_result" not in st.session_state:
    st.session_state.invoice_result = None

if "student_card_image_bytes" not in st.session_state:
    st.session_state.student_card_image_bytes = None

if "student_card_back_image_bytes" not in st.session_state:
    st.session_state.student_card_back_image_bytes = None
# -----------------------
# 上傳圖片
# -----------------------

uploaded_images = st.file_uploader(
    "📷 一次上傳學生證正面、學生證背面及發票",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

st.caption("⚠️ 請先遮蔽學生證正面的大頭照及不必要的個資。")

student_card = None
student_card_back = None
invoice = None

if len(uploaded_images) == 3:
    student_card = st.selectbox(
        "選擇學生證正面",
        uploaded_images,
        index=0,
        format_func=lambda file: file.name,
    )

    student_card_back = st.selectbox(
        "選擇學生證背面",
        uploaded_images,
        index=1,
        format_func=lambda file: file.name,
    )

    invoice = st.selectbox(
        "選擇發票",
        uploaded_images,
        index=2,
        format_func=lambda file: file.name,
    )

elif uploaded_images:
    st.warning("請一次選取正面、背面及發票，共 3 張圖片。")

col1, col2, col3 = st.columns(3)

with col1:
    if student_card:
        st.image(
            student_card,
            caption="學生證正面",
            use_container_width=True,
        )

with col2:
    if student_card_back:
        st.image(
            student_card_back,
            caption="學生證背面",
            use_container_width=True,
        )

with col3:
    if invoice:
        st.image(
            invoice,
            caption="發票",
            use_container_width=True,
        )


# -----------------------
# Gemini 辨識
# -----------------------

if st.button("🤖 開始辨識", type="primary"):

    if len(uploaded_images) != 3:
        st.error("請一次上傳 3 張圖片")

    elif len(
        {
            student_card.name,
            student_card_back.name,
            invoice.name,
        }
    ) != 3:
        st.error("正面、背面及發票不可選擇同一張圖片")

    else:
        with st.spinner("Gemini 正在辨識學生證正面與發票..."):

            result = read_documents(
                student_card.getvalue(),
                student_card.type,
                invoice.getvalue(),
                invoice.type,
            )

            st.session_state.student_result = result["student"]
            st.session_state.invoice_result = result["invoice"]

            # 保存正面圖片
            st.session_state.student_card_image_bytes = (
                student_card.getvalue()
            )

            # 保存背面圖片，但不傳給 Gemini
            st.session_state.student_card_back_image_bytes = (
                student_card_back.getvalue()
            )

        st.success("辨識完成！")


# -----------------------
# 顯示辨識結果
# -----------------------

if (
    st.session_state.student_result is not None
    and st.session_state.invoice_result is not None
):

    student_result = st.session_state.student_result
    invoice_result = st.session_state.invoice_result

    st.divider()

    st.subheader("學生資料")

    student_id = st.text_input(
        "學號",
        value=student_result.get("student_id", ""),
    )

    full_name = st.text_input(
        "姓名",
        value=student_result.get("full_name", ""),
    )

    surname = st.text_input(
        "姓氏",
        value=student_result.get("surname", ""),
    )

    id_and_surname = st.text_input(
        "證號+姓氏",
        value=f"{student_id} {surname}",
    )

    st.divider()

    st.subheader("發票資料")

    invoice_date = st.text_input(
        "發票日期",
        value=invoice_result.get("invoice_date", ""),
    )

    invoice_number = st.text_input(
        "發票號碼",
        value=invoice_result.get("invoice_number", ""),
    )

    amount = st.text_input(
        "發票金額",
        value=str(invoice_result.get("amount", "")),
    )

    product_model = st.text_input(
        "產品型號",
        value=invoice_result.get("product_model", ""),
    )

    st.info("產品描述固定留空，不需輸入。")

    st.divider()

    st.subheader("其他資料")

    phone = st.text_input("電話")

    email = st.text_input("Email")

    st.divider()

    # -----------------------
    # 產生 Word
    # -----------------------

    if st.button("📄 產生 Word"):

        word_file = create_word_document(
                invoice_date=invoice_date,
                id_and_surname=id_and_surname,
                invoice_number=invoice_number,
                amount=amount,
                product_model=product_model,
                phone=phone,
                email=email,
                student_card_image_bytes=(
                    st.session_state.student_card_image_bytes
                ),
                student_card_back_image_bytes=(
                    st.session_state.student_card_back_image_bytes
                ),
            )
        date_parts = re.findall(r"\d+", invoice_date)

        if len(date_parts) == 3:
            year, month, day = map(int, date_parts)

            if year < 1911:
                year += 1911

            filename_date = f"{year:04d}{month:02d}{day:02d}"
        else:
            filename_date = re.sub(r"\D", "", invoice_date)

        filename = f"{invoice_number}_{filename_date}.docx"

        st.download_button(
            "⬇️ 下載 Word",
            data=word_file,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
