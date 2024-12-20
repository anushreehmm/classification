import pandas as pd
from io import BytesIO
import base64

def process_file(contents, filename):
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_excel(BytesIO(decoded))
        df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
        df = df[df['DATE'].dt.year >= 2024]

        if df.empty:
            return f"No valid data from 2024 in '{filename}'.", "", None

        date_range_info = f"Data available from {df['DATE'].min().strftime('%Y-%m-%d')} to {df['DATE'].max().strftime('%Y-%m-%d')}"
        return f"File '{filename}' uploaded successfully!", date_range_info, df.to_dict('records')

    except Exception as e:
        return f"Error processing file: {str(e)}", "", None
