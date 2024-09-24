import json
import pandas as pd
from dotenv import load_dotenv
import os

# Configuarations
load_dotenv(".env", override=True)

INPUT_FILE_PATH = os.getenv('INPUT_FILE_PATH', "input.json")
OUTPUT_FILE_PATH = os.getenv('OUTPUT_FILE_PATH', "output.xlsx")

# Constants
RAW_SHEET_NAME = "layer1"
NO_DUP_SHEET_NAME = "layer2"
AGGREGATED_SHEET_NAME = "layer3"

# Data extraction
# Extracted JSON objects will be stored in a list
data_objs = []

try:
    with open(INPUT_FILE_PATH, "r") as input_data_file:
        # Iterate over each line
        for line in input_data_file:
            # Parse the JSON object from the current line and add to the list
            json_obj = json.loads(line)
            data_objs.append(json_obj)

except FileNotFoundError as fnf_error:
    print(fnf_error)

else:
    # Layer 1. Raw data

    # Convert JSON data to pandas dataframe
    df = pd.DataFrame(data_objs)

    writer = pd.ExcelWriter(OUTPUT_FILE_PATH, engine = 'openpyxl')

    # Export Pandas DataFrame to Excel
    df.to_excel(writer, index=False, sheet_name=RAW_SHEET_NAME)

    # Layer 2. No duplicates
    # Data flattening
    df_normalized = pd.json_normalize(data_objs)

    # Convert "agent.name" to uppercase format
    df_normalized["agent.name"] = df_normalized["agent.name"].str.upper()

    # Remove duplicates and export the DataFrame to Excel
    df_normalized = df_normalized.drop_duplicates(subset=["@timestamp", "application", "agent.name"])
    df_normalized.to_excel(writer, index=False, sheet_name=NO_DUP_SHEET_NAME)

    # Layer 3. Aggregation and dividing into tables

    # Create data report
    shift = 0

    data = {'Initial number of rows': [df.shape[0]], 
            'After duplicates removal': [df_normalized.shape[0]]}
    summary = pd.DataFrame(data)
    summary.to_excel(writer, sheet_name=AGGREGATED_SHEET_NAME, header=True, index=False)
    shift += summary.size + 2

    severity_series = df_normalized.groupby('processed.Severity').size()
    severity_series.to_excel(writer, sheet_name=AGGREGATED_SHEET_NAME, header=['Count'], startrow=shift)
    shift += severity_series.size + 2

    application_series = df_normalized.groupby('application').size()
    application_series.to_excel(writer, sheet_name=AGGREGATED_SHEET_NAME, header=['Count'], startrow=shift)

    # Data splitting by Severity
    grouped_data = df_normalized.groupby('processed.Severity')
    for name, group in grouped_data:
        group = group.sort_values(by=['@timestamp', 'application'], ascending=[False, True])
        group.to_excel(writer, index=False, sheet_name=AGGREGATED_SHEET_NAME + "_" + name)

    writer.close()