# src/file_processor.py

import re
import logging
import pdfplumber

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str, max_pages: int = 10) -> str:
    """
    从 PDF 文件中提取文本。
    """
    try:
        text = []
        with pdfplumber.open(pdf_path) as pdf:
            pages_to_read = min(len(pdf.pages), max_pages)
            for i, page in enumerate(pdf.pages[:pages_to_read]):
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
        
        full_text = "\n".join(text)
        cleaned_text = _clean_text(full_text)
        
        # 截断以符合模型上下文长度限制
        if len(cleaned_text) > 8000:
            cleaned_text = cleaned_text[:8000] + "\n[...Text Truncated...]"
            
        logger.debug(f"Extracted and cleaned {len(cleaned_text)} characters from '{pdf_path}'.")
        return cleaned_text
    except Exception as e:
        logger.error(f"Error reading PDF file '{pdf_path}': {e}")
        return ""

def _clean_text(text: str) -> str:
    """
    对提取的文本进行基本的清理。
    """
    if not text:
        return ""
    # 移除无效字符，保留基本ASCII和换行符
    text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
    # 规范化换行
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # 规范化空格
    text = re.sub(r' +', ' ', text)
    return text.strip()

def parse_llm_response(response_text: str) -> dict:
    """
    解析LLM返回的键值对格式的文本。
    """
    result = {}
    try:
        for line in response_text.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'is_relevant':
                    result[key] = value.lower() == 'true'
                elif key == 'confidence_score':
                    result[key] = float(value) if value else 0.0
                elif key in ['materials_identified', 'key_evidence', 'exclusion_reasons']:
                    result[key] = [v.strip() for v in value.split(',') if v.strip()]
                else:
                    result[key] = value

        # 确保所有期望的字段都存在
        expected_keys = ['is_relevant', 'confidence_score', 'primary_focus', 'recommendation', 'materials_identified', 'key_evidence', 'exclusion_reasons']
        for k in expected_keys:
            if k not in result:
                logger.warning(f"LLM response missing expected key: '{k}'")
                result[k] = '' # 提供一个默认值
        
        return result
    except Exception as e:
        logger.error(f"Failed to parse LLM response: {e}. Response: '{response_text[:200]}...'")
        return {'error': 'Failed to parse response', 'raw_response': response_text}