"""
This script defines the `get_df()` function, which loads employee contact information from a CSV file into a pandas DataFrame.
The CSV data is processed to handle missing values and ensure consistency by converting all entries to strings.
The DataFrame includes fields like name, department, position, responsibilities, email, phone, location, description, and programs.
"""

# Importing the pandas library, which is essential for handling tabular data such as CSV files.
import pandas as pd

def get_df():
    """
    Reads employee contact information from a CSV file and returns it as a pandas DataFrame.
    
    - The CSV file is expected to contain fields such as name, department, position, responsibilities, email, phone, location, description, and programs.
    - Missing values (NaN) are replaced with empty strings, and all data is converted to string format for consistency.
    
    :return: A pandas DataFrame containing cleaned employee contact data.
    """
    
    # List of columns expected in the CSV file, representing various contact details.
    cols = ["name", "department", "position", "responsibilities", "email", "phone", "location", "description", "programs"]

    # Reading the CSV file ('res/data.csv') using semicolon (;) as the separator. 
    # The first row of the CSV file is considered the header (header=0).
    # The `names` argument ensures that the correct column names are applied to the DataFrame.
    df = pd.read_csv("res/data.csv", sep=";", header=0, names=cols)

    # Replace any missing values (NaN) with empty strings to avoid issues with missing data.
    # Convert the entire DataFrame to strings to ensure data consistency across columns.
    df = df.fillna('').astype(str)

    # Return the processed and cleaned DataFrame.
    return df