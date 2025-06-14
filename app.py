from flask import Flask, render_template, request, send_file
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import io

app = Flask(__name__)

# Load Data
file_path = "data_sekolah.xlsx"
df = pd.read_excel(file_path)

# Pastikan data memiliki kolom yang sesuai
if not {'Nama Sekolah', 'Tahun', 'Nilai Bawah', 'Nilai Atas'}.issubset(df.columns):
    raise ValueError("Kolom dalam file Excel tidak sesuai. Pastikan ada: 'Nama Sekolah', 'Tahun', 'Nilai Bawah', 'Nilai Atas'")

# Pisahkan data 2023 dan 2024
df_2023 = df[df["Tahun"] == 2023]
df_2024 = df[df["Tahun"] == 2024]

# Fungsi prediksi peluang berdasarkan nilai pengguna
def prediksi_peluang(nilai_user):
    prediksi = []
    for _, row in df_2024.iterrows():
        nama_sekolah = row["Nama Sekolah"]
        nilai_bawah = row["Nilai Bawah"]
        nilai_atas = row["Nilai Atas"]
        
        if nilai_user >= nilai_atas:
            peluang = 95  
        elif nilai_user >= nilai_bawah:
            peluang = 70  
        else:
            peluang = 30  
        
        prediksi.append((nama_sekolah, peluang))
    
    prediksi.sort(key=lambda x: x[1], reverse=True)  
    return prediksi

# Fungsi untuk membuat grafik secara dinamis
def generate_chart(nilai_user):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # 1. Grafik Perbandingan Nilai Bawah & Atas (2023 - 2024)
    sns.lineplot(data=df, x="Tahun", y="Nilai Bawah", label="Nilai Bawah", marker="o", ax=axes[0])
    sns.lineplot(data=df, x="Tahun", y="Nilai Atas", label="Nilai Atas", marker="o", ax=axes[0])
    axes[0].set_title("Perbandingan Nilai Bawah & Atas (2023 - 2024)")
    axes[0].set_xlabel("Tahun")
    axes[0].set_ylabel("Nilai")
    axes[0].legend()
    axes[0].grid()

    # 2. Grafik Prediksi Sekolah Berdasarkan Nilai Pengguna
    df_prediksi = pd.DataFrame(prediksi_peluang(nilai_user), columns=["Nama Sekolah", "Peluang"])
    sns.barplot(data=df_prediksi, x="Peluang", y="Nama Sekolah", hue="Peluang", ax=axes[1], palette="Reds")
    axes[1].set_title(f"Prediksi Sekolah berdasarkan Nilai {nilai_user}")

    # 3. Grafik Tren Nilai Ambang Batas
    sns.lineplot(data=df, x="Tahun", y="Nilai Bawah", label="Nilai Bawah", marker="o", ax=axes[2])
    sns.lineplot(data=df, x="Tahun", y="Nilai Atas", label="Nilai Atas", marker="o", ax=axes[2])
    axes[2].scatter(2025, nilai_user, color="blue", label="Nilai Anda", zorder=5)  # Plot nilai user di 2025
    axes[2].set_title("Prediksi Nilai Ambang Batas 2025")
    axes[2].set_xlabel("Tahun")
    axes[2].set_ylabel("Nilai")
    axes[2].legend()
    axes[2].grid()

    # Simpan ke dalam objek BytesIO
    img_io = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img_io, format="png")
    img_io.seek(0)
    plt.close()
    return img_io

# ROUTES
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/prediksi", methods=["POST"])
def prediksi():
    nilai_user = float(request.form["nilai"])
    hasil_prediksi = prediksi_peluang(nilai_user)
    return render_template("hasil.html", nilai=nilai_user, hasil_prediksi=hasil_prediksi)

@app.route("/grafik.png")
def grafik():
    nilai_user = float(request.args.get("nilai", 90))  # Default 90 jika tidak ada input
    img_io = generate_chart(nilai_user)
    return send_file(img_io, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
