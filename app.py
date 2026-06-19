import streamlit as st
import pandas as pd
import datetime

# ==========================================
# 1. CẤU HÌNH TRANG & CSS OVERRIDE
# ==========================================
st.set_page_config(page_title="Lịch đấu World Cup 2026", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* Reset & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: #1a1a1a;
    }
    
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }

    .main-title {
        font-size: 32px;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 24px;
        position: relative;
        padding-left: 16px;
    }
    .main-title::before {
        content: "";
        position: absolute;
        left: 0;
        top: 4px;
        bottom: 4px;
        width: 6px;
        background-color: #4f46e5;
        border-radius: 4px;
    }

    div.row-widget.stRadio > div {
        display: flex;
        flex-direction: row;
        background-color: #f3f4f6;
        padding: 4px;
        border-radius: 8px;
        width: fit-content;
        gap: 0;
    }
    div.row-widget.stRadio > div > label {
        background-color: transparent;
        padding: 10px 24px;
        border-radius: 6px;
        cursor: pointer;
        margin: 0;
        transition: all 0.2s;
    }
    div.row-widget.stRadio > div > label > div:first-child { display: none; }
    div.row-widget.stRadio > div > label > div:nth-child(2) {
        margin-left: 0; font-weight: 600; color: #4b5563; font-size: 15px;
    }
    div.row-widget.stRadio > div > label[data-checked="true"] {
        background-color: #ffffff; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    div.row-widget.stRadio > div > label[data-checked="true"] > div:nth-child(2) { color: #b91c1c; }

    .match-card {
        background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px;
        padding: 20px; margin-bottom: 16px; display: flex; flex-direction: column;
        align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .match-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-color: #d1d5db; }
    .stadium-text { font-size: 13px; color: #9ca3af; margin-bottom: 12px; font-weight: 500; }
    .score-row { display: flex; align-items: center; justify-content: center; width: 100%; gap: 30px; }
    .team { display: flex; align-items: center; gap: 12px; flex: 1; }
    .team.home { justify-content: flex-end; }
    .team.away { justify-content: flex-start; }
    .team-name { font-size: 18px; font-weight: 600; color: #111827; }
    .flag { width: 28px; height: 20px; border-radius: 3px; object-fit: cover; border: 1px solid #f3f4f6; }
    .score-box { display: flex; flex-direction: column; align-items: center; min-width: 100px; }
    .score-number { font-size: 28px; font-weight: 700; color: #111827; letter-spacing: 2px; }
    .status-pill {
        font-size: 12px; padding: 4px 12px; border-radius: 20px;
        background-color: #f3f4f6; color: #6b7280; font-weight: 500; margin-bottom: 8px;
    }
    .status-pill.live { background-color: #fef2f2; color: #ef4444; }
    .status-pill.live::before { content: "●"; margin-right: 4px; font-size: 10px; }
    .match-footer { font-size: 13px; color: #6b7280; margin-top: 12px; }

    .section-divider {
        font-size: 20px; font-weight: 700; color: #1f2937; margin: 32px 0 16px 0;
        display: flex; align-items: center;
    }
    .section-divider::before {
        content: ""; display: inline-block; width: 4px; height: 20px;
        background-color: #10b981; margin-right: 12px; border-radius: 2px;
    }
    .section-divider.red::before { background-color: #b91c1c; }
    
    .bracket {
        display: flex; flex-direction: row; width: 100%; overflow-x: auto;
        padding: 20px 0; background-color: #f8fafc; border-radius: 16px; min-height: 600px;
    }
    .round {
        display: flex; flex-direction: column; justify-content: space-around;
        width: 300px; padding: 0 20px; position: relative;
    }
    .round-title {
        text-align: center; font-size: 14px; font-weight: 700; color: #9f1239;
        margin-bottom: 20px; text-transform: uppercase;
    }
    .bracket-match {
        background: #ffffff; border-radius: 12px; padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #f1f5f9;
        margin-bottom: 20px; position: relative; z-index: 2;
    }
    .b-match-header { font-size: 11px; color: #b91c1c; font-weight: 600; margin-bottom: 12px; }
    .b-team { display: flex; align-items: center; gap: 10px; padding: 6px 0; }
    .b-flag {
        width: 20px; height: 14px; background-color: #e2e8f0;
        border-radius: 2px; display: inline-block; border: 1px solid #cbd5e1;
    }
    .b-team-name { font-size: 14px; font-weight: 600; color: #1e293b; }
    .connector { position: absolute; border: 2px solid #cbd5e1; border-left: none; z-index: 1; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. KẾT NỐI DỮ LIỆU TỪ GOOGLE SHEETS
# ==========================================

@st.cache_data(ttl=60)
def load_data():
    sheet_csv_url = "https://docs.google.com/spreadsheets/d/1MjLscwg33h8ljGSo6k2rs13ZckSMUZI4JNCxBB_X3Yg/export?format=csv&gid=0"
    try:
        df_matches = pd.read_csv(sheet_csv_url)
        col_mapping = {
            'Trận': 'id', 'Ngày': 'day', 'Giờ (VN)': 'time', 'Bảng': 'group',
            'Vòng': 'stage', 'Đội 1': 'home', 'Đội 2': 'away',
            'Tỷ số 1': 'home_score', 'Tỷ số 2': 'away_score',
            'Trạng thái': 'status', 'Sân': 'stadium'
        }
        df_matches = df_matches.rename(columns=col_mapping)
        if 'day' in df_matches.columns:
             df_matches['date_str'] = df_matches['day']
    except Exception as e:
        st.error(f"⚠️ Lỗi kết nối Google Sheets: {e}")
        return pd.DataFrame()

    # Cập nhật danh sách 32 đội WC 2022 để test
    teams = {
        "Qatar": "qa", "Ecuador": "ec", "Senegal": "sn", "Netherlands": "nl",
        "England": "gb-eng", "Iran": "ir", "USA": "us", "Wales": "gb-wls",
        "Argentina": "ar", "Saudi Arabia": "sa", "Mexico": "mx", "Poland": "pl",
        "France": "fr", "Australia": "au", "Denmark": "dk", "Tunisia": "tn",
        "Spain": "es", "Costa Rica": "cr", "Germany": "de", "Japan": "jp",
        "Belgium": "be", "Canada": "ca", "Morocco": "ma", "Croatia": "hr",
        "Brazil": "br", "Serbia": "rs", "Switzerland": "ch", "Cameroon": "cm",
        "Portugal": "pt", "Ghana": "gh", "Uruguay": "uy", "South Korea": "kr",
        "Nam Phi": "za", "CH Czech": "cz", "Bosnia & Herz.": "ba", "Paraguay": "py"
    }
    
    def get_flag_url(team_name):
        if pd.isna(team_name): return "https://flagcdn.com/w80/un.png"
        code = teams.get(str(team_name).strip(), 'un')
        return f"https://flagcdn.com/w80/{code}.png"
        
    if 'home' in df_matches.columns and 'away' in df_matches.columns:
        df_matches['home_flag'] = df_matches['home'].map(get_flag_url)
        df_matches['away_flag'] = df_matches['away'].map(get_flag_url)
    
    return df_matches

df = load_data()

# ==========================================
# 3. HELPER FUNCTIONS (FRONTEND RENDERERS)
# ==========================================
def render_match_card(row, show_stadium=False):
    status = str(row.get('status', ''))
    stadium = str(row.get('stadium', ''))
    home_team = str(row.get('home', 'Chưa xác định'))
    away_team = str(row.get('away', 'Chưa xác định'))
    stage = str(row.get('stage', ''))
    group = str(row.get('group', ''))
    home_flag = str(row.get('home_flag', 'https://flagcdn.com/w80/un.png'))
    away_flag = str(row.get('away_flag', 'https://flagcdn.com/w80/un.png'))
    time = str(row.get('time', ''))

    status_class = "live" if status.lower() in ["đang diễn ra", "live"] else ""
    stadium_html = f'<div class="stadium-text">{stadium}</div>' if show_stadium and stadium and stadium != 'nan' else ''
    
    home_score = row.get('home_score')
    away_score = row.get('away_score')
    
    if pd.isna(home_score) or pd.isna(away_score) or str(home_score).strip() == "" or str(away_score).strip() == "":
        score_text = time if time and time != 'nan' else "vs"
    else:
        try:
             score_text = f"{int(float(home_score))} - {int(float(away_score))}"
        except ValueError:
             score_text = "vs"

# ĐOẠN HTML NÀY ĐÃ ĐƯỢC ĐẨY SÁT LỀ TRÁI HOÀN TOÀN
    html = f"""
<div class="match-card">
    {stadium_html}
    <div class="score-row">
        <div class="team home">
            <span class="team-name">{home_team}</span>
            <img src="{home_flag}" class="flag" alt="{home_team}">
        </div>
        <div class="score-box">
            <div class="status-pill {status_class}">{status if status != 'nan' else 'Sắp diễn ra'}</div>
            <div class="score-number">{score_text}</div>
        </div>
        <div class="team away">
            <img src="{away_flag}" class="flag" alt="{away_team}">
            <span class="team-name">{away_team}</span>
        </div>
    </div>
    <div class="match-footer">{stage if stage != 'nan' else ''} {('• ' + group) if group and group != 'nan' else ''}</div>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 4. MAIN UI LAYOUT
# ==========================================
st.markdown('<div class="main-title">Lịch đấu World Cup 2026</div>', unsafe_allow_html=True)

if df.empty:
    st.warning("Không có dữ liệu để hiển thị. Vui lòng kiểm tra lại Google Sheets.")
    st.stop()

col_nav, col_empty, col_search = st.columns([6, 1, 3])
with col_nav:
    view_mode = st.radio(
        "Navigation",
        ["Xem theo ngày", "Xem theo bảng", "Vòng loại trực tiếp"],
        horizontal=True,
        label_visibility="collapsed"
    )
with col_search:
    st.markdown('<div style="text-align: right; font-size: 12px; color: #9ca3af; margin-top: 10px;">* Giờ thi đấu: GMT+7 Hanoi, Bangkok, Jakarta</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------------------------------
if view_mode == "Xem theo ngày":
    if 'day' in df.columns:
        days = df['day'].dropna().unique().tolist()
        if days:
            selected_day = st.radio("Chọn ngày", ["Tất cả"] + days, horizontal=True, label_visibility="collapsed")
            if selected_day == "Tất cả":
                filtered_df = df
            else:
                filtered_df = df[df['day'] == selected_day]
                
            if 'date_str' in filtered_df.columns:
                grouped = filtered_df.groupby('date_str')
                for date, group in grouped:
                    st.markdown(f'<div class="section-divider">{date}</div>', unsafe_allow_html=True)
                    for _, match in group.iterrows():
                        render_match_card(match, show_stadium=False)
            else:
                 st.write("Cột 'date_str' không tồn tại.")
        else:
            st.write("Chưa có dữ liệu ngày thi đấu.")
    else:
        st.error("Cột 'Ngày' hoặc 'day' không tồn tại trong dữ liệu. Vui lòng kiểm tra Google Sheets.")

# ------------------------------------------
elif view_mode == "Xem theo bảng":
    if 'group' in df.columns:
        groups = [str(g) for g in df['group'].dropna().unique().tolist() if str(g).strip() != "" and str(g).lower() != "nan"]
        groups = sorted(groups)
        if groups:
            selected_group = st.radio("Chọn bảng", groups, horizontal=True, label_visibility="collapsed")
            st.markdown(f'<div class="section-divider red" style="text-transform: uppercase;">{selected_group}</div>', unsafe_allow_html=True)
            
            filtered_df = df[df['group'].astype(str) == selected_group]
            for _, match in filtered_df.iterrows():
                render_match_card(match, show_stadium=True)
        else:
             st.write("Không tìm thấy thông tin Bảng đấu.")
    else:
        st.error("Cột 'Bảng' hoặc 'group' không tồn tại trong dữ liệu.")

# ------------------------------------------
elif view_mode == "Vòng loại trực tiếp":
    bracket_html = """
    <div class="bracket">
        <div class="round">
            <div class="round-title">Vòng 32 Đội</div>
            <div class="bracket-match">
                <div class="b-match-header">Trận 73 • 02:00 • 29/6</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhì bảng A</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhì bảng B</span></div>
            </div>
            <div class="connector" style="top: 130px; bottom: 310px; right: -20px; width: 20px;"></div>
            <div class="connector" style="top: 220px; right: -40px; width: 20px; border:none; border-top: 2px solid #cbd5e1;"></div>
            <div class="bracket-match" style="margin-top: 20px;">
                <div class="b-match-header">Trận 75 • 03:30 • 30/6</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhất bảng E</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Hạng ba A/B/C/D/F</span></div>
            </div>
            <div style="height: 60px;"></div>
            <div class="bracket-match">
                <div class="b-match-header">Trận 74 • 00:00 • 30/6</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhất bảng C</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhì bảng F</span></div>
            </div>
            <div class="connector" style="top: 480px; bottom: -40px; right: -20px; width: 20px;"></div>
            <div class="connector" style="top: 570px; right: -40px; width: 20px; border:none; border-top: 2px solid #cbd5e1;"></div>
            <div class="bracket-match" style="margin-top: 20px;">
                <div class="b-match-header">Trận 77 • 00:00 • 1/7</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhì bảng E</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhì bảng D</span></div>
            </div>
        </div>
        <div class="round" style="margin-left: 40px; justify-content: flex-start; padding-top: 0px;">
            <div class="round-title">Vòng 16 Đội</div>
            <div class="bracket-match" style="margin-top: 130px;">
                <div class="b-match-header">Trận 89 • 00:00 • 5/7</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Thắng trận 73</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Thắng trận 75</span></div>
            </div>
            <div class="bracket-match" style="margin-top: 180px;">
                <div class="b-match-header">Trận 90 • 04:00 • 5/7</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Thắng trận 74</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Thắng trận 77</span></div>
            </div>
        </div>
        <div class="round" style="margin-left: 40px; justify-content: center; opacity: 0.3;">
            <div class="round-title">Tứ Kết</div>
            <div class="bracket-match">
                <div class="b-match-header">Trận 97</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Thắng trận 89</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Thắng trận 90</span></div>
            </div>
        </div>
    </div>
    """
    st.markdown(bracket_html, unsafe_allow_html=True)
