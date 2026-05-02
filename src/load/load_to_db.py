import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "host.docker.internal"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "dbname": os.getenv("POSTGRES_DB", "ekonomi_db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "123456"),
}

DATA_FOLDER = "/opt/airflow/data/processed"


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def insert_dim_provinsi(cur, nama_provinsi):
    cur.execute(
        """
        INSERT INTO dim_provinsi (nama_provinsi)
        VALUES (%s)
        ON CONFLICT (nama_provinsi) DO NOTHING;
        """,
        (nama_provinsi,)
    )

    cur.execute(
        """
        SELECT id_provinsi
        FROM dim_provinsi
        WHERE nama_provinsi = %s;
        """,
        (nama_provinsi,)
    )

    return cur.fetchone()[0]


def insert_dim_komoditas(cur, nama_komoditas):
    cur.execute(
        """
        INSERT INTO dim_komoditas (nama_komoditas)
        VALUES (%s)
        ON CONFLICT (nama_komoditas) DO NOTHING;
        """,
        (nama_komoditas,)
    )

    cur.execute(
        """
        SELECT id_komoditas
        FROM dim_komoditas
        WHERE nama_komoditas = %s;
        """,
        (nama_komoditas,)
    )

    return cur.fetchone()[0]


def insert_dim_waktu(cur, tahun, bulan):
    cur.execute(
        """
        INSERT INTO dim_waktu (tahun, bulan)
        VALUES (%s, %s)
        ON CONFLICT (tahun, bulan) DO NOTHING;
        """,
        (tahun, bulan)
    )


def insert_fact_harga(cur, id_provinsi, id_komoditas, tahun, bulan, harga):
    cur.execute(
        """
        INSERT INTO fact_harga 
        (id_provinsi, id_komoditas, tahun, bulan, harga)
        VALUES (%s, %s, %s, %s, %s);
        """,
        (id_provinsi, id_komoditas, tahun, bulan, harga)
    )


def load_csv(file_path):
    print(f"Loading file: {file_path}")

    df = pd.read_csv(file_path)

    # rapikan nama kolom
    df.columns = [col.lower().strip() for col in df.columns]

    required_columns = ["provinsi", "komoditas", "tahun", "bulan", "harga"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Kolom '{col}' tidak ditemukan di {file_path}. Kolom tersedia: {list(df.columns)}")

    conn = get_connection()
    cur = conn.cursor()

    try:
        for _, row in df.iterrows():
            nama_provinsi = str(row["provinsi"]).strip()
            nama_komoditas = str(row["komoditas"]).strip()
            tahun = int(row["tahun"])
            bulan = str(row["bulan"]).strip()
            harga = float(row["harga"])

            id_provinsi = insert_dim_provinsi(cur, nama_provinsi)
            id_komoditas = insert_dim_komoditas(cur, nama_komoditas)
            insert_dim_waktu(cur, tahun, bulan)
            insert_fact_harga(cur, id_provinsi, id_komoditas, tahun, bulan, harga)

        conn.commit()
        print(f"SUCCESS loaded: {file_path}")

    except Exception as e:
        conn.rollback()
        print(f"FAILED load {file_path}: {e}")
        raise e

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    if not os.path.exists(DATA_FOLDER):
        raise FileNotFoundError(f"Folder tidak ditemukan: {DATA_FOLDER}")

    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".csv"):
            load_csv(os.path.join(DATA_FOLDER, file))