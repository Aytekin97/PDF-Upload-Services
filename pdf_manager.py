from loguru import logger
from schemas import TablesSchema
from typing import List

import pdfplumber

class PdfManager:
    def extract(self, client, corpus, schema, agent):

        # Extract data from pdf
        logger.info("Extracting data")
        try:
            logger.info("Prompting ChatGPT")
            prompt = agent.prompt(corpus)
            extracted_data = client.query_gpt(prompt, schema)
            logger.success("Response received from ChatGPT")

            return extracted_data
                
        except Exception as e:
            logger.error(f"An error occured while querying ChatGPT: {e}")

    # Format tables into 
    def format_table_for_embedding(self, tables_schema: TablesSchema) -> List[str]:
        # Convert table schema to text
        formatted_tables = []

        for table in tables_schema.tables:
            formatted_table = f"Table: {table.table_name}\n"

            # Add column names
            formatted_table += f"Columns: {', '.join(table.columns)}\n"

            # Add rows in table format
            for row in table.rows:
                formatted_table += f"Row: {', '.join(row)}\n"
            
            formatted_tables.append(formatted_table)
        
        return formatted_tables
    
    # Extract text using pdfplumber
    def pdf_reader(self):

        # File path
        pdf_file_name = "documents\TSLA-Q1-2024-Update.pdf"

        logger.info(f"Starting to read: {pdf_file_name}")
        with pdfplumber.open(pdf_file_name) as pdf:
            extracted_text = ""
            for page in pdf.pages:
                extracted_text += page.extract_text() + "\n"   
        logger.success(f"Text extracted. Length = {len(extracted_text)}")

        return extracted_text