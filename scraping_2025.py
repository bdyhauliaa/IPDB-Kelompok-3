import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# =========================
# CONFIG
# =========================
url = "https://www.bi.go.id/hargapangan/WebSite/Home/GetGridData1"

headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}

start_date = datetime(2025, 1, 1)
end_date   = datetime(2025, 12, 31)

all_data = []

# =========================
# LOOP TANGGAL
# =========================
current_date = start_date

while current_date <= end_date:
    
    # format tanggal (AMAN semua OS)
    formatted_date = current_date.strftime("%b %d, %Y").replace(" 0", " ")
    
    params = {
        "tanggal": formatted_date,
        "commodity": 1,
        "priceType": 1,
        "isPasokan": 1,
        "jenis": 1,
        "periode": 1,
        "provId": 0
    }
    
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        
        json_data = res.json()
        
        # cek ada data atau tidak
        if "data" in json_data and len(json_data["data"]) > 0:
            df = pd.DataFrame(json_data["data"])
            
            # tambah kolom tanggal request
            df["Tanggal_Request"] = current_date
            
            all_data.append(df)
            print(f"✔ {formatted_date} berhasil ({len(df)} baris)")
        else:
            print(f"⚠ {formatted_date} tidak ada data")
    
    except Exception as e:
        print(f"❌ ERROR {formatted_date}: {e}")
    
    # delay biar aman
    time.sleep(1)
    
    current_date += timedelta(days=1)

# =========================
# GABUNG DATA
# =========================
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    
    # simpan CSV
    final_df.to_csv("harga_pangan_2025_full.csv", index=False)
    
    print("\n🔥 DONE! Data berhasil disimpan")
    print(f"Total baris: {len(final_df)}")
else:
    print("❌ Tidak ada data yang berhasil diambil")