import os

DATA_FOLDER = "/opt/airflow/data"


def extract():
    print("=== EXTRACT START ===")

    files = os.listdir(DATA_FOLDER)
    csv_files = [f for f in files if f.endswith(".csv")]

    if not csv_files:
        print("Tidak ada file CSV")
    else:
        for file in csv_files:
            print(f"Found file: {file}")

    print(f"Total CSV: {len(csv_files)}")
    print("=== EXTRACT DONE ===")


if __name__ == "__main__":
    extract()