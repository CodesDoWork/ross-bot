import pandas as pd

def get_df():
    cols = ["name", "department", "position", "responsibilities", "email", "phone", "location", "description", "programs"]
    df = pd.read_csv("res/data.csv", sep=";", header=0, names=cols)

    #   Replace NaN values with an empty string and convert everything to string
    df = df.fillna('').astype(str)

    return df

