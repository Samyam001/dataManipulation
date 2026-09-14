import pandas as pd

from dataManipulation import clean_data, manipulate_data


EXCEL_PATH = r"D:\Academics\_sec\RetailStoreData.xlsx"


def main():
    try:
        # Load Excel file
        df = pd.read_excel(EXCEL_PATH)

        print("Excel file loaded successfully!")
        print("\nOriginal data:")
        print(df.head())

        # Data manipulation
        print("Data cleaning ....")
        df = clean_data(df)
        df = manipulate_data(df)

        print("\nProcessed data:")
        print(df.head())

    except FileNotFoundError:
        print("Error: The Excel file was not found.")
        print(f"Checked location: {EXCEL_PATH}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()