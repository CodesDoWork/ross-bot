import pandas as pd

def get_df():
    cols = ["name", "department", "position", "responsibilities", "email", "phone", "location", "description", "programs"]
    return pd.read_csv("res/data.csv", sep=";", header=0, names=cols)
