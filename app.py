
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(
    page_title="VendorSelect | SPK Vendor IT",
    page_icon="💻",
    layout="wide"
)

# =========================
# STYLE
# =========================
st.markdown("""
<style>
.stApp { background: #f5f7fb; }
.block-container { padding: 1.5rem 2rem 2rem; max-width: 1500px; }
.hero {
    padding: 26px 30px;
    border-radius: 18px;
    background: linear-gradient(135deg, #14213d 0%, #1f5b8f 100%);
    color: white;
    margin-bottom: 20px;
}
.hero h1 { margin: 0; font-size: 32px; }
.hero p { margin: 7px 0 0; opacity: .9; }
.section {
    background: white;
    padding: 18px 20px;
    border-radius: 15px;
    border: 1px solid #e6e9ef;
    margin-bottom: 18px;
}
.recommend {
    background: #eef8f1;
    border: 1px solid #b9dfc5;
    border-left: 6px solid #2e8b57;
    padding: 18px 22px;
    border-radius: 12px;
}
.formula {
    background: #f8f9fc;
    padding: 12px 16px;
    border-radius: 10px;
    border: 1px solid #e6e9ef;
}
</style>
""", unsafe_allow_html=True)

# =========================
# DEFAULT DATA
# =========================
default_vendors = pd.DataFrame({
    "Vendor": [
        "PT Digital Solusi",
        "PT Tech Indonesia",
        "PT E-Business Solution",
        "PT Inovasi Teknologi"
    ],
    "C1": [85, 75, 90, 80],
    "C2": [90, 88, 82, 86],
    "C3": [80, 92, 78, 85],
    "C4": [95, 90, 85, 88],
    "C5": [85, 80, 90, 82],
    "C6": [90, 78, 85, 88]
})

default_criteria = pd.DataFrame({
    "Kode": ["C1", "C2", "C3", "C4", "C5", "C6"],
    "Kriteria": [
        "Harga Penawaran",
        "Kualitas Teknis",
        "Pengalaman Vendor",
        "Keamanan Sistem",
        "Layanan & Support",
        "Waktu Implementasi"
    ],
    "Bobot (%)": [25, 25, 15, 15, 10, 10],
    "Jenis": ["Cost", "Benefit", "Benefit", "Benefit", "Benefit", "Cost"]
})

if "vendors" not in st.session_state:
    st.session_state.vendors = default_vendors.copy()

if "criteria" not in st.session_state:
    st.session_state.criteria = default_criteria.copy()

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# =========================
# WP FUNCTION
# =========================
def calculate_wp(vendors, criteria):
    criteria = criteria.reset_index(drop=True)
    score_cols = criteria["Kode"].tolist()

    valid = vendors.copy()
    for col in score_cols:
        valid[col] = pd.to_numeric(valid[col], errors="coerce")

    weights = criteria["Bobot (%)"].astype(float).to_numpy()
    normalized_weights = weights / weights.sum()

    # Benefit = positive exponent, Cost = negative exponent
    signs = np.where(criteria["Jenis"].str.lower().eq("cost"), -1, 1)
    wp_weights = normalized_weights * signs

    matrix = valid[score_cols].to_numpy(dtype=float)
    S = np.prod(np.power(matrix, wp_weights), axis=1)
    V = S / S.sum()

    result = valid[["Vendor"]].copy()
    result["Vektor S"] = S
    result["Nilai V"] = V
    result = result.sort_values("Nilai V", ascending=False).reset_index(drop=True)
    result.insert(0, "Ranking", range(1, len(result) + 1))
    return result, normalized_weights, wp_weights

# =========================
# HEADER
# =========================
st.markdown("""
<div class="hero">
    <h1>💻 VendorSelect</h1>
    <p>Sistem Pendukung Keputusan Pemilihan Vendor IT untuk Proyek E-Business • Metode Weighted Product (WP)</p>
</div>
""", unsafe_allow_html=True)

# =========================
# TOP ACTIONS
# =========================
a, b, c, d = st.columns([1, 1, 1, 4])

with a:
    if st.button("🔄 Reset Data", use_container_width=True):
        st.session_state.vendors = default_vendors.copy()
        st.session_state.criteria = default_criteria.copy()
        st.session_state.last_result = None
        st.rerun()

with b:
    calculate_clicked = st.button("🧮 Hitung WP", type="primary", use_container_width=True)

with c:
    show_detail = st.toggle("📐 Detail WP", value=True)

# =========================
# DATA VENDOR
# =========================
st.markdown("### 🏢 Data & Penilaian Vendor")

vendors = st.session_state.vendors.copy()
criteria = st.session_state.criteria.copy()

score_cols = criteria["Kode"].tolist()

# Keep vendor columns aligned with criteria
for code in score_cols:
    if code not in vendors.columns:
        vendors[code] = 1

vendors = vendors[["Vendor"] + score_cols]

edited_vendors = st.data_editor(
    vendors,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="vendor_editor",
    column_config={
        "Vendor": st.column_config.TextColumn("Nama Vendor", required=True),
        **{
            code: st.column_config.NumberColumn(
                code,
                min_value=1,
                max_value=100,
                step=1,
                help=f"Nilai penilaian {code}: 1–100"
            ) for code in score_cols
        }
    }
)

st.session_state.vendors = edited_vendors.copy()

# =========================
# CRITERIA
# =========================
st.markdown("### ⚙️ Kriteria & Bobot")

edited_criteria = st.data_editor(
    criteria,
    use_container_width=True,
    hide_index=True,
    num_rows="dynamic",
    key="criteria_editor",
    column_config={
        "Kode": st.column_config.TextColumn("Kode", disabled=True),
        "Kriteria": st.column_config.TextColumn("Nama Kriteria", required=True),
        "Bobot (%)": st.column_config.NumberColumn(
            "Bobot (%)", min_value=0, max_value=100, step=1
        ),
        "Jenis": st.column_config.SelectboxColumn(
            "Jenis", options=["Benefit", "Cost"], required=True
        )
    }
)

# Ensure codes remain unique and create missing score columns
if edited_criteria["Kode"].duplicated().any():
    st.error("Kode kriteria tidak boleh sama.")
    st.stop()

if (edited_criteria["Bobot (%)"] < 0).any():
    st.error("Bobot tidak boleh negatif.")
    st.stop()

st.session_state.criteria = edited_criteria.copy()

total_weight = float(edited_criteria["Bobot (%)"].sum())
m1, m2, m3 = st.columns(3)
m1.metric("Total Bobot", f"{total_weight:.0f}%")
m2.metric("Jumlah Vendor", len(edited_vendors))
m3.metric("Jumlah Kriteria", len(edited_criteria))

if abs(total_weight - 100) > 0.001:
    st.warning("Total bobot saat ini belum 100%. Sistem tetap dapat menghitung karena bobot akan dinormalisasi otomatis.")

# =========================
# CALCULATE
# =========================
if calculate_clicked:
    if edited_vendors.empty:
        st.error("Tambahkan minimal satu vendor.")
        st.stop()

    if edited_criteria.empty:
        st.error("Tambahkan minimal satu kriteria.")
        st.stop()

    if total_weight <= 0:
        st.error("Total bobot harus lebih dari 0.")
        st.stop()

    if edited_vendors["Vendor"].astype(str).str.strip().eq("").any():
        st.error("Nama vendor tidak boleh kosong.")
        st.stop()

    # Re-align vendor score columns
    calc_vendors = edited_vendors.copy()
    for code in edited_criteria["Kode"]:
        if code not in calc_vendors.columns:
            calc_vendors[code] = 1

    try:
        result, normalized, wp_weights = calculate_wp(
            calc_vendors,
            edited_criteria
        )
        st.session_state.last_result = {
            "result": result,
            "normalized": normalized,
            "wp_weights": wp_weights
        }
        st.success("Perhitungan Weighted Product berhasil dilakukan.")
    except Exception as e:
        st.error(f"Perhitungan gagal. Pastikan seluruh nilai penilaian berisi angka 1–100. Detail: {e}")

# =========================
# RESULT
# =========================
if st.session_state.last_result is not None:
    data = st.session_state.last_result
    result = data["result"]
    normalized = data["normalized"]
    wp_weights = data["wp_weights"]

    best = result.iloc[0]

    st.markdown("### 🏆 Hasil Pemilihan Vendor")

    st.markdown(f"""
    <div class="recommend">
        <div style="font-size:14px;">⭐ VENDOR YANG DIREKOMENDASIKAN</div>
        <h2 style="margin:5px 0;">{best['Vendor']}</h2>
        <div>Nilai Vektor V: <b>{best['Nilai V']:.6f}</b> • Ranking: <b>1</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    result_display = result.copy()
    result_display["Vektor S"] = result_display["Vektor S"].map(lambda x: f"{x:.6f}")
    result_display["Nilai V"] = result_display["Nilai V"].map(lambda x: f"{x:.6f}")

    st.dataframe(
        result_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ranking": st.column_config.NumberColumn("Ranking"),
            "Vendor": st.column_config.TextColumn("Vendor"),
            "Vektor S": st.column_config.TextColumn("Vektor S"),
            "Nilai V": st.column_config.TextColumn("Nilai V")
        }
    )

    st.markdown("### 📈 Grafik Ranking")
    chart = result.set_index("Vendor")[["Nilai V"]]
    st.bar_chart(chart)

    if show_detail:
        st.markdown("### 📐 Detail Perhitungan WP")

        detail = edited_criteria[["Kode", "Kriteria", "Bobot (%)", "Jenis"]].copy()
        detail["Bobot Normalisasi"] = normalized
        detail["Bobot WP"] = wp_weights
        st.dataframe(
            detail,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Bobot Normalisasi": st.column_config.NumberColumn(format="%.6f"),
                "Bobot WP": st.column_config.NumberColumn(format="%.6f")
            }
        )

        st.markdown("""
        <div class="formula">
        <b>Rumus Weighted Product:</b>
        <br><br>
        Wj = wj / Σwj
        <br>
        Si = Π (xij)<sup>wj</sup>
        <br>
        Vi = Si / ΣSi
        <br><br>
        <b>Catatan:</b> kriteria <i>Cost</i> menggunakan bobot negatif,
        sedangkan <i>Benefit</i> menggunakan bobot positif.
        </div>
        """, unsafe_allow_html=True)

# =========================
# EXPORT EXCEL
# =========================
st.markdown("### 📥 Export Laporan")

if st.session_state.last_result is not None:
    result = st.session_state.last_result["result"]

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        st.session_state.vendors.to_excel(writer, sheet_name="Penilaian Vendor", index=False)
        st.session_state.criteria.to_excel(writer, sheet_name="Kriteria", index=False)
        result.to_excel(writer, sheet_name="Hasil WP", index=False)
    output.seek(0)

    st.download_button(
        "📊 Download Hasil ke Excel",
        data=output,
        file_name="hasil_pemilihan_vendor_WP.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=False
    )
else:
    st.info("Klik **🧮 Hitung WP** terlebih dahulu untuk mengaktifkan export laporan.")

st.divider()
st.caption("VendorSelect • SPK Pemilihan Vendor IT • Weighted Product (WP)")
