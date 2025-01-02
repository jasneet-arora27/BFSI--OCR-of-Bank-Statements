import streamlit as st
import os
import io
import tempfile
import fitz
from PIL import Image
import pandas as pd
import base64
import requests
import cloudinary
import cloudinary.api
from dotenv import load_dotenv
import random
import zipfile
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from document_processor import DocumentProcessor
from visualizations import visualize_comparative_data, process_comparative_data,create_interactive_pie_chart

# Initialize session state
if 'processed_dfs' not in st.session_state:
    st.session_state.processed_dfs = []
if 'temp_image_paths' not in st.session_state:
    st.session_state.temp_image_paths = []
if 'processing_errors' not in st.session_state:
    st.session_state.processing_errors = []
if 'cloudinary_images' not in st.session_state:
    st.session_state.cloudinary_images = []

# Load environment variables and configure Cloudinary
load_dotenv()
cloudinary.config(
    cloud_name=st.secrets["cloudinary"]["CLOUDINARY_CLOUD_NAME"],
    api_key=st.secrets["cloudinary"]["CLOUDINARY_API_KEY"],
    api_secret=st.secrets["cloudinary"]["CLOUDINARY_API_SECRET"]
)

def create_requests_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def download_image(url, session=None):
    if session is None:
        session = requests.Session()
    try:
        response = session.get(url, timeout=(10, 30))
        return response.content if response.status_code == 200 else None
    except requests.exceptions.RequestException:
        return None

def fetch_images(folder_name, subfolder, num_images):
    session = create_requests_session()
    try:
        full_path = f"{folder_name}/{subfolder}"
        resources = cloudinary.api.resources(
            type="upload",
            prefix=full_path,
            max_results=500
        )
        
        if not resources.get('resources'):
            st.error(f"No images found in {subfolder}")
            return []
        
        all_resources = resources['resources']
        random.shuffle(all_resources)
        
        images = []
        for resource in all_resources[:int(num_images)]:
            image_url = resource['secure_url']
            image_content = download_image(image_url, session)
            
            if image_content:
                images.append({
                    'content': image_content,
                    'url': image_url,
                    'name': os.path.basename(resource['public_id']) + '.jpg'
                })
        return images
    except Exception as e:
        st.error(f"Error fetching images: {str(e)}")
        return []

def create_zip_file(images):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for idx, image in enumerate(images):
            zip_file.writestr(image['name'], image['content'])
    return zip_buffer.getvalue()

def process_uploaded_files(uploaded_files, processor, selected_doc_type):
    if not st.session_state.processed_dfs:  # Only process if not already processed
        for uploaded_file in uploaded_files:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_path = temp_file.name

                if os.path.splitext(uploaded_file.name)[1].lower() == ".pdf":
                    with fitz.open(stream=uploaded_file.getvalue(), filetype="pdf") as doc:
                        page = doc[0]
                        pix = page.get_pixmap()
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        temp_image_path = f"{temp_path}_page_0.png"
                        img.save(temp_image_path)
                        st.session_state.temp_image_paths.append(temp_image_path)
                else:
                    st.session_state.temp_image_paths.append(temp_path)

                df, _ = processor.extract_parameters(st.session_state.temp_image_paths[-1], selected_doc_type)

                if df is not None and all(col in df.columns for col in ["Parameter", "Value"]):
                    df["Document"] = uploaded_file.name if len(uploaded_files) > 1 else "Default Document"
                    st.session_state.processed_dfs.append(df)
                else:
                    st.session_state.processing_errors.append(f"Invalid DataFrame format for {uploaded_file.name}")

            except Exception as e:
                st.session_state.processing_errors.append(f"Error processing {uploaded_file.name}: {str(e)}")

def main():
    st.set_page_config(page_title="Financial Document Analyzer", layout="wide")

    with st.sidebar:
        st.title("Financial Document Analyzer")
        document_types = {
            "Bank Statement": "bank_statements",
            "Cheques": "cheques",
            "Profit and Loss Statement": "profit_loss_statements",
            "Salary Slip": "salary_slips",
            "Transaction History": "transaction_history",
        }
        selected_doc_type = st.selectbox("Select Document Type", list(document_types.keys()))

        graph_types = ["Bar Chart", "Pie Chart"]
        data_source = st.radio("Select Data Source", ["Fetch from Cloudinary", "Upload Files"])
        selected_graph_type = st.selectbox("Select Graph Type", graph_types)
        
        if st.button("Clear All Data"):
            st.session_state.processed_dfs = []
            st.session_state.temp_image_paths = []
            st.session_state.processing_errors = []
            st.session_state.cloudinary_images = []
            st.rerun()

    st.header(f"{selected_doc_type} Analysis")
    processor = DocumentProcessor()

    # Cloudinary Section
    if data_source == "Fetch from Cloudinary":
        num_images = st.number_input("Number of images to fetch", min_value=1, max_value=100, value=5)
        
        if st.button("Fetch Images") and not st.session_state.cloudinary_images:
            with st.spinner("Fetching images from Cloudinary..."):
                st.session_state.cloudinary_images = fetch_images(
                    "financial_data",
                    document_types[selected_doc_type],
                    num_images
                )
                
                if st.session_state.cloudinary_images:
                    for image_data in st.session_state.cloudinary_images:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                            temp_file.write(image_data['content'])
                            st.session_state.temp_image_paths.append(temp_file.name)
                            
                            df, _ = processor.extract_parameters(temp_file.name, selected_doc_type)
                            if df is not None and all(col in df.columns for col in ["Parameter", "Value"]):
                                df["Document"] = image_data['name']
                                st.session_state.processed_dfs.append(df) 
        
        if st.session_state.cloudinary_images:
            cols = 3
            rows = -(-len(st.session_state.cloudinary_images) // cols)
            for row in range(rows):
                columns = st.columns(cols)
                for col in range(cols):
                    idx = row * cols + col
                    if idx < len(st.session_state.cloudinary_images):
                        with columns[col]:
                            image = Image.open(io.BytesIO(st.session_state.cloudinary_images[idx]['content']))
                            st.image(
                                image, 
                                caption=st.session_state.cloudinary_images[idx]['name'],
                                use_container_width=True
                            )

    # Manual Upload Section
    else:
        upload_multiple = st.checkbox("Upload Multiple Files", value=False)
        uploaded_files = st.file_uploader(
            f"Upload {selected_doc_type} {'(Multiple Files)' if upload_multiple else ''}",
            type=["png", "jpg", "jpeg", "pdf"],
            accept_multiple_files=upload_multiple,
        )
        
        if not upload_multiple and uploaded_files:
            uploaded_files = [uploaded_files]
            
        if uploaded_files:
            process_uploaded_files(uploaded_files, processor, selected_doc_type)

    # Display errors if any
    for error in st.session_state.processing_errors:
        st.error(error)

    # Process and visualize data
    if st.session_state.processed_dfs:
        combined_df = pd.concat(st.session_state.processed_dfs, ignore_index=True)
        
        st.subheader("Extracted Parameters")
        st.dataframe(combined_df)

        if selected_graph_type == "Bar Chart":
            figs = visualize_comparative_data(combined_df)
            if figs:
                for fig in figs:
                    st.plotly_chart(fig, use_container_width=True)

        elif selected_graph_type == "Pie Chart":
            if len(st.session_state.processed_dfs) > 1:
                _, common_params = process_comparative_data(combined_df)
                selected_param = st.selectbox("Choose a parameter to visualize", common_params, key='pie_param')
                pie_fig = create_interactive_pie_chart(combined_df, selected_param)
            else:
                pie_fig = create_interactive_pie_chart(combined_df)
                
            if pie_fig:
                st.plotly_chart(pie_fig, use_container_width=True)

        # Download CSV option
        csv_buffer = io.StringIO()
        combined_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="Download Parameters CSV",
            data=csv_buffer.getvalue(),
            file_name=f"{selected_doc_type.lower().replace(' ', '_')}_parameters.csv",
            mime="text/csv",
        )

        # Image Query Section
        st.divider()
        st.subheader("Ask a Question About the Document")
        
        if st.session_state.temp_image_paths:
            if len(st.session_state.temp_image_paths) > 1:
                selected_image = st.selectbox(
                    "Select Image to Query",
                    [f"Document {i+1}" for i in range(len(st.session_state.temp_image_paths))],
                    key='query_image'
                )
                image_index = [f"Document {i+1}" for i in range(len(st.session_state.temp_image_paths))].index(selected_image)
                current_image_path = st.session_state.temp_image_paths[image_index]
            else:
                current_image_path = st.session_state.temp_image_paths[0]
            
            user_query = st.text_input("Enter your question about the document:", key='user_query')
            
            if user_query:
                try:
                    with open(current_image_path, "rb") as img_file:
                        encoded_image = base64.b64encode(img_file.read()).decode("utf-8")
                    
                    response = processor.client.chat.completions.create(
                        model=processor.model,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": user_query},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                                ]
                            }
                        ],
                        max_tokens=500,
                        temperature=0.3
                    )
                    
                    st.write(response.choices[0].message.content)
                
                except Exception as e:
                    st.error(f"Error processing query: {e}")

if __name__ == "__main__":
    main()