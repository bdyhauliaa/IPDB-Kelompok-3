import pandas as pd
import os

def clean_file(input_path, output_path):
    df = pd.read_csv(input_path)

    # contoh cleaning
    df = df.drop_duplicates()
    df = df.dropna()

    # contoh ubah kolom (sesuaikan dengan datamu)
    df.columns = [col.lower() for col in df.columns]

    df.to_csv(output_path, index=False)
    print(f"Cleaned: {output_path}")


if __name__ == "__main__":
    input_folder = "data/raw"
    output_folder = "data/processed"

    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.endswith(".csv"):
            clean_file(
                f"{input_folder}/{file}",
                f"{output_folder}/{file}"
            )