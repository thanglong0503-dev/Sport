import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
import json
import os

# =========================================
# 1. CẤU HÌNH KẾT NỐI GOOGLE SHEETS
# =========================================
# Định nghĩa quyền truy cập
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Trên máy tính (Local): Trỏ đường dẫn trực tiếp tới file JSON bạn tải về ở Bước 1
# Khi đưa lên GitHub, chúng ta sẽ dùng os.environ để bảo mật
try:
    # Thử lấy từ biến môi trường (Khi chạy trên GitHub Actions)
    creds_dict = json.loads(os.environ.get('GOOGLE_SHEETS_CREDENTIALS'))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
except TypeError:
    # Nếu chạy ở máy tính (Local), đọc file JSON trực tiếp
    creds = ServiceAccountCredentials.from_json_keyfile_name('TEN_FILE_BIMAT_CUA_BAN.json', scope)

client = gspread.authorize(creds)

# Mở Google Sheets bằng Link của bạn
sheet_url = "https://docs.google.com/spreadsheets/d/1MjLscwg33h8ljGSo6k2rs13ZckSMUZI4JNCxBB_X3Yg/edit"
spreadsheet = client.open_by_url(sheet_url)
worksheet = spreadsheet.worksheet("Matches") # Điền đúng tên Tab trang tính của bạn

# =========================================
# 2. HÀM LẤY DỮ LIỆU TỪ API BÓNG ĐÁ
# =========================================
def fetch_live_data():
    # Ví dụ gọi API-Football (Bạn thay bằng logic của soccerdata hoặc api khác tùy ý)
    url = "https://v3.football.api-sports.io/fixtures"
    headers = {
        "x-apisports-key": "ĐIỀN_API_KEY_CỦA_BAN_VAO_DAY" # API Key lấy từ api-football.com
    }
    # Giả sử lấy dữ liệu World Cup (League ID 1)
    params = {"league": "1", "season": "2026"}
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    # Bóc tách JSON thành danh sách (list) khớp với các cột trên Google Sheets
    matches = []
    for item in data.get('response', []):
        # Format lại dữ liệu sao cho giống hệt với bảng nhập tay hiện tại
        match_info = [
            item['fixture']['id'],                                  # id
            item['fixture']['date'][:10],                           # day (YYYY-MM-DD)
            item['fixture']['date'][11:16],                         # time
            item['league']['round'],                                # group/vòng
            "Vòng đấu bảng",                                        # stage
            item['teams']['home']['name'],                          # home
            item['teams']['away']['name'],                          # away
            item['goals']['home'] if item['goals']['home'] is not None else "", # home_score
            item['goals']['away'] if item['goals']['away'] is not None else "", # away_score
            "Kết thúc" if item['fixture']['status']['short'] == 'FT' else ("Đang diễn ra" if item['fixture']['status']['short'] in ['1H', '2H', 'HT'] else "Sắp diễn ra"), # status
            item['fixture']['venue']['name']                        # stadium
        ]
        matches.append(match_info)
    
    # Đặt tên cột đúng chuẩn với file Sheets
    columns = ['id', 'day', 'time', 'group', 'stage', 'home', 'away', 'home_score', 'away_score', 'status', 'stadium']
    return pd.DataFrame(matches, columns=columns)

# =========================================
# 3. GHI ĐÈ DỮ LIỆU MỚI LÊN GOOGLE SHEETS
# =========================================
if __name__ == "__main__":
    print("Bắt đầu lấy dữ liệu mới từ API...")
    try:
        df_new_data = fetch_live_data()
        
        if not df_new_data.empty:
            # Xóa sạch dữ liệu cũ trong Tab (Chỉ giữ lại dòng Tiêu đề)
            worksheet.clear()
            
            # Ghi đè toàn bộ DataFrame mới lên
            worksheet.update([df_new_data.columns.values.tolist()] + df_new_data.values.tolist())
            print("Cập nhật Google Sheets thành công!")
        else:
            print("Không lấy được dữ liệu mới.")
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")
