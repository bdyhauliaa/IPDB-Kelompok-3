import requests
import pandas as pd
from datetime import datetime, timedelta
import time


# =========================
# CONFIG API
# =========================

BASE_URL = "https://www.bi.go.id/hargapangan/WebSite/Home/GetVectorMapData"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# =========================
# KOMODITAS RESMI BI
# =========================

KOMODITAS = {
    1: "Beras",
    2: "Daging Ayam",
    3: "Daging Sapi",
    4: "Telur Ayam",
    5: "Bawang Merah",
    6: "Bawang Putih",
    7: "Cabai Merah",
    8: "Cabai Rawit",
    9: "Minyak Goreng",
    10: "Gula Pasir"
}


# =========================
# FORMAT TANGGAL
# =========================

def format_tanggal(dt):
    return dt.strftime("%b %d, %Y").replace(" 0", " ")


# =========================
# SCRAPING FUNCTION
# =========================

def get_data_per_hari(tanggal, commodity_id, commodity_name):

    params = {
        "tanggal": tanggal,
        "commodity": commodity_id,
        "priceType": 1,
        "isPasokan": 1,
        "jenis": 1,
        "periode": 1,
        "provId": 0
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    json_data = response.json()

    if not json_data.get("data"):
        return []

    rows = []

    for item in json_data["data"]:

        value = item["Value"]

        rows.append({
            "tanggal": tanggal,
            "commodity_id": commodity_id,
            "komoditas": commodity_name,
            "provinsi": item["Key"],
            "id_provinsi": value.get("id"),
            "harga": value.get("nilai"),
            "show": value.get("show"),
            "avg_api": value.get("avg"),
            "stddev_api": value.get("stdDev")
        })

    return rows


# =========================
# MAIN SCRAPER
# =========================

def main():

    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)

    all_rows = []

    current = start_date

    print("Mulai scraping data harga pangan BI 2025...\n")

    while current <= end_date:

        tanggal = format_tanggal(current)

        for cid, cname in KOMODITAS.items():

            try:

                rows = get_data_per_hari(
                    tanggal,
                    cid,
                    cname
                )

                all_rows.extend(rows)

                print(f"OK  : {tanggal} | {cname} -> {len(rows)} baris")

                time.sleep(0.25)

            except Exception as e:

                print(f"GAGAL: {tanggal} | {cname} -> {e}")

        current += timedelta(days=1)


    if not all_rows:

        print("Tidak ada data berhasil diambil.")
        return


    df = pd.DataFrame(all_rows)


    # =========================
    # FILTER DATA VALID
    # =========================

    df_valid = df[
        (df["show"] == True) &
        (df["harga"] > 0)
    ].copy()


    # =========================
    # FORMAT TANGGAL
    # =========================

    df_valid["tanggal"] = pd.to_datetime(df_valid["tanggal"])

    df_valid["bulan"] = df_valid["tanggal"].dt.to_period("M").astype(str)


    # =========================
    # AGREGASI BULANAN
    # =========================

    df_bulanan = (
        df_valid
        .groupby(
            ["bulan", "provinsi", "komoditas"],
            as_index=False
        )["harga"]
        .mean()
        .rename(columns={"harga": "rata_rata_harga"})
    )


    # =========================
    # SAVE FILE
    # =========================

    df_valid.to_csv("harga_harian_2025.csv", index=False)
    df_bulanan.to_csv("harga_bulanan_2025.csv", index=False)


    print("\n🔥 DONE! Scraping 2025 selesai")
    print("File tersimpan:")
    print("harga_harian_2025.csv")
    print("harga_bulanan_2025.csv")


# =========================
# RUN
# =========================

if __name__ == "__main__":
    main()