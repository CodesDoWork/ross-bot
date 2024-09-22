import pandas as pd


def get_df():
    """
    Reads employee contact information from a CSV file and returns it as a pandas DataFrame.
    
    - The CSV file is expected to contain fields such as name, department, position, responsibilities, email, phone, location, description, and programs.
    - Missing values (NaN) are replaced with empty strings, and all data is converted to string format for consistency.
    
    :return: A pandas DataFrame containing cleaned employee contact data.
    """
    cols = ["name", "department", "position", "responsibilities", "email", "phone", "location", "description", "programs"]
    df = pd.read_csv("res/data.csv", sep=";", header=0, names=cols)
    df = df.fillna('').astype(str)

    return df
