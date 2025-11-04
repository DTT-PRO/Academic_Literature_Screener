# src/api_client.py

import os
import time
import logging
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class APIClient:
    """
    用于与大语言模型 API 进行交互的客户端。
    """
    def __init__(self, provider: str, api_key: str, base_url: str, model: str):
        self.provider = provider
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY") # 示例环境变量
        self.base_url = base_url
        self.model = model
        self.client = self._initialize_client()
        logger.info(f"API client initialized for provider: {self.provider}, model: {self.model}")

    def _initialize_client(self):
        """初始化 OpenAI 兼容的 API 客户端。"""
        try:
            return OpenAI(api_key=self.api_key, base_url=self.base_url)
        except Exception as e:
            logger.error(f"Failed to initialize API client: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_completion(self, prompt: str, max_tokens: int = 1500) -> str:
        """
        调用 LLM API 获取响应，并实现重试机制。
        """
        try:
            time.sleep(1) # 简单的速率限制
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a highly specialized academic paper analysis assistant. Follow user instructions precisely and only return text in the specified format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.0,
            )
            content = response.choices[0].message.content
            logger.debug(f"API call successful. Response received.")
            return content
        except Exception as e:
            logger.error(f"API call failed after retries: {e}")
            raise