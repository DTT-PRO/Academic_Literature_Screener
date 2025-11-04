# run_screener.py

import argparse
import logging
from src.config_manager import load_config, validate_config
from src.main_processor import LiteratureScreener

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('literature_screener.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主执行函数，用于启动文献筛选流程。"""
    parser = argparse.ArgumentParser(
        description="A tool for screening academic literature using Large Language Models.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to the configuration file (default: config.json)'
    )
    args = parser.parse_args()

    print("=" * 70)
    print("      Academic Literature Screening Tool")
    print("      Powered by Large Language Models")
    print("=" * 70 + "\n")

    try:
        # 1. 加载配置
        config = load_config(args.config)

        # 2. 验证配置
        errors = validate_config(config)
        if errors:
            for error in errors:
                logger.error(error)
            print("\nConfiguration validation failed. Please check the log and your config file.")
            return

        logger.info("Configuration loaded and validated successfully.")
        
        # 3. 初始化并运行筛选器
        screener = LiteratureScreener(config)
        screener.run()

        logger.info("Screening process completed successfully.")

    except FileNotFoundError:
        logger.error(f"Configuration file not found at '{args.config}'.")
        print(f"\nError: Configuration file '{args.config}' not found.")
        print("Please ensure 'config.json' exists or use 'config.example.json' as a template.")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        print(f"\nAn unexpected error occurred. See 'literature_screener.log' for details.")


if __name__ == "__main__":
    main()