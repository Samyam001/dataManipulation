import pandas as pd

path = r"D:\Academics\_sec\RetailStoreData.xlsx"

try:
    df = pd.read_excel(path)

    print("Excel file loaded successfully!")
    print("\nData:")
    print(df.head())

except FileNotFoundError:
    print("Error: The Excel file was not found.")
    print(f"Checked location: {path}")

except Exception as e:
    print(f"An error occurred: {e}")