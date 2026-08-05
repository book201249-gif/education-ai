import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("找不到 GOOGLE_API_KEY，請確認 .env 是否正確。")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"


def clean_json_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json").removesuffix("```").strip()
    elif text.startswith("```"):
        text = text.removeprefix("```").removesuffix("```").strip()

    return text


def read_student_card(image_bytes: bytes, mime_type: str) -> dict:
    prompt = """
你是一個學生證資料辨識助手。

請辨識這張學生證，只擷取以下資料：
1. student_id：學號或證號
2. full_name：完整姓名
3. surname：姓氏

規則：
- 中文姓名通常取第一個字為姓氏。
- 英文姓名請依版面與常見格式判斷姓氏。
- 無法確定的欄位請填空字串。
- 不要猜測不存在的資料。
- 只輸出 JSON，不要加入說明文字。

輸出格式：
{
  "student_id": "",
  "full_name": "",
  "surname": ""
}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
            prompt,
        ],
    )

    text = clean_json_text(response.text)

    return json.loads(text)


def read_invoice(image_bytes: bytes, mime_type: str) -> dict:
    prompt = """
你是一個台灣統一發票與商品資料辨識助手。

請辨識圖片中的發票資料，只擷取以下欄位：

1. invoice_date：發票日期
2. invoice_number：發票號碼
3. amount：發票總金額，只保留數字
4. product_model：商品型號
{
  "invoice_date": "",
  "invoice_number": "",
  "amount": "",
  "product_model": ""
}

辨識規則：
- 發票日期請使用民國格式，例如 115.07.23。
- 發票號碼通常是兩個英文字母加八位數字。
- 金額只輸出數字，不要逗號、元或貨幣符號。
- 商品型號需保留英文、數字、斜線及連字號。
- 無法確定的欄位請填空字串。
- 不可自行猜測圖片中不存在的資料。
- 只輸出 JSON，不要加入解釋或 Markdown。

輸出格式：
{
  "invoice_date": "",
  "invoice_number": "",
  "amount": "",
  "product_model": "",
}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
            prompt,
        ],
    )

    text = clean_json_text(response.text)

    return json.loads(text)