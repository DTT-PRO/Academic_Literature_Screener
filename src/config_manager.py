# src/config_manager.py

import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "api_provider": "qwen",
    "api_key": "YOUR_API_KEY_HERE",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "model_name": "qwen-vl-max",
    "pdf_folder": "./papers",
    "output_file": "screening_results.txt",
    "max_workers": 1,
    "max_pages_per_pdf": 10,
    "prompt_template_file": "./prompts/analysis_prompt_template.txt"
}

def load_config(config_path: str = "config.json") -> dict:
    """
    加载配置文件。如果文件不存在，则从示例创建。
    """
    if not os.path.exists(config_path):
        logger.warning(f"Config file '{config_path}' not found. Creating from example.")
        print(f"Warning: '{config_path}' not found. Please create it based on 'config.example.json'.")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        user_config = json.load(f)

    # 用默认值填充缺失的键
    config = DEFAULT_CONFIG.copy()
    config.update(user_config)
    
    logger.info(f"Configuration loaded from '{config_path}'.")
    return config

def validate_config(config: dict) -> list:
    """
    验证配置的有效性。
    """
    errors = []
    
    # 检查 API 密钥
    api_key = config.get('api_key')
    env_key = os.getenv('DASHSCOPE_API_KEY') # 示例，可根据实际API调整
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        if not env_key:
             errors.append("API key is not set. Please set 'api_key' in config.json or as an environment variable.")

    # 检查 PDF 文件夹
    pdf_folder = config.get('pdf_folder')
    if not os.path.isdir(pdf_folder):
        errors.append(f"PDF folder '{pdf_folder}' does not exist.")
    else:
        pdf_count = len(list(Path(pdf_folder).glob("*.pdf")))
        if pdf_count == 0:
            errors.append(f"No PDF files found in '{pdf_folder}'.")
        else:
            logger.info(f"Found {pdf_count} PDF file(s) in '{pdf_folder}'.")

    # 检查 Prompt 模板文件
    if not os.path.exists(config.get('prompt_template_file')):
        errors.append(f"Prompt template file '{config.get('prompt_template_file')}' not found.")
        
    return errors