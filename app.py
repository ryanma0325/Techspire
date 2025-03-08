import google.generativeai as genai
import requests
import pandas as pd
import re
from io import BytesIO
from PIL import Image

# Configure Google Gemini AI API
GENAI_API_KEY = "REPLACE WITH YOUR OWN GEMINI AI API KEY"  # Replace with your valid API key
genai.configure(api_key=GENAI_API_KEY)

# Function: Convert Google Drive Link to Direct URL
def convert_drive_link(url):
    """Converts a Google Drive sharing link into a direct download link."""
    match = re.search(r"file/d/([a-zA-Z0-9_-]+)", url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    return None  # Return None if invalid

# Function: Download Image from Google Drive
def download_image(image_url):
    """Downloads an image and returns it as BytesIO."""
    try:
        direct_url = convert_drive_link(image_url)
        if not direct_url:
            return None  # Skip invalid links
        
        response = requests.get(direct_url, allow_redirects=True)
        if response.status_code == 200:
            return BytesIO(response.content)
    except requests.RequestException:
        return None  # Return None if download fails
    return None

# Function: Analyze Image with Gemini AI
def analyze_image(image_url):
    """Downloads and analyzes an image using Google Gemini AI."""
    try:
        image_bytes = download_image(image_url)
        if not image_bytes:
            return "Error: Could not download image."

        # Convert to a valid image format
        try:
            image = Image.open(image_bytes)  # Convert to PIL Image
        except:
            return "Error: Invalid image file."

        # Send properly formatted image to Gemini AI
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = """If image of clothing, analyze the image and assign a quality score (e.g., "Like New," "Used
        - Good," "Salvage") based on product wear and tear.If it is a tag, respond with the tag number."""
        
        ai_response = gemini_model.generate_content([prompt, image])  # Send prompt and image
        
        return ai_response.text if ai_response else "No AI response."
        
        return ai_response.text if ai_response else "No AI response."
    except Exception as e:
        return f"Error: {str(e)}"

# Function: Process CSV and Save Analysis Results
def process_csv(input_csv, output_csv="analysis_results.csv"):
    """Reads a CSV file, processes images, and saves analysis results."""
    try:
        df = pd.read_csv(input_csv)
        if "image_url" not in df.columns:
            raise ValueError("CSV file must contain an 'image_url' column.")
        
        # Apply AI analysis to each image URL
        df["AI_Analysis"] = df["image_url"].apply(analyze_image)

        # Save results
        df.to_csv(output_csv, index=False)
        print(f"Analysis saved to {output_csv}")
    except Exception as e:
        print(f"Error processing CSV: {str(e)}")

# Run Analysis on image_links.csv
csv_file_path = "image_links.csv"  # Ensure this file is present
process_csv(csv_file_path)
