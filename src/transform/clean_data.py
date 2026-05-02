import os
import re
import pandas as pd

INPUT_FOLDER = "/opt/airflow/data/raw"
OUTPUT_FOLDER = "/opt/airflow/data/processed"

MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]


# ==============================
# CLEAN NUMBER
# ==============================
def clean_number(value):
    if pd.isna(value):
        return None

    value = str(value).strip()
    value = value.replace("Rp", "").replace(" ", "")

    if value.lower() in ["", "-", "nan", "none"]:
        return None

    if "," in value and "." in value:
        value = value.replace(".", "").replace(",", ".")
    elif "," in value:
        value = value.replace(",", ".")

    value = re.sub(r"[^0-9.\-]", "", value)

    if value == "":
        return None

    return round(float(value), 2)


# ==============================
# GET YEAR
# ==============================
def get_year_from_filename(filename):
    match = re.search(r"(2024|2025)", filename)
    return int(match.group(1)) if match else None


# ==============================
# NORMALISASI PROVINSI (PENTING)
# ==============================
def normalize_provinsi(text):
    if pd.isna(text):
        return None

    text = str(text).strip()

    # hapus prefix "Prov"
    text = re.sub(r"(?i)^prov\s+", "", text)

    # standardisasi case
    text = text.title()

    # FIX CASE KHUSUS
    mapping = {
        "Dki Jakarta": "DKI Jakarta",
        "Dki Jakarta": "DKI Jakarta",
        "Di Yogyakarta": "DI Yogyakarta",
        "D I Yogyakarta": "DI Yogyakarta",
        "Yogyakarta": "DI Yogyakarta",
        "Papua": "Papua",
    }

    return mapping.get(text, text)


# ==============================
# TRANSFORM HARGA
# ==============================
def transform_harga(input_path, output_path):
    filename = os.path.basename(input_path)
    print(f"Processing harga: {filename}")

    df = pd.read_csv(input_path)

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    required = ["bulan", "provinsi", "komoditas", "rata_rata_harga"]

    for col in required:
        if col not in df.columns:
            print(f"Kolom {col} tidak ditemukan")
            return

    result = pd.DataFrame()

    result["provinsi"] = df["provinsi"].apply(normalize_provinsi)
    result["komoditas"] = df["komoditas"].astype(str).str.strip()

    result["tahun"] = df["bulan"].astype(str).str[:4].astype(int)

    bulan_angka = df["bulan"].astype(str).str[-2:]

    mapping_bulan = {
        "01": "Januari",
        "02": "Februari",
        "03": "Maret",
        "04": "April",
        "05": "Mei",
        "06": "Juni",
        "07": "Juli",
        "08": "Agustus",
        "09": "September",
        "10": "Oktober",
        "11": "November",
        "12": "Desember"
    }

    result["bulan"] = bulan_angka.map(mapping_bulan)

    result["harga"] = df["rata_rata_harga"].apply(clean_number)

    result = result.dropna()
    result = result.drop_duplicates()

    result.to_csv(output_path, index=False)

    print(f"Saved harga: {output_path}")
    print(f"Rows: {len(result)}")


# ==============================
# TRANSFORM INFLASI
# ==============================
def transform_inflasi(input_path, output_path):
    filename = os.path.basename(input_path)
    tahun = get_year_from_filename(filename)

    print(f"Processing inflasi: {filename}")

    df = pd.read_csv(input_path, skiprows=3)

    df = df.dropna(axis=1, how="all")

    df.columns = [str(c).strip() for c in df.columns]

    df = df.rename(columns={df.columns[0]: "provinsi"})

    if "Tahunan" in df.columns:
        df = df.drop(columns=["Tahunan"])

    df["provinsi"] = df["provinsi"].apply(normalize_provinsi)

    # hapus baris kosong / Indonesia
    df = df[df["provinsi"].str.lower() != "indonesia"]

    bulan_ada = [m for m in MONTHS if m in df.columns]

    result = df.melt(
        id_vars=["provinsi"],
        value_vars=bulan_ada,
        var_name="bulan",
        value_name="nilai_inflasi"
    )

    result["tahun"] = tahun

    result["nilai_inflasi"] = result["nilai_inflasi"].apply(clean_number)

    result = result[["provinsi", "tahun", "bulan", "nilai_inflasi"]]

    result = result.dropna()
    result = result.drop_duplicates()

    result.to_csv(output_path, index=False)

    print(f"Saved inflasi: {output_path}")
    print(f"Rows: {len(result)}")


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    print("=== TRANSFORM START ===")

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    target_files = [
        "harga_bulanan_2024.csv",
        "harga_bulanan_2025.csv",
        "inflasi_2024.csv",
        "inflasi_2025.csv"
    ]

    for file in os.listdir(INPUT_FOLDER):
        if file not in target_files:
            print(f"SKIP: {file}")
            continue

        path = os.path.join(INPUT_FOLDER, file)
        output_path = os.path.join(OUTPUT_FOLDER, file)

        if "harga" in file.lower():
            transform_harga(path, output_path)

        elif "inflasi" in file.lower():
            transform_inflasi(path, output_path)

    print("=== TRANSFORM DONE ===")
