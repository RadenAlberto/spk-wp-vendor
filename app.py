import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import plotly.graph_objects as go

st.set_page_config(
    page_title="VendorSelect Pro | SPK Vendor IT",
    page_icon="💻",
    layout="wide"
)

# =========================
# STYLE 100% FULL DARK THEME (HIGH CONTRAST)
# =========================
st.markdown("""
<style>
/* Background Utama Full Dark */
.stApp { 
    background-color: #0b0f19 !important; 
    color: #f8fafc !important;
}

.block-container { 
    padding: 1.8rem 2.2rem 3rem; 
    max-width: 1450px; 
}

/* Pastikan semua judul dan teks selalu putih/kontras */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
    font-weight: 700 !important;
}
p, span, label {
    color: #cbd5e1 !important;
}

.stCaption, [data-testid="stCaptionContainer"] p {
    color: #94a3b8 !important;
}

/* Hero Header */
.hero {
    padding: 24px 30px;
    border-radius: 16px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    border: 1px solid #334155;
    margin-bottom: 20px;
}
.hero h1 { 
    margin: 0; 
    font-size: 28px; 
    font-weight: 800;
    color: #ffffff !important; 
}
.hero p { 
    margin: 6px 0 0; 
    font-size: 14px;
    color: #94a3b8 !important; 
}

/* Styling TAB Navigasi agar sangat jelas terbaca */
button[data-baseweb="tab"] {
    color: #94a3b8 !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding-bottom: 8px !important;
}
button[data-baseweb="tab"]:hover {
    color: #e2e8f0 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #60a5fa !important;
    border-bottom-color: #3b82f6 !important;
}

/* Metric Cards Dark */
[data-testid="stMetric"] {
    background-color: #151c2c !important;
    border: 1px solid #334155 !important;
    padding: 14px 18px !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}
[data-testid="stMetricLabel"] p {
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}
[data-testid="stMetricValue"] div {
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 24px !important;
}

/* PODIUM KARTU TOP 3 (DARK THEME) */
.podium-card {
    background: #151c2c;
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
    border: 1px solid #334155;
    height: 100%;
}
.podium-1 {
    border: 2px solid #eab308;
    border-top: 6px solid #eab308;
    background: linear-gradient(180deg, #242013 0%, #151c2c 100%);
    box-shadow: 0 8px 24px rgba(234, 179, 8, 0.25);
}
.podium-2 {
    border-top: 6px solid #94a3b8;
}
.podium-3 {
    border-top: 6px solid #d97706;
}
.podium-rank {
    font-size: 24px;
    font-weight: 800;
    margin-bottom: 6px;
}
.podium-title {
    font-size: 20px;
    font-weight: 800;
    color: #ffffff !important;
    margin-bottom: 6px;
}
.podium-score {
    font-size: 14px;
    color: #cbd5e1 !important;
}

/* Executive Summary Box */
.summary-box {
    background: rgba(6, 78, 59, 0.25);
    border: 1px solid #059669;
    border-left: 6px solid #10b981;
    padding: 16px 20px;
    border-radius: 12px;
    margin: 15px 0 20px;
    color: #a7f3d0 !important;
}
.summary-box b {
    color: #34d399 !important;
}

/* Formula Box */
.formula-card {
    background: #151c2c;
    padding: 18px 22px;
    border-radius: 12px;
    border: 1px solid #334155;
    border-left: 6px solid #3b82f6;
    color: #e2e8f0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
.formula-card code {
    background: #0f172a;
    color: #60a5fa;
    padding: 2px 6px;
    border-radius: 4px;
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
# FUNGSI PERHITUNGAN WP
# =========================
def calculate_wp(vendors, criteria):
    criteria = criteria.reset_index(drop=True)
    score_cols = criteria["Kode"].tolist()

    valid = vendors.copy()
    for col in score_cols:
        valid[col] = pd.to_numeric(valid[col], errors="coerce").fillna(1)

    weights = criteria["Bobot (%)"].astype(float).to_numpy()
    total_w = weights.sum() if weights.sum() > 0 else 1.0
    normalized_weights = weights / total_w

    signs = np.where(criteria["Jenis"].str.lower().eq("cost"), -1, 1)
    wp_weights = normalized_weights * signs

    matrix = valid[score_cols].to_numpy(dtype=float)
    S = np.prod(np.power(matrix, wp_weights), axis=1)
    sum_s = S.sum() if S.sum() > 0 else 1.0
    V = S / sum_s

    result = valid[["Vendor"]].copy()
    result["Vektor S"] = S
    result["Nilai V"] = V
    result = result.sort_values("Nilai V", ascending=False).reset_index(drop=True)
    result.insert(0, "Ranking", range(1, len(result) + 1))
    return result, normalized_weights, wp_weights

# Hitung awal jika belum ada hasil
if st.session_state.last_result is None:
    res, norm, wp_w = calculate_wp(st.session_state.vendors, st.session_state.criteria)
    st.session_state.last_result = {"result": res, "normalized": norm, "wp_weights": wp_w}

# =========================
# MODAL / DIALOG TAMBAH VENDOR
# =========================
dialog_fn = getattr(st, "dialog", getattr(st, "experimental_dialog", None))

def show_add_vendor_modal():
    @dialog_fn("➕ Tambah Vendor Baru", width="large")
    def modal():
        st.markdown("Masukkan identitas vendor dan nilai performa kriteria (skala **1 – 100**):")
        with st.form("form_add_vendor", clear_on_submit=True):
            nama_vendor = st.text_input("Nama Vendor*", placeholder="Contoh: PT Solusi Nusantara")
            
            st.markdown("---")
            st.markdown("##### 📝 Nilai Kriteria Penilaian")
            
            scores = {}
            cols = st.columns(2)
            for idx, (_, row) in enumerate(st.session_state.criteria.iterrows()):
                kode = row["Kode"]
                nama_kriteria = row["Kriteria"]
                jenis = row["Jenis"]
                col = cols[idx % 2]
                with col:
                    scores[kode] = st.slider(
                        f"{kode} - {nama_kriteria} ({jenis})",
                        min_value=1,
                        max_value=100,
                        value=80,
                        step=1
                    )

            submitted = st.form_submit_button("💾 Simpan Vendor", type="primary", use_container_width=True)
            if submitted:
                if not nama_vendor.strip():
                    st.error("Nama Vendor tidak boleh kosong!")
                elif nama_vendor.strip() in st.session_state.vendors["Vendor"].values:
                    st.error("Nama Vendor sudah terdaftar. Gunakan nama lain.")
                else:
                    new_row = {"Vendor": nama_vendor.strip(), **scores}
                    st.session_state.vendors = pd.concat([st.session_state.vendors, pd.DataFrame([new_row])], ignore_index=True)
                    res, norm, wp_w = calculate_wp(st.session_state.vendors, st.session_state.criteria)
                    st.session_state.last_result = {"result": res, "normalized": norm, "wp_weights": wp_w}
                    st.success(f"Vendor '{nama_vendor}' berhasil ditambahkan!")
                    st.rerun()
    modal()

# =========================
# HEADER
# =========================
st.markdown("""
<div class="hero">
    <h1>💻 VendorSelect Pro</h1>
    <p>Sistem Pendukung Keputusan Pemilihan Vendor IT Proyek E-Business • Metode Weighted Product (WP)</p>
</div>
""", unsafe_allow_html=True)

# =========================
# QUICK ACTION BAR
# =========================
col_act1, col_act2, col_act3, col_preset = st.columns([1.3, 1.4, 1.1, 3.2])

with col_act1:
    calculate_clicked = st.button("🧮 Hitung Ulang", type="primary", use_container_width=True)

with col_act2:
    if st.button("➕ Tambah Vendor", use_container_width=True):
        if dialog_fn:
            show_add_vendor_modal()

with col_act3:
    if st.button("🔄 Reset Data", use_container_width=True):
        st.session_state.vendors = default_vendors.copy()
        st.session_state.criteria = default_criteria.copy()
        res, norm, wp_w = calculate_wp(st.session_state.vendors, st.session_state.criteria)
        st.session_state.last_result = {"result": res, "normalized": norm, "wp_weights": wp_w}
        st.rerun()

with col_preset:
    preset_choice = st.selectbox(
        "⚡ Preset Skenario Bobot:",
        options=[
            "Pilih Skenario Bobot...",
            "Standar (Default)",
            "Prioritas Efisiensi Biaya (Cost-Focused)",
            "Prioritas Kualitas & Keamanan Teknis",
            "Prioritas Kecepatan Implementasi"
        ],
        label_visibility="collapsed"
    )
    if preset_choice == "Standar (Default)":
        st.session_state.criteria["Bobot (%)"] = [25, 25, 15, 15, 10, 10]
        res, norm, wp_w = calculate_wp(st.session_state.vendors, st.session_state.criteria)
        st.session_state.last_result = {"result": res, "normalized": norm, "wp_weights": wp_w}
    elif preset_choice == "Prioritas Efisiensi Biaya (Cost-Focused)":
        st.session_state.criteria["Bobot (%)"] = [45, 15, 10, 10, 10, 10]
        res, norm, wp_w = calculate_wp(st.session_state.vendors, st.session_state.criteria)
        st.session_state.last_result = {"result": res, "normalized": norm, "wp_weights": wp_w}
    elif preset_choice == "Prioritas Kualitas & Keamanan Teknis":
        st.session_state.criteria["Bobot (%)"] = [15, 35, 10, 30, 5, 5]
        res, norm, wp_w = calculate_wp(st.session_state.vendors, st.session_state.criteria)
        st.session_state.last_result = {"result": res, "normalized": norm, "wp_weights": wp_w}
    elif preset_choice == "Prioritas Kecepatan Implementasi":
        st.session_state.criteria["Bobot (%)"] = [15, 20, 15, 10, 10, 30]
        res, norm, wp_w = calculate_wp(st.session_state.vendors, st.session_state.criteria)
        st.session_state.last_result = {"result": res, "normalized": norm, "wp_weights": wp_w}

st.write("")

# =========================
# TABS UTAMA (DENGAN TULISAN JELAS)
# =========================
tab_data, tab_result, tab_chart, tab_math = st.tabs([
    "🏢 1. Data & Penilaian Vendor",
    "🏆 2. Hasil & Rekomendasi",
    "📊 3. Visualisasi & Radar Chart",
    "📐 4. Detail Perhitungan WP"
])

# =========================
# TAB 1: DATA & PENILAIAN
# =========================
with tab_data:
    col_t1_left, col_t1_right = st.columns([2.8, 1.2])
    
    with col_t1_left:
        st.markdown("### 🏢 Matriks Penilaian Vendor")
        st.caption("Klik langsung pada sel angka di tabel untuk mengedit nilai (skala 1–100):")
        
        score_cols = st.session_state.criteria["Kode"].tolist()
        for c in score_cols:
            if c not in st.session_state.vendors.columns:
                st.session_state.vendors[c] = 80
        
        vendors_display = st.session_state.vendors[["Vendor"] + score_cols]
        
        edited_vendors = st.data_editor(
            vendors_display,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="vendor_table_editor",
            column_config={
                "Vendor": st.column_config.TextColumn("Nama Vendor", required=True),
                **{c: st.column_config.NumberColumn(c, min_value=1, max_value=100, step=1) for c in score_cols}
            }
        )
        st.session_state.vendors = edited_vendors

    with col_t1_right:
        st.markdown("### ⚙️ Kriteria & Bobot")
        st.caption("Ubah persentase bobot atau jenis kriteria:")
        edited_criteria = st.data_editor(
            st.session_state.criteria,
            use_container_width=True,
            hide_index=True,
            key="criteria_table_editor",
            column_config={
                "Kode": st.column_config.TextColumn("Kode", disabled=True),
                "Kriteria": st.column_config.TextColumn("Kriteria", required=True),
                "Bobot (%)": st.column_config.NumberColumn("Bobot (%)", min_value=0, max_value=100, step=1),
                "Jenis": st.column_config.SelectboxColumn("Jenis", options=["Benefit", "Cost"], required=True)
            }
        )
        st.session_state.criteria = edited_criteria
        
        tot_w = float(edited_criteria["Bobot (%)"].sum())
        st.metric("Total Bobot Kriteria", f"{tot_w:.0f}%")
        if abs(tot_w - 100) > 0.001:
            st.caption("ℹ️ *Bobot akan dinormalisasi otomatis menjadi 100% saat perhitungan.*")

    # Fitur Import / Export Template
    with st.expander("📁 Import / Export Template Data Vendor (Excel)"):
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            template_io = BytesIO()
            with pd.ExcelWriter(template_io, engine="openpyxl") as writer:
                st.session_state.vendors.to_excel(writer, sheet_name="DataVendor", index=False)
            template_io.seek(0)
            st.download_button(
                "📥 Download Template Excel Vendor",
                data=template_io,
                file_name="template_vendor_wp.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with c_exp2:
            uploaded_file = st.file_uploader("Upload Excel Nilai Vendor", type=["xlsx", "xls"], label_visibility="collapsed")
            if uploaded_file is not None:
                try:
                    df_up = pd.read_excel(uploaded_file)
                    if "Vendor" in df_up.columns:
                        st.session_state.vendors = df_up
                        res, norm, wp_w = calculate_wp(st.session_state.vendors, st.session_state.criteria)
                        st.session_state.last_result = {"result": res, "normalized": norm, "wp_weights": wp_w}
                        st.success("Data berhasil diimport dari file!")
                        st.rerun()
                    else:
                        st.error("File Excel wajib memiliki kolom 'Vendor'.")
                except Exception as ex:
                    st.error(f"Gagal membaca file: {ex}")

if calculate_clicked:
    if st.session_state.vendors.empty:
        st.error("Minimal harus ada 1 vendor!")
    else:
        res, norm, wp_w = calculate_wp(st.session_state.vendors, st.session_state.criteria)
        st.session_state.last_result = {"result": res, "normalized": norm, "wp_weights": wp_w}
        st.success("✅ Perhitungan WP berhasil diperbarui!")

# =========================
# TAB 2: HASIL & REKOMENDASI
# =========================
with tab_result:
    if st.session_state.last_result is not None:
        res_data = st.session_state.last_result["result"]
        best_vendor = res_data.iloc[0]

        st.markdown("### 🏆 Podium Peringkat Teratas")
        
        pod_cols = st.columns([1, 1.2, 1])
        
        # Juara 2
        with pod_cols[0]:
            if len(res_data) > 1:
                v2 = res_data.iloc[1]
                st.markdown(f"""
                <div class="podium-card podium-2">
                    <div class="podium-rank">🥈 JUARA 2</div>
                    <div class="podium-title">{v2['Vendor']}</div>
                    <div class="podium-score">Skor Preferensi (V): <b>{v2['Nilai V']:.5f}</b></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='podium-card'>-</div>", unsafe_allow_html=True)

        # Juara 1
        with pod_cols[1]:
            st.markdown(f"""
            <div class="podium-card podium-1">
                <div class="podium-rank" style="color:#eab308;">🥇 REKOMENDASI UTAMA</div>
                <div class="podium-title" style="font-size: 24px; color: #facc15;">{best_vendor['Vendor']}</div>
                <div class="podium-score" style="font-size: 15px;">Skor Preferensi (V): <b>{best_vendor['Nilai V']:.5f}</b></div>
                <div style="margin-top: 8px; color: #eab308; font-weight: 700; font-size: 13px;">★ PILIHAN TERBAIK ★</div>
            </div>
            """, unsafe_allow_html=True)

        # Juara 3
        with pod_cols[2]:
            if len(res_data) > 2:
                v3 = res_data.iloc[2]
                st.markdown(f"""
                <div class="podium-card podium-3">
                    <div class="podium-rank">🥉 JUARA 3</div>
                    <div class="podium-title">{v3['Vendor']}</div>
                    <div class="podium-score">Skor Preferensi (V): <b>{v3['Nilai V']:.5f}</b></div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='podium-card'>-</div>", unsafe_allow_html=True)

        # Executive Summary
        st.markdown(f"""
        <div class="summary-box">
            <b>📌 Executive Summary:</b><br>
            Berdasarkan matriks pembobotan Weighted Product, <b>{best_vendor['Vendor']}</b> direkomendasikan sebagai vendor penyedia sistem IT terbaik dengan perolehan nilai preferensi tertinggi <b>{best_vendor['Nilai V']:.6f}</b>.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📋 Tabel Peringkat Lengkap")
        table_disp = res_data.copy()
        table_disp["Vektor S"] = table_disp["Vektor S"].apply(lambda x: f"{x:.6f}")
        table_disp["Nilai V"] = table_disp["Nilai V"].apply(lambda x: f"{x:.6f}")
        st.dataframe(table_disp, use_container_width=True, hide_index=True)

        # Export Excel
        out_excel = BytesIO()
        with pd.ExcelWriter(out_excel, engine="openpyxl") as wr:
            st.session_state.vendors.to_excel(wr, sheet_name="Data Vendor", index=False)
            st.session_state.criteria.to_excel(wr, sheet_name="Kriteria", index=False)
            res_data.to_excel(wr, sheet_name="Hasil Ranking WP", index=False)
        out_excel.seek(0)
        
        st.download_button(
            "📥 Download Laporan Lengkap (.xlsx)",
            data=out_excel,
            file_name="Laporan_SPK_Vendor_WP.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

# =========================
# TAB 3: VISUALISASI & RADAR CHART
# =========================
with tab_chart:
    if st.session_state.last_result is not None:
        res_data = st.session_state.last_result["result"]
        
        c_ch1, c_ch2 = st.columns(2)
        
        with c_ch1:
            st.markdown("### 📊 Perbandingan Skor Preferensi (Vektor V)")
            chart_df = res_data.set_index("Vendor")[["Nilai V"]]
            st.bar_chart(chart_df, color="#3b82f6")

        with c_ch2:
            st.markdown("### 🕸️ Spider / Radar Chart (Profil Vendor)")
            
            crit_names = st.session_state.criteria["Kriteria"].tolist()
            crit_codes = st.session_state.criteria["Kode"].tolist()
            
            fig_radar = go.Figure()
            top_vendors = res_data.head(4)["Vendor"].tolist()
            
            for v_name in top_vendors:
                v_row = st.session_state.vendors[st.session_state.vendors["Vendor"] == v_name]
                if not v_row.empty:
                    val_list = [v_row[code].values[0] for code in crit_codes]
                    val_closed = val_list + [val_list[0]]
                    crit_closed = crit_names + [crit_names[0]]
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=val_closed,
                        theta=crit_closed,
                        fill='toself',
                        name=v_name,
                        opacity=0.4
                    ))

            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], color="#94a3b8", gridcolor="#334155"),
                    angularaxis=dict(color="#f8fafc", gridcolor="#334155"),
                    bgcolor="#151c2c"
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e2e8f0"),
                showlegend=True,
                legend=dict(font=dict(color="#e2e8f0")),
                margin=dict(l=40, r=40, t=30, b=30),
                height=380
            )
            st.plotly_chart(fig_radar, use_container_width=True)

# =========================
# TAB 4: DETAIL PERHITUNGAN WP
# =========================
with tab_math:
    st.markdown("### 📐 Tahapan Perhitungan Weighted Product (WP)")
    
    if st.session_state.last_result is not None:
        det_crit = st.session_state.criteria[["Kode", "Kriteria", "Bobot (%)", "Jenis"]].copy()
        det_crit["Bobot Ternormalisasi (Wj)"] = st.session_state.last_result["normalized"]
        det_crit["Pangkat Bobot WP"] = st.session_state.last_result["wp_weights"]
        
        st.markdown("##### 1. Normalisasi Bobot Kriteria")
        st.dataframe(
            det_crit,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Bobot Ternormalisasi (Wj)": st.column_config.NumberColumn(format="%.5f"),
                "Pangkat Bobot WP": st.column_config.NumberColumn(format="%.5f")
            }
        )

        st.markdown("##### 2. Rumus dan Kaidah Weighted Product")
        st.markdown("""
        <div class="formula-card">
            <b>Langkah 1 (Normalisasi Bobot):</b><br>
            <code>Wj = wj / Σwj</code> (Sehingga total seluruh bobot menjadi 1).<br><br>
            <b>Langkah 2 (Menghitung Nilai Vektor S):</b><br>
            <code>Si = Π (xij)<sup>Wj</sup></code><br>
            • Jika Kriteria <b>Benefit</b>: Pangkat bobot positif (+Wj).<br>
            • Jika Kriteria <b>Cost</b>: Pangkat bobot bernilai negatif (-Wj).<br><br>
            <b>Langkah 3 (Menghitung Nilai Vektor V / Preferensi):</b><br>
            <code>Vi = Si / ΣSi</code> (Alternatif dengan Vi terbesar adalah vendor terbaik).
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("VendorSelect Pro • Sistem Pendukung Keputusan Pemilihan Vendor IT • Weighted Product (WP)")