import streamlit as st
import pandas as pd
import datetime

# ==========================================
# 1. CẤU HÌNH TRANG & CSS OVERRIDE
# ==========================================
st.set_page_config(page_title="Lịch đấu World Cup 2026", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")

# Inject CSS để ép giao diện Streamlit giống hệt thiết kế UI/UX chuyên nghiệp
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

    /* Tiêu đề chính có thanh màu dọc bên trái */
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
        background-color: #4f46e5; /* Màu xanh tím */
        border-radius: 4px;
    }

    /* Tùy chỉnh Streamlit Radio thành Segmented Control (Tabs) */
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
    /* Ẩn dấu chấm radio */
    div.row-widget.stRadio > div > label > div:first-child {
        display: none;
    }
    div.row-widget.stRadio > div > label > div:nth-child(2) {
        margin-left: 0;
        font-weight: 600;
        color: #4b5563;
        font-size: 15px;
    }
    /* Trạng thái Active của Tab */
    div.row-widget.stRadio > div > label[data-checked="true"] {
        background-color: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    div.row-widget.stRadio > div > label[data-checked="true"] > div:nth-child(2) {
        color: #b91c1c; /* Màu đỏ đô */
    }

    /* Style cho Match Card */
    .match-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .match-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-color: #d1d5db;
    }
    .stadium-text {
        font-size: 13px;
        color: #9ca3af;
        margin-bottom: 12px;
        font-weight: 500;
    }
    .score-row {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        gap: 30px;
    }
    .team {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;
    }
    .team.home { justify-content: flex-end; }
    .team.away { justify-content: flex-start; }
    .team-name {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
    }
    .flag {
        width: 28px;
        height: 20px;
        border-radius: 3px;
        object-fit: cover;
        border: 1px solid #f3f4f6;
    }
    .score-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 100px;
    }
    .score-number {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
        letter-spacing: 2px;
    }
    .status-pill {
        font-size: 12px;
        padding: 4px 12px;
        border-radius: 20px;
        background-color: #f3f4f6;
        color: #6b7280;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .status-pill.live {
        background-color: #fef2f2;
        color: #ef4444;
    }
    .status-pill.live::before {
        content: "●";
        margin-right: 4px;
        font-size: 10px;
    }
    .match-footer {
        font-size: 13px;
        color: #6b7280;
        margin-top: 12px;
    }

    /* Style cho Group Title / Date Title */
    .section-divider {
        font-size: 20px;
        font-weight: 700;
        color: #1f2937;
        margin: 32px 0 16px 0;
        display: flex;
        align-items: center;
    }
    .section-divider::before {
        content: "";
        display: inline-block;
        width: 4px;
        height: 20px;
        background-color: #10b981;
        margin-right: 12px;
        border-radius: 2px;
    }
    .section-divider.red::before { background-color: #b91c1c; }
    
    /* Bracket CSS */
    .bracket {
        display: flex;
        flex-direction: row;
        width: 100%;
        overflow-x: auto;
        padding: 20px 0;
        background-color: #f8fafc;
        border-radius: 16px;
        min-height: 600px;
    }
    .round {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        width: 300px;
        padding: 0 20px;
        position: relative;
    }
    .round-title {
        text-align: center;
        font-size: 14px;
        font-weight: 700;
        color: #9f1239;
        margin-bottom: 20px;
        text-transform: uppercase;
    }
    .bracket-match {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9;
        margin-bottom: 20px;
        position: relative;
        z-index: 2;
    }
    .b-match-header {
        font-size: 11px;
        color: #b91c1c;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .b-team {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 0;
    }
    .b-flag {
        width: 20px;
        height: 14px;
        background-color: #e2e8f0;
        border-radius: 2px;
        display: inline-block;
        border: 1px solid #cbd5e1;
    }
    .b-team-name {
        font-size: 14px;
        font-weight: 600;
        color: #1e293b;
    }
    
    /* Connector Lines for Bracket */
    .connector {
        position: absolute;
        border: 2px solid #cbd5e1;
        border-left: none;
        z-index: 1;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. DỮ LIỆU MẪU (BACKEND MOCK)
# Ghi chú: Trong thực tế, bạn sẽ dùng pd.read_csv("link_google_sheets") ở đây
# ==========================================
def load_data():
    # Database Các đội bóng & Cờ (Sử dụng FlagCDN để có cờ chuẩn nét)
    teams = {
        "Mexico": "mx", "Nam Phi": "za", 
        "Hàn Quốc": "kr", "CH Czech": "cz",
        "Canada": "ca", "Bosnia & Herz.": "ba",
        "Mỹ": "us", "Paraguay": "py"
    }
    
    # Bảng Matches
    matches_data = [
        {"id": 1, "date_str": "Ngày 12/6", "day": "Thứ 6, 12/6", "time": "20:00", "group": "Bảng A", "stage": "Vòng đấu bảng", 
         "home": "Mexico", "away": "Nam Phi", "home_score": 2, "away_score": 0, "status": "Kết thúc", "stadium": "Estadio Azteca, Mexico City"},
        {"id": 2, "date_str": "Ngày 12/6", "day": "Thứ 6, 12/6", "time": "23:00", "group": "Bảng A", "stage": "Vòng đấu bảng", 
         "home": "Hàn Quốc", "away": "CH Czech", "home_score": 2, "away_score": 1, "status": "Kết thúc", "stadium": "Estadio Akron, Guadalajara"},
        {"id": 3, "date_str": "Ngày 13/6", "day": "Thứ 7, 13/6", "time": "18:00", "group": "Bảng B", "stage": "Vòng đấu bảng", 
         "home": "Canada", "away": "Bosnia & Herz.", "home_score": 1, "away_score": 1, "status": "Kết thúc", "stadium": "BMO Field, Toronto"},
        {"id": 4, "date_str": "Ngày 13/6", "day": "Thứ 7, 13/6", "time": "21:00", "group": "Bảng D", "stage": "Vòng đấu bảng", 
         "home": "Mỹ", "away": "Paraguay", "home_score": 4, "away_score": 1, "status": "Kết thúc", "stadium": "Lumen Field, Seattle"},
        {"id": 5, "date_str": "Ngày 14/6", "day": "Chủ nhật, 14/6", "time": "02:00", "group": "Bảng A", "stage": "Vòng đấu bảng", 
         "home": "CH Czech", "away": "Nam Phi", "home_score": 1, "away_score": 1, "status": "Kết thúc", "stadium": "Mercedes-Benz Stadium, Atlanta"},
        {"id": 6, "date_str": "Ngày 14/6", "day": "Chủ nhật, 14/6", "time": "08:00", "group": "Bảng A", "stage": "Vòng đấu bảng", 
         "home": "Mexico", "away": "Hàn Quốc", "home_score": 1, "away_score": 0, "status": "Đang diễn ra", "stadium": "Estadio Akron, Guadalajara"}
    ]
    df_matches = pd.DataFrame(matches_data)
    
    # Mapping Cờ vào DF
    df_matches['home_flag'] = df_matches['home'].map(lambda x: f"https://flagcdn.com/w80/{teams.get(x, 'un')}.png")
    df_matches['away_flag'] = df_matches['away'].map(lambda x: f"https://flagcdn.com/w80/{teams.get(x, 'un')}.png")
    
    return df_matches

df = load_data()


# ==========================================
# 3. HELPER FUNCTIONS (FRONTEND RENDERERS)
# ==========================================
def render_match_card(row, show_stadium=False):
    """Tạo HTML Component cho một thẻ trận đấu chuyên nghiệp"""
    status_class = "live" if row['status'] == "Đang diễn ra" else ""
    stadium_html = f'<div class="stadium-text">{row["stadium"]}</div>' if show_stadium else ''
    
    # Score format
    if pd.isna(row['home_score']):
        score_text = "vs"
    else:
        score_text = f"{int(row['home_score'])} - {int(row['away_score'])}"

    html = f"""
    <div class="match-card">
        {stadium_html}
        <div class="score-row">
            <div class="team home">
                <span class="team-name">{row['home']}</span>
                <img src="{row['home_flag']}" class="flag" alt="{row['home']}">
            </div>
            
            <div class="score-box">
                <div class="status-pill {status_class}">{row['status']}</div>
                <div class="score-number">{score_text}</div>
            </div>
            
            <div class="team away">
                <img src="{row['away_flag']}" class="flag" alt="{row['away']}">
                <span class="team-name">{row['away']}</span>
            </div>
        </div>
        <div class="match-footer">{row['stage']} • {row['group']}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ==========================================
# 4. MAIN UI LAYOUT
# ==========================================
st.markdown('<div class="main-title">Lịch đấu World Cup 2026</div>', unsafe_allow_html=True)

# Khung điều hướng chính (Sử dụng st.radio được CSS ghi đè thành Segmented Tabs)
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
# TAB 1: XEM THEO NGÀY
# ------------------------------------------
if view_mode == "Xem theo ngày":
    # Lấy danh sách các ngày có trận đấu
    days = df['day'].unique().tolist()
    
    # Dùng radio button tiếp tục làm menu lọc ngày (Nằm ngang)
    selected_day = st.radio("Chọn ngày", ["Tất cả"] + days, horizontal=True, label_visibility="collapsed")
    
    if selected_day == "Tất cả":
        filtered_df = df
    else:
        filtered_df = df[df['day'] == selected_day]
        
    # Group dữ liệu theo Ngày để render
    grouped = filtered_df.groupby('date_str')
    
    for date, group in grouped:
        st.markdown(f'<div class="section-divider">{date}</div>', unsafe_allow_html=True)
        for _, match in group.iterrows():
            render_match_card(match, show_stadium=False)

# ------------------------------------------
# TAB 2: XEM THEO BẢNG
# ------------------------------------------
elif view_mode == "Xem theo bảng":
    groups = sorted(df['group'].unique().tolist())
    
    # Bộ lọc Bảng (Giao diện thuốc viên - Pills)
    selected_group = st.radio("Chọn bảng", groups, horizontal=True, label_visibility="collapsed")
    
    st.markdown(f'<div class="section-divider red" style="text-transform: uppercase;">{selected_group}</div>', unsafe_allow_html=True)
    
    filtered_df = df[df['group'] == selected_group]
    
    for _, match in filtered_df.iterrows():
        # Ở chế độ xem theo bảng, hiển thị Tên Sân Vận Động ở trên cùng (Giống ảnh 2)
        render_match_card(match, show_stadium=True)

# ------------------------------------------
# TAB 3: VÒNG LOẠI TRỰC TIẾP (KNOCKOUT BRACKET)
# ------------------------------------------
elif view_mode == "Vòng loại trực tiếp":
    
    # Sử dụng hoàn toàn Custom HTML/CSS Flexbox để vẽ nhánh đấu
    # Không dùng thư viện ngoài để đảm bảo tính nhẹ và tốc độ
    
    bracket_html = """
    <div class="bracket">
        <!-- CỘT 1: VÒNG 32 ĐỘI -->
        <div class="round">
            <div class="round-title">Vòng 32 Đội</div>
            
            <!-- Trận 73 -->
            <div class="bracket-match">
                <div class="b-match-header">Trận 73 • 02:00 • 29/6</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhì bảng A</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhì bảng B</span></div>
            </div>
            
            <!-- Đường nối giữa trận 73, 75 ra trận 89 -->
            <div class="connector" style="top: 130px; bottom: 310px; right: -20px; width: 20px;"></div>
            <div class="connector" style="top: 220px; right: -40px; width: 20px; border:none; border-top: 2px solid #cbd5e1;"></div>
            
            <!-- Trận 75 -->
            <div class="bracket-match" style="margin-top: 20px;">
                <div class="b-match-header">Trận 75 • 03:30 • 30/6</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhất bảng E</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Hạng ba A/B/C/D/F</span></div>
            </div>
            
            <div style="height: 60px;"></div> <!-- Khoảng trống -->
            
            <!-- Trận 74 -->
            <div class="bracket-match">
                <div class="b-match-header">Trận 74 • 00:00 • 30/6</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhất bảng C</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhì bảng F</span></div>
            </div>
            
            <!-- Đường nối giữa trận 74, 77 ra trận 90 -->
            <div class="connector" style="top: 480px; bottom: -40px; right: -20px; width: 20px;"></div>
            <div class="connector" style="top: 570px; right: -40px; width: 20px; border:none; border-top: 2px solid #cbd5e1;"></div>

            <!-- Trận 77 -->
            <div class="bracket-match" style="margin-top: 20px;">
                <div class="b-match-header">Trận 77 • 00:00 • 1/7</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhì bảng E</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Nhì bảng D</span></div>
            </div>
        </div>
        
        <!-- CỘT 2: VÒNG 16 ĐỘI -->
        <div class="round" style="margin-left: 40px; justify-content: flex-start; padding-top: 0px;">
            <div class="round-title">Vòng 16 Đội</div>
            
            <!-- Trận 89 -->
            <div class="bracket-match" style="margin-top: 130px;">
                <div class="b-match-header">Trận 89 • 00:00 • 5/7</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Thắng trận 73</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Thắng trận 75</span></div>
            </div>
            
            <!-- Trận 90 -->
            <div class="bracket-match" style="margin-top: 180px;">
                <div class="b-match-header">Trận 90 • 04:00 • 5/7</div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Thắng trận 74</span></div>
                <div class="b-team"><span class="b-flag"></span><span class="b-team-name">Thắng trận 77</span></div>
            </div>
        </div>
        
        <!-- CỘT 3: TỨ KẾT (Chỗ trống để mở rộng sau) -->
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
