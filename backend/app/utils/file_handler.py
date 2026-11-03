"""DOCX/PDF 合同文本提取工具。"""

from pathlib import Path

from docx import Document as WordDocument
from PyPDF2 import PdfReader


class FileParseError(ValueError):
    """文件格式正确但解析失败时抛出的可预期异常。"""


def _extract_docx(path: Path) -> str:
    """提取 Word 段落和表格中的纯文本。"""
    try:
        document = WordDocument(str(path))
        parts = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        for table in document.tables:
            for row in table.rows:
                cells = [cell.text.strip() for cell in row.cells]
                if any(cells):
                    parts.append(" | ".join(cells))
        return "\n".join(parts).strip()
    except Exception as exc:  # 第三方解析器异常需转成统一业务错误。
        raise FileParseError(f"DOCX 文件解析失败：{exc}") from exc


def _extract_pdf(path: Path) -> str:
    """提取 PDF 每一页的文本；扫描版 PDF 可能返回空文本。"""
    try:
        reader = PdfReader(str(path))
        pages: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text.strip())
        return "\n\n".join(pages).strip()
    except Exception as exc:
        raise FileParseError(f"PDF 文件解析失败：{exc}") from exc


def extract_text(file_path: str | Path) -> str:
    """按扩展名读取 DOCX 或 PDF，并返回纯文本。"""
    path = Path(file_path)
    if not path.is_file():
        raise FileParseError("文件不存在或不可读取")

    suffix = path.suffix.lower()
    if suffix == ".docx":
        text = _extract_docx(path)
    elif suffix == ".pdf":
        text = _extract_pdf(path)
    else:
        raise FileParseError("仅支持 .docx 和 .pdf 文件")

    if not text:
        raise FileParseError("未能从文件中提取文本；扫描版 PDF 可能需要 OCR")
    return text
