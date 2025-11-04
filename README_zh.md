# 学术文献智能筛选器 (Academic Literature Screener)

一个基于大语言模型（LLM）的命令行工具，用于自动筛选和分类学术论文。本工具旨在帮助科研人员根据特定标准快速过滤大量文献，从而显著节省文献综述阶段的时间。

该项目最初用于筛选**钠离子电池正极材料**领域的相关论文，但其核心提示（Prompt）和配置可以轻松修改，以适应任何研究领域。

## ✨ 功能特性

-   **批量处理**：自动分析指定文件夹中的所有 PDF 文件。
-   **LLM 驱动分析**：利用强大的大语言模型（可配置，如通义千问、OpenAI GPT 等）来“阅读”和分类论文。
-   **自定义筛选标准**：分析标准定义在外部的提示模板文件中，可以轻松修改以适应不同的研究主题。
-   **结构化输出**：为每篇论文生成一个清晰、易读的文本文件，包含详细的分类结果。
-   **并发处理**：支持多线程并发处理，加快大量文件的分析速度。
-   **稳健的错误处理**：包含 API 调用的自动重试机制和文件处理的容错能力。

## 📂 项目结构

```
/Academic_Literature_Screener/
├── src/                  # 源代码目录
├── prompts/              # Prompt 模板目录
├── .gitignore            # Git 忽略文件配置
├── config.example.json   # 配置文件示例
├── README.md             # 项目说明（英文版）
├── README_zh.md          # 项目说明（中文版）
├── requirements.txt      # Python 依赖项
└── run_screener.py       # 主执行脚本
```

## 🚀 快速开始

### 1. 安装

首先，请确保您的电脑已安装 Python 3.8 或更高版本。

**a. 克隆仓库**
```bash
git clone https://github.com/DTT-PRO/Academic_Literature_Screener.git
cd Academic_Literature_Screener
```

**b. 创建并激活虚拟环境 (推荐)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**c. 安装依赖**
```bash
pip install -r requirements.txt
```

### 2. 配置

**a. 创建配置文件**
将示例配置文件 `config.example.json` 复制一份，并重命名为 `config.json`。
```bash
cp config.example.json config.json
```

**b. 编辑 `config.json`**
用文本编辑器打开 `config.json` 并填入您的信息：
-   `"api_key"`: **(必需)** 您的大语言模型提供商的 API 密钥。
-   `"base_url"`: API 的基础 URL。
-   `"model_name"`: 您希望使用的具体模型名称。
-   `"pdf_folder"`: 存放待处理 PDF 文件的文件夹路径。请先创建此文件夹（例如，`mkdir papers`），然后将您的文献放入其中。
-   `"max_workers"`: 用于处理文件的并发线程数。建议初次使用时设置为 `1` 或 `2`，以避免超出 API 的速率限制。
-   其他设置可根据需要修改。

### 3. 运行

当您配置好 `config.json` 并将 PDF 文件放入指定文件夹后，在终端中运行以下命令即可启动筛选程序：
```bash
python run_screener.py
```

程序将开始处理文件，并显示一个进度条。处理完成后，摘要信息将打印在控制台，详细的分析结果会保存在您配置的 `output_file` 文件中（默认为 `screening_results.txt`）。

## 📜 许可证

本项目采用 MIT 许可证。