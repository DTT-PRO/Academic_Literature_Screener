# src/main_processor.py

import os
import time
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from .api_client import APIClient
from .file_processor import extract_text_from_pdf, parse_llm_response

logger = logging.getLogger(__name__)

class LiteratureScreener:
    """
    编排整个文献筛选流程。
    """
    def __init__(self, config: dict):
        self.config = config
        self.api_client = APIClient(
            provider=config['api_provider'],
            api_key=config['api_key'],
            base_url=config['base_url'],
            model=config['model_name']
        )
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """从文件加载 Prompt 模板。"""
        try:
            with open(self.config['prompt_template_file'], 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error(f"Prompt template file not found at: {self.config['prompt_template_file']}")
            raise
        except Exception as e:
            logger.error(f"Error reading prompt template file: {e}")
            raise

    def process_single_file(self, pdf_path: Path) -> dict:
        """处理单个PDF文件。"""
        start_time = time.time()
        file_name = pdf_path.name
        
        base_result = {
            "file_name": file_name,
            "file_path": str(pdf_path),
            "timestamp": datetime.now().isoformat(),
        }

        try:
            logger.info(f"Processing: {file_name}")
            
            # 1. 提取文本
            paper_text = extract_text_from_pdf(str(pdf_path), self.config['max_pages_per_pdf'])
            if not paper_text or len(paper_text.strip()) < 200:
                logger.warning(f"Text extraction failed or text too short for '{file_name}'.")
                return {**base_result, "status": "ERROR", "details": "Text extraction failed or content is too short."}

            # 2. 构建 Prompt
            prompt = self.prompt_template.format(paper_text=paper_text)
            
            # 3. 调用 API
            logger.info(f"Sending '{file_name}' to API for analysis...")
            llm_response = self.api_client.get_completion(prompt)
            
            # 4. 解析结果
            analysis = parse_llm_response(llm_response)
            if 'error' in analysis:
                return {**base_result, "status": "ERROR", "details": analysis['error']}

            return {
                **base_result,
                "status": "PROCESSED",
                "analysis": analysis,
                "processing_time_seconds": round(time.time() - start_time, 2)
            }

        except Exception as e:
            logger.error(f"An error occurred while processing '{file_name}': {e}", exc_info=True)
            return {
                **base_result,
                "status": "ERROR",
                "details": str(e),
                "processing_time_seconds": round(time.time() - start_time, 2)
            }

    def run(self):
        """执行批量处理并保存结果。"""
        pdf_files = list(Path(self.config['pdf_folder']).glob("*.pdf"))
        if not pdf_files:
            print("No PDF files to process. Exiting.")
            return

        results = []
        max_workers = self.config.get('max_workers', 1)
        
        print(f"\nStarting batch processing of {len(pdf_files)} files with {max_workers} worker(s)...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_pdf = {executor.submit(self.process_single_file, pdf): pdf for pdf in pdf_files}
            
            for future in tqdm(as_completed(future_to_pdf), total=len(pdf_files), desc="Screening Papers"):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    pdf_path = future_to_pdf[future]
                    logger.error(f"A future task for '{pdf_path.name}' failed unexpectedly: {e}")
                    results.append({
                        "file_name": pdf_path.name,
                        "file_path": str(pdf_path),
                        "timestamp": datetime.now().isoformat(),
                        "status": "FATAL_ERROR",
                        "details": f"Task execution failed: {e}"
                    })

        self._save_results(results)
        self._print_summary(results)

    def _save_results(self, results: list):
        """将处理结果保存到文本文件。"""
        output_file = self.config['output_file']
        with open(output_file, 'w', encoding='utf-8') as f:
            for res in sorted(results, key=lambda x: x['file_name']):
                f.write(f"--- Result for: {res['file_name']} ---\n")
                f.write(f"Status: {res['status']}\n")
                if res['status'] == 'PROCESSED':
                    analysis = res.get('analysis', {})
                    f.write(f"Recommendation: {analysis.get('recommendation', 'N/A')}\n")
                    f.write(f"Is Relevant: {analysis.get('is_relevant', 'N/A')}\n")
                    f.write(f"Confidence: {analysis.get('confidence_score', 'N/A')}\n")
                    f.write(f"Primary Focus: {analysis.get('primary_focus', 'N/A')}\n")
                    f.write(f"Materials Identified: {', '.join(analysis.get('materials_identified', []))}\n")
                    f.write(f"Key Evidence: {', '.join(analysis.get('key_evidence', []))}\n")
                    f.write(f"Exclusion Reasons: {', '.join(analysis.get('exclusion_reasons', []))}\n")
                else:
                    f.write(f"Details: {res['details']}\n")
                f.write(f"Processing Time: {res.get('processing_time_seconds', 'N/A')}s\n")
                f.write("\n")
        logger.info(f"All results saved to '{output_file}'.")
        print(f"\n✅ Results have been saved to '{output_file}'.")

    def _print_summary(self, results: list):
        """打印处理结果的摘要。"""
        total = len(results)
        processed = sum(1 for r in results if r['status'] == 'PROCESSED')
        errors = total - processed
        
        recommendations = {
            "KEEP": 0,
            "REVIEW": 0,
            "EXCLUDE": 0,
            "N/A": 0
        }
        if processed > 0:
            for r in results:
                if r['status'] == 'PROCESSED':
                    rec = r.get('analysis', {}).get('recommendation', 'N/A')
                    recommendations[rec] = recommendations.get(rec, 0) + 1
        
        print("\n--- Processing Summary ---")
        print(f"Total files processed: {total}")
        print(f"  - Successfully analyzed: {processed}")
        print(f"  - Errors: {errors}")
        if processed > 0:
            print("\n--- Recommendation Summary ---")
            print(f"  👍 Keep:    {recommendations['KEEP']}")
            print(f"  🤔 Review:  {recommendations['REVIEW']}")
            print(f"  👎 Exclude: {recommendations['EXCLUDE']}")
        print("--------------------------")