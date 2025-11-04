# Academic Literature Screener

A command-line tool designed to automatically screen and classify academic papers using Large Language Models (LLMs). This tool helps researchers quickly filter large volumes of literature based on specific criteria, saving significant time in the literature review process.

This project was initially developed to screen papers on **sodium-ion battery cathode materials**, but its prompt and configuration can be easily adapted for any research field.

## Features

-   **Batch Processing**: Analyzes all PDF files in a specified folder.
-   **LLM-Powered Analysis**: Leverages powerful LLMs (configurable, e.g., OpenAI, Qwen) to "read" and classify papers.
-   **Customizable Criteria**: The analysis criteria are defined in an external prompt template, allowing easy adaptation to different research topics.
-   **Structured Output**: Generates a clean, readable text file with the classification results for each paper.
-   **Concurrent Processing**: Supports multi-threaded processing to speed up the analysis of many files.
-   **Robust Error Handling**: Includes retries for API calls and graceful handling of file processing errors.

## Project Structure

```
/Academic_Literature_Screener/
├── src/                  # Source code
├── prompts/              # Prompt templates
├── .gitignore
├── config.example.json   # Example configuration
├── README.md
├── requirements.txt
└── run_screener.py       # Main execution script
```

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/DTT-PRO/Academic_Literature_Screener.git
    cd Academic_Literature_Screener
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate
    
    # For macOS / Linux
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  **Create your configuration file:**
    Copy the example configuration file:
    ```bash
    cp config.example.json config.json
    ```

2.  **Edit `config.json`:**
    -   `api_key`: **(Required)** Your API key for the LLM provider.
    -   `base_url`: The API endpoint URL for your provider.
    -   `model_name`: The specific model you want to use.
    -   `pdf_folder`: The path to the folder containing your PDF files. Create this folder (e.g., `mkdir papers`) and place your literature inside.
    -   `max_workers`: The number of concurrent threads to use for processing. Start with 1 or 2 to avoid rate-limiting issues.
    -   ... and other settings as needed.

3.  **Customize the Prompt (Optional):**
    If you want to screen for a different topic, edit `prompts/analysis_prompt_template.txt`. Modify the `Analysis Topic`, `Key Areas of Interest`, and `Exclusion Criteria` sections to match your needs.

## Usage

Once you have configured `config.json` and placed your PDF files in the designated folder, run the screener from your terminal:

```bash
python run_screener.py
```

The script will start processing the files, and a progress bar will be displayed. Upon completion, a summary will be printed to the console, and detailed results will be saved to the file specified by `output_file` in your configuration (e.g., `screening_results.txt`).

## How It Works

1.  **Initialization**: The script loads configurations and validates them.
2.  **File Discovery**: It scans the `pdf_folder` for all `.pdf` files.
3.  **Processing Queue**: It creates a processing job for each PDF.
4.  **For each PDF**:
    -   The text from the first few pages is extracted.
    -   A specific prompt is constructed using the template from `prompts/` and the extracted text.
    -   The prompt is sent to the configured LLM API.
    -   The LLM's structured response is parsed.
5.  **Result Aggregation**: All results are collected and saved into a single, well-formatted output file.

## License

This project is licensed under the MIT License.