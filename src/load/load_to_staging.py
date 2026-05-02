import os
import pandas as pd
import psycopg2

DATA_FOLDER = "/opt/airflow/data/processed"

DB_CONFIG = {
    "host": "postgres",
    "port": "5432",
    "dbname": "ekonomi_db",
    "user": "postgres",
    "password": "031205"
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def main():
    conn = get_connection()
    cur = conn.cursor()

    print("=== LOAD STAGING START ===")

    cur.execute("TRUNCATE staging.stg_harga;")
    cur.execute("TRUNCATE staging.stg_inflasi;")

    for file in os.listdir(DATA_FOLDER):
        path = os.path.join(DATA_FOLDER, file)

        if not file.endswith(".csv"):
            continue

        df = pd.read_csv(path)
        df.columns = [c.lower() for c in df.columns]

        if "komoditas" in df.columns:
            for _, row in df.iterrows():
                cur.execute("""
                    INSERT INTO staging.stg_harga
                    VALUES (%s,%s,%s,%s,%s)
                """, (
                    row["provinsi"],
                    row["komoditas"],
                    int(row["tahun"]),
                    row["bulan"],
                    float(row["harga"])
                ))

        elif "nilai_inflasi" in df.columns:
            for _, row in df.iterrows():
                cur.execute("""
                    INSERT INTO staging.stg_inflasi
                    VALUES (%s,%s,%s,%s)
                """, (
                    row["provinsi"],
                    int(row["tahun"]),
                    row["bulan"],
                    float(row["nilai_inflasi"])
                ))

    conn.commit()
    cur.close()
    conn.close()

    print("=== LOAD STAGING DONE ===")


if __name__ == "__main__":
    main()