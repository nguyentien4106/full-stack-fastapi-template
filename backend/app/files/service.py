from app.core.config import settings
import io
import uuid
from io import StringIO
from urllib.parse import quote

import pandas as pd
from google import genai
from pandas.core.frame import DataFrame
from sqlmodel import Session

from app.aws.client import generate_presigned_put_url
from app.aws.config import aws_settings
from app.backend_pre_start import logger
from app.files.dependencies import CurrentUser
from app.files.models import File
from app.files.schemas import FileCreate
from app.files.utils import get_df_from_result_json


def create_file(*, session: Session, file_in: FileCreate, user_id: uuid.UUID) -> File:
    db_file = File.model_validate(file_in, update={"user_id": user_id})
    session.add(db_file)
    session.commit()
    session.refresh(db_file)
    return db_file

def delete_file(*, session: Session, file_id: uuid.UUID) -> None:
    db_file = session.get(File, file_id)
    if db_file:
        session.delete(db_file)
        session.commit()

def update_file_info(
    session: Session, file_id: uuid.UUID, job_status: str, job_id: str | None = None, err_msg : str | None = None
) -> File | None:
    db_file: File | None = session.get(File, file_id)
    if db_file:
        db_file.job_status = job_status
        if job_id:
            db_file.job_id = job_id
        if err_msg:
            db_file.err_msg = err_msg
        session.add(db_file)
        session.commit()
        session.refresh(db_file)
        return db_file
    return None

def download_file(file: File, user: CurrentUser, type: str = "excel") -> tuple[bytes, str]:
    """
    Given a File record, download the file content from its URL and return bytes
    and a Content-Disposition header for the requested format.

    Supported types: "excel", "csv", "json", "html".
    """
    json_key = f"{user.email}/{file.id}/result.json"
    presigned_url = generate_presigned_put_url(key=json_key, bucket=aws_settings.R2_BUCKET_NAME, expiration=3600)

    df: DataFrame = get_df_from_result_json(presigned_url)

    safe_name = file.filename.rsplit(".", 1)[0] if "." in file.filename else file.filename

    if type == "xlsx":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:  # type: ignore[abstract]  # ty:ignore[invalid-argument-type]
            df.to_excel(writer, index=False, sheet_name="OCR Tables")
        data_bytes = output.getvalue()
        filename = f"{safe_name}_tables.xlsx"
    elif type == "csv":
        output = StringIO()
        df.to_csv(output, index=False)
        data_bytes = output.getvalue().encode("utf-8")
        filename = f"{safe_name}_tables.csv"
    elif type == "json":
        text = df.to_json(orient="records", force_ascii=False) or ""
        data_bytes = text.encode("utf-8")
        filename = f"{safe_name}_tables.json"
    elif type == "html":
        text = df.to_html(index=False) or ""
        data_bytes = text.encode("utf-8")
        filename = f"{safe_name}_tables.html"
    else:
        raise ValueError(f"Unsupported file type requested: {type}")

    # RFC 5987: percent-encode the UTF-8 filename for the filename* parameter
    encoded_filename = quote(filename, safe="")
    logger.info(f"Generated filename: {filename}, encoded filename: {encoded_filename}")
    content_disposition = (
        f"attachment; filename=\"{filename}\"; "
        f"filename*=UTF-8''{encoded_filename}"
    )

    return (data_bytes, content_disposition)



def get_gemini_response_for_file(input_path: str, output_path: str, *, model: str | None = None) -> None:
    """Read a local file (CSV or XLSX), send its contents to Gemini with the Vietnamese
    prompt, and write the model's returned contents into `output_path` as XLSX when
    the output filename ends with .xlsx.

    Behavior:
    - If input is .xlsx or .xls, read with pandas and convert to CSV text for the prompt.
    - Otherwise, read the file as text and include it verbatim.
    - The prompt explicitly asks Gemini to return only the new file contents (CSV/plain text).
    - If the output is requested as .xlsx, the function will attempt to parse the model's
      CSV/plain-text response back into a DataFrame and write it to Excel.
      If parsing fails, the raw response will be put into a single-cell Excel sheet.

    Prompt used (Vietnamese):
    "Tôi muốn bạn đọc file này. Sau đó dựa vào nội dung trong cột thứ 2 để xác định giao dịch này thuộc mã tài khoản kế toán nào (mã này được lấy từ thị trường Việt Nam). Sau đó trả ra cho tôi file mới có thêm cột mã tk, và tên tk ở cuối"

    Note: The GEMINI_API_KEY must be set in the environment for `genai.Client()` to authenticate.
    """
    client = genai.Client(api_key=settings.GMN_API_KEY)

    if model is None:
        model = "gemini-3-flash-preview"

    # Load input file. If Excel, convert to CSV text to include in the prompt.
    file_ext = input_path.lower().rsplit('.', 1)[-1] if '.' in input_path else ''
    if file_ext in ("xlsx", "xls"):
        df_in = pd.read_excel(input_path)
        file_text = df_in.to_csv(index=False)
    else:
        # For non-excel files, read as text
        with open(input_path, encoding="utf-8") as f:
            file_text = f.read()

    # Build prompt that asks the model to return only the file contents (CSV/plain text)
    user_instruction = (
        "Tôi muốn bạn đọc file này. Sau đó dựa vào nội dung trong cột thứ 2 để xác định giao dịch "
        "này thuộc mã tài khoản kế toán nào (mã này được lấy từ thị trường Việt Nam). Sau đó trả ra "
        "cho tôi file mới có thêm cột mã tk, và tên tk ở cuối.\n\n"
        "Dưới đây là nội dung file (nguyên văn). Hãy trả lại CHÍNH XÁC NỘI DUNG file mới dưới dạng CSV hoặc plain text, "
        "không thêm giải thích, chú thích hay văn bản khác. Chỉ output nội dung file mới.\n\n"
    )

    full_prompt = user_instruction + "---FILE-BEGIN---\n" + file_text + "\n---FILE-END---\n"

    # Send to Gemini
    response = client.models.generate_content(model=model, contents=full_prompt)
    resp_text = response.text or ""

    # If output path requests xlsx, try to parse response as CSV/plain text and write to Excel
    out_ext = output_path.lower().rsplit('.', 1)[-1] if '.' in output_path else ''
    if out_ext in ("xlsx", "xls"):
        try:
            df_out = pd.read_csv(StringIO(resp_text))
            df_out.to_excel(output_path, index=False, engine='openpyxl')
        except Exception:
            # Fallback: write the raw response into a single-cell sheet
            fallback_df = pd.DataFrame({"result": [resp_text]})
            fallback_df.to_excel(output_path, index=False, engine='openpyxl')
    else:
        # For non-xlsx output, write raw text
        with open(output_path, "w", encoding="utf-8") as out_f:
            out_f.write(resp_text)
