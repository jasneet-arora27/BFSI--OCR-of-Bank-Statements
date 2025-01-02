import streamlit as st
import os
import base64
import re
import pandas as pd
import fitz
from PIL import Image
from together import Together

class DocumentProcessor:
    def __init__(self):
        self.model = "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo"
        self.client = Together(api_key=st.secrets["together"]["TOGETHER_API_KEY"])

    def encode_image(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                return encoded_image
        except FileNotFoundError:
            st.error(f"Image not found: {image_path}")
            return None
        except Exception as e:
            st.error(f"Error encoding image: {e}")
            return None

    def extract_parameters(self, image_path, document_type):
        
        # Validate image path
        if not os.path.exists(image_path):
            st.error(f"Image path does not exist: {image_path}")
            return None, "Image file not found"

        encoded_image = self.encode_image(image_path)
        
        if not encoded_image:
            st.error("Image could not be encoded")
            return None, "Image encoding failed"
        
        prompts = {
            "Bank Statement": """Analyze this financial document carefully. Extract the most significant numeric financial parameters:
            - Look for balance, credits, debits, and other key monetary values.
            - Be flexible in parameter identification.
            - Return ONLY 5 numeric values with clear labels, one per line.   
            
            The output format should be:
            Total Balance: 5000.50
            Monthly Credits: 3200.75
            Monthly Debits: 2800.25
            Opening Balance: 4500.00
            Closing Balance: 5200.75
            Do not include any statements or additional text.""",
            
            "Cheques": """Extract key details from the cheque:
            - Focus on numeric values.
            - Include cheque number, amount, date, and account details.
            - Provide ONLY 5 clear, labeled values, one per line.
            
            The output format should be:
            Cheque Number: 123456
            Amount: 5000.00
            Date Timestamp: 1701907200
            Bank Account: 9876
            Transaction Value: 5000.00
            Do not include any statements or additional text.""",
            
            "Profit and Loss Statement": """Extract critical financial metrics from the Profit and Loss statement:
            - Total Revenue
            - Total Expenses
            - Gross Profit
            - Net Profit
            - Operating Expenses
            Return ONLY 5 clear, labeled numeric values, one per line.
            
            The output format should be:
            Total Revenue: 100000.00
            Total Expenses: 75000.00
            Gross Profit: 25000.00
            Net Profit: 20000.00
            Operating Expenses: 5000.00
            Do not include any statements or additional text.""",
            
            "Salary Slip": """Extract key salary details from the salary slip:
            - Basic Salary
            - Total Allowances
            - Total Deductions
            - Net Salary
            - Gross Salary
            Return ONLY 5 clear, labeled numeric values, one per line.
            
            The output format should be:
            Basic Salary: 30000.00
            Total Allowances: 5000.00
            Total Deductions: 2000.00
            Net Salary: 27000.00
            Gross Salary: 32000.00
            Do not include any statements or additional text.""",

            "Transaction History": """Extract summary transaction metrics from the transaction history:
            - Total Number of Transactions
            - Total Credits
            - Total Debits
            - Highest Single Transaction Amount
            - Average Transaction Amount
            Return ONLY 5 clear, labeled numeric values, one per line.
            
            The output format should be:
            Total Number of Transactions: 150
            Total Credits: 50000.00
            Total Debits: 30000.00
            Highest Single Transaction Amount: 10000.00
            Average Transaction Amount: 400.00
            Do not include any statements or additional text."""

        }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompts.get(document_type, "")},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                        ]
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            extracted_text = response.choices[0].message.content.strip()
            
            # Robust parameter extraction
            parameters = []
            for line in extracted_text.split('\n'):
                parts = line.split(":", 1)
                if len(parts) == 2:
                    try:
                        parameter = parts[0].strip().strip('*')
                        value_str = parts[1].strip()
                        
                        # More robust number cleaning
                        cleaned_value_str = re.sub(r"[^\d,-.]", "", value_str)
                        cleaned_value_str = cleaned_value_str.replace(',', '')  # Remove commas
                        
                        # Handle potential scientific notation or large numbers
                        try:
                            value = float(cleaned_value_str)
                        except ValueError:
                            value = cleaned_value_str
                        
                        parameters.append([parameter, value])
                        
                    except Exception as parse_error:
                        print(f"Error parsing parameter: {parse_error}")
            
            if not parameters:
                st.warning(f"No parameters found in text: {extracted_text}")
                return None, extracted_text
            
            df = pd.DataFrame(parameters, columns=['Parameter', 'Value'])
            return df, extracted_text

        except Exception as e:
            st.error(f"Comprehensive Extraction Error: {e}")
            import traceback
            return None, str(e)