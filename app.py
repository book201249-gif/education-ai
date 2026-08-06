import re

import streamlit as st

from ai.gemini import read_invoice, read_student_card
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


# -----------------------
# 上傳圖片
# -----------------------

student_card = st.file_uploader(
    "📷 上傳學生證",
    type=["jpg", "jpeg", "png"],
)

invoice = st.file_uploader(
    "🧾 上傳發票",
    type=["jpg", "jpeg", "png"],
)

col1, col2 = st.columns(2)

with col1:
    if student_card:
        st.image(student_card, caption="學生證", use_container_width=True)

with col2:
    if invoice:
        st.image(invoice, caption="發票", use_container_width=True)


# -----------------------
# Gemini 辨識
# -----------------------

if st.button("🤖 開始辨識", type="primary"):

    if student_card is None:
        st.error("請先上傳學生證")

    elif invoice is None:
        st.error("請先上傳發票")

    else:

        with st.spinner("Gemini 正在辨識..."):

            st.session_state.student_result = read_student_card(
                student_card.getvalue(),
                student_card.type,
            )

            st.session_state.invoice_result = read_invoice(
                invoice.getvalue(),
                invoice.type,
            )

            # ★ 改成保存學生證圖片
            st.session_state.student_card_image_bytes = student_card.getvalue()

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

            # ★ 改成學生證
            student_card_image_bytes=st.session_state.student_card_image_bytes,
        )

        filename = f"{invoice_number}_{invoice_date}.docx"
        st.download_button(
            "⬇️ 下載 Word",
            data=word_file,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )