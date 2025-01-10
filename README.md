# BFSI- OCR of Bank Statements

![BFSI](./BFSI.png)

## Overview

The BFSI (Banking, Financial Services, and Insurance) OCR of Bank Statements project is a comprehensive system designed to automate the extraction, visualization, and analysis of financial document data. Using the **meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo** model, it processes various financial documents like bank statements, cheques, profit and loss statements, salary slips, and transaction histories. The goal is to simplify financial data extraction, deliver accurate results with minimal human intervention, and provide tools for better decision-making and analysis.

## Features

- **Multi-source Document Upload**: Support for both manual uploads and cloud-based retrieval via Cloudinary.
- **Advanced OCR Processing**: Utilizes **meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo** model for accurate text extraction.
- **Interactive Data Visualization**: Dynamic charts using Plotly.
- **Document Querying**: AI-powered chatbot interface for document-specific questions.
- **Data Export**: Option to download extracted financial data as CSV.

## Tech Stack

### Core Technologies

- Python 3.8+
- Streamlit (UI Framework)
- meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo model
- Cloudinary (Cloud Storage)
- Together API

### Key Libraries

- PyMuPDF (fitz): PDF processing
- Pandas: Data manipulation
- Plotly: Interactive visualizations
- Pillow: Image processing
- Regular Expressions (re): Data cleaning

## System Requirements

### Hardware Requirements

- CPU: 2.5 GHz or higher
- RAM: 8GB minimum
- Storage: 50GB available space

### Software Requirements

- Operating System: Windows, macOS, or Linux
- Python 3.8 or higher
- Web Browser: Chrome/Firefox (recommended)

## Installation and Setup

The complete final project is located in the **Milestone4** folder. Follow these steps to run the system:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/jasneet-arora27/BFSI--OCR-of-Bank-Statements.git
   cd BFSI--OCR-of-Bank-Statements/Milestone4
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required packages:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the Together API locally:**
   Ensure the **Together API** is set up and running locally. The system will interact with it for certain processing tasks.

5. **Configure Cloudinary:**

   - Create a `.env` file in the **Milestone4** folder and configure the following environment variables for Cloudinary:
     ```plaintext
     CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
     CLOUDINARY_API_KEY=your_cloudinary_api_key
     CLOUDINARY_API_SECRET=your_cloudinary_api_secret
     ```

6. **Start the application:**

   ```bash
   streamlit run main.py
   ```

7. **Access the web interface at** `http://localhost:8501`.

## Usage

1. **Select document processing mode:**

   - Upload new documents through the drag-and-drop interface.
   - Retrieve existing documents from Cloudinary storage.

2. **Choose document type:**

   - Bank Statements
   - Salary Slips
   - Profit & Loss Statements
   - Cheques
   - Transaction History

3. **View and analyze results:**
   - Examine extracted parameters in tabular format.
   - Choose visualization type (Bar/Pie chart).
   - Use the query interface to ask questions about the document.
   - Download extracted data as CSV.

## Flowchart

The project flowchart below visualizes the workflow of the system:

![Flowchart](./BFSI%20Flowchart.png)

## Contributing

1. Fork the repository.
2. Create your feature branch
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. Push to the branch
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request.

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

## Support

For support and queries, please open an issue in the GitHub repository.

---

Made with ❤️ by Jasneet Arora
