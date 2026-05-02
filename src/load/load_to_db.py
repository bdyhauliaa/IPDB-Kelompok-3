import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": "postgres",
    "port": "5432",
    "dbname": "ekonomi_db",
    "user": "postgres",
    "password": "031205",
}

DATA_FOLDER = "/opt/airflow/data/processed"


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def insert_dim_provinsi(cur, nama):
    cur.execute("""
        INSERT INTO dim_provinsi (nama_provinsi)
        VALUES (%s)
        ON CONFLICT (nama_provinsi) DO NOTHING;
    """, (nama,))

    cur.execute("""
        SELECT id_provinsi FROM dim_provinsi
        WHERE nama_provinsi = %s;
    """, (nama,))

    return cur.fetchone()[0]


def insert_dim_komoditas(cur, nama):
    cur.execute("""
        INSERT INTO dim_komoditas (nama_komoditas)
        VALUES (%s)
        ON CONFLICT (nama_komoditas) DO NOTHING;
    """, (nama,))

    cur.execute("""
        SELECT id_komoditas FROM dim_komoditas
        WHERE nama_komoditas = %s;
    """, (nama,))

    return cur.fetchone()[0]


def insert_dim_waktu(cur, tahun, bulan):
    cur.execute("""
        INSERT INTO dim_waktu (tahun, bulan)
        VALUES (%s, %s)
        ON CONFLICT (tahun, bulan) DO NOTHING;
    """, (tahun, bulan))


# =========================
# LOAD HARGA
# =========================
def load_harga(cur, df):
    for _, row in df.iterrows():
        prov = insert_dim_provinsi(cur, row["provinsi"])
        komod = insert_dim_komoditas(cur, row["komoditas"])

        tahun = int(row["tahun"])
        bulan = str(row["bulan"])
        harga = float(row["harga"])

        insert_dim_waktu(cur, tahun, bulan)

        cur.execute("""
            INSERT INTO fact_harga
            (id_provinsi, id_komoditas, tahun, bulan, harga)
            VALUES (%s, %s, %s, %s, %s);
        """, (prov, komod, tahun, bulan, harga))


# =========================
# LOAD INFLASI
# =========================
def load_inflasi(cur, df):
    for _, row in df.iterrows():
        prov = insert_dim_provinsi(cur, row["provinsi"])

        tahun = int(row["tahun"])
        bulan = str(row["bulan"])
        nilai = float(row["nilai_inflasi"])

        insert_dim_waktu(cur, tahun, bulan)

        cur.execute("""
            INSERT INTO fact_inflasi
            (id_provinsi, tahun, bulan, nilai_inflasi)
            VALUES (%s, %s, %s, %s);
        """, (prov, tahun, bulan, nilai))


def load_csv(path):
    print(f"Loading: {path}")

    df = pd.read_csv(path)
    df.columns = [c.lower() for c in df.columns]

    conn = get_connection()
    cur = conn.cursor()

    try:
        if "komoditas" in df.columns:
            print("→ DETECTED HARGA")
            load_harga(cur, df)

        elif "nilai_inflasi" in df.columns:
            print("→ DETECTED INFLASI")
            load_inflasi(cur, df)

        conn.commit()
        print("SUCCESS")

    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
        raise e

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    print("=== LOAD START ===")

    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".csv"):
            load_csv(os.path.join(DATA_FOLDER, file))

    print("=== LOAD DONE ===")