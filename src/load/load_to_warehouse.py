import psycopg2

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

    print("=== LOAD WAREHOUSE START ===")

    cur.execute("TRUNCATE warehouse.fact_harga RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE warehouse.fact_inflasi RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE warehouse.dim_provinsi RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE warehouse.dim_komoditas RESTART IDENTITY CASCADE;")
    cur.execute("TRUNCATE warehouse.dim_waktu RESTART IDENTITY CASCADE;")

    # DIMENSI
    cur.execute("""
        INSERT INTO warehouse.dim_provinsi (nama_provinsi)
        SELECT DISTINCT provinsi FROM staging.stg_harga
        UNION
        SELECT DISTINCT provinsi FROM staging.stg_inflasi;
    """)

    cur.execute("""
        INSERT INTO warehouse.dim_komoditas (nama_komoditas)
        SELECT DISTINCT komoditas FROM staging.stg_harga;
    """)

    cur.execute("""
        INSERT INTO warehouse.dim_waktu (tahun, bulan)
        SELECT DISTINCT tahun, bulan FROM staging.stg_harga
        UNION
        SELECT DISTINCT tahun, bulan FROM staging.stg_inflasi;
    """)

    # FACT HARGA
    cur.execute("""
        INSERT INTO warehouse.fact_harga
        (id_provinsi, id_komoditas, id_waktu, harga)

        SELECT
            dp.id_provinsi,
            dk.id_komoditas,
            dw.id_waktu,
            s.harga

        FROM staging.stg_harga s
        JOIN warehouse.dim_provinsi dp
            ON s.provinsi = dp.nama_provinsi
        JOIN warehouse.dim_komoditas dk
            ON s.komoditas = dk.nama_komoditas
        JOIN warehouse.dim_waktu dw
            ON s.tahun = dw.tahun
            AND s.bulan = dw.bulan;
    """)

    # FACT INFLASI
    cur.execute("""
        INSERT INTO warehouse.fact_inflasi
        (id_provinsi, id_waktu, nilai_inflasi)

        SELECT
            dp.id_provinsi,
            dw.id_waktu,
            s.nilai_inflasi

        FROM staging.stg_inflasi s
        JOIN warehouse.dim_provinsi dp
            ON s.provinsi = dp.nama_provinsi
        JOIN warehouse.dim_waktu dw
            ON s.tahun = dw.tahun
            AND s.bulan = dw.bulan;
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("=== LOAD WAREHOUSE DONE ===")


if __name__ == "__main__":
    main()