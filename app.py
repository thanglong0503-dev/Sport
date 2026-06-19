import streamlit as st
import pandas as pd

# 🔴 THAY THẾ LINK GOOGLE SHEETS CỦA BẠN VÀO ĐÂY
SHEET_URL = "https://docs.google.com/spreadsheets/d/1MjLscwg33h8ljGSo6k2rs13ZckSMUZI4JNCxBB_X3Yg/edit?usp=sharing"

# Hàm tự động chuyển đổi link Sheets sang định dạng CSV để Pandas đọc trực tiếp
def get_csv_url(base_url, sheet_name):
    try:
        sheet_id = base_url.split("/d/")[1].split("/")[0]
        return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    except IndexError:
        return None

# Cấu hình giao diện ứng dụng
st.set_page_config(page_title="World Cup Tracker", page_icon="🏆", layout="wide")

st.title("🏆 World Cup 2026 Live Tracker")
st.write("Dữ liệu được đồng bộ trực tiếp từ Google Sheets. Bạn chỉ cần cập nhật file Sheets, website sẽ tự đổi theo!")

# Tạo nút bấm thủ công để xóa cache và tải lại dữ liệu mới nhất nếu cần
if st.button("🔄 Làm mới dữ liệu (Refresh)"):
    st.cache_data.clear()
    st.toast("Đang tải lại dữ liệu mới nhất...", icon="ℹ️")

# Đọc dữ liệu từ Google Sheets (Sử dụng cache để tối ưu tốc độ tải trang)
@st.cache_data(ttl=60) # Tự động xóa cache sau mỗi 60 giây để cập nhật dữ liệu mới
def load_data_from_sheets(url):
    url_matches = get_csv_url(url, "Matches")
    url_standings = get_csv_url(url, "Standings")
    
    matches = pd.read_csv(url_matches)
    standings = pd.read_csv(url_standings)
    return matches, standings

try:
    matches_df, standings_df = load_data_from_sheets(SHEET_URL)
    
    # Thiết kế giao diện Tabs
    tab1, tab2 = st.tabs(["📅 Lịch thi đấu & Kết quả", "📊 Bảng xếp hạng"])
    
    with tab1:
        st.subheader("Danh sách trận đấu vòng bảng")
        # Hiển thị bảng dữ liệu lịch thi đấu mượt mà
        st.dataframe(matches_df, use_container_width=True, hide_index=True)
        
    with tab2:
        st.subheader("Cập nhật vị trí các đội bóng")
        if 'Bảng' in standings_df.columns:
            # Tự động gom nhóm theo các Bảng (A, B, C...) có trong file Sheets
            available_groups = sorted(standings_df['Bảng'].unique())
            
            # Hiển thị mỗi bảng trong một ô đóng mở (Expander) cho gọn
            for group in available_groups:
                with st.expander(f"Bảng {group}", expanded=True):
                    group_data = standings_df[standings_df['Bảng'] == group].sort_values(by=['Điểm', 'Hệ số'], ascending=False)
                    st.dataframe(group_data, use_container_width=True, hide_index=True)
        else:
            st.dataframe(standings_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error("Không thể kết nối tới Google Sheets của bạn!")
    st.info("Vui lòng kiểm tra lại: 1. Quyền chia sẻ link (Anyone with link can view) | 2. Tên 2 tab phải chuẩn xác là 'Matches' và 'Standings'.")
