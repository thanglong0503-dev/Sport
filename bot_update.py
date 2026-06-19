import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import requests
import json
import os

# =========================================
# 1. CẤU HÌNH KẾT NỐI GOOGLE SHEETS
# =========================================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

try:
    # Lấy thông tin xác thực từ GitHub Actions (Khi deploy tự động)
    creds_dict = json.loads(os.environ.get('GOOGLE_SHEETS_CREDENTIALS'))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
except TypeError:
    # Nếu chạy ở máy tính (Local), đổi tên file này thành file JSON bí mật của bạn
    creds = ServiceAccountCredentials.from_json_keyfile_name('TEN_FILE_BIMAT_CUA_BAN.json', scope)

client = gspread.authorize(creds)

# Mở Google Sheets bằng Link của bạn
sheet_url = "https://docs.google.com/spreadsheets/d/1MjLscwg33h8ljGSo6k2rs13ZckSMUZI4JNCxBB_X3Yg/edit"
spreadsheet = client.open_by_url(sheet_url)
worksheet = spreadsheet.worksheet("Matches")

# =========================================
# 2. HÀM LẤY DỮ LIỆU TỪ API-FOOTBALL
# =========================================
def fetch_live_data():
    print("Đang gọi API lấy dữ liệu World Cup 2026...")
    url = "https://v3.football.api-sports.io/fixtures"
    
    # Gắn API Key bạn vừa cung cấp
    headers = {
        "x-apisports-key": "ea509f4bca00d9a7d3778fb6f16f2a2e"
    }
    
    # Lấy giải World Cup (id: 1), mùa 2026, và tự động chuyển giờ sang GMT+7 (Hồ Chí Minh)
    params = {
        "league": "1", 
        "season": "2026",
        "timezone": "Asia/Ho_Chi_Minh"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        matches = []
        for item in data.get('response', []):
            fixture = item.get('fixture', {})
            teams = item.get('teams', {})
            goals = item.get('goals', {})
            league = item.get('league', {})
            
            # Lấy ngày và giờ chuẩn VN
            date_full = fixture.get('date', '')
            day = date_full[:10] if len(date_full) >= 10 else ""
            time_str = date_full[11:16] if len(date_full) >= 16 else ""
            
            # Phân loại trạng thái trận đấu
            status_short = fixture.get('status', {}).get('short', '')
            status = "Sắp diễn ra"
            if status_short in ['FT', 'AET', 'PEN']:
                status = "Kết thúc"
            elif status_short in ['1H', 'HT', '2H', 'ET', 'BT', 'P']:
                status = "Đang diễn ra"
                
            # Tránh lỗi Null khi trận đấu chưa bắt đầu
            home_score = goals.get('home')
            away_score = goals.get('away')
            
            # Format lại dữ liệu sao cho khớp với các cột trên Google Sheets
            match_info = [
                fixture.get('id', ''),
                day,
                time_str,
                league.get('round', ''), # Tên Vòng/Bảng từ API
                "World Cup 2026",        # Ghi chú Giải
                teams.get('home', {}).get('name', ''),
                teams.get('away', {}).get('name', ''),
                int(home_score) if home_score is not None else "",
                int(away_score) if away_score is not None else "",
                status,
                fixture.get('venue', {}).get('name', '')
            ]
            matches.append(match_info)
        
        # Đặt tên cột đúng chuẩn để đẩy lên Sheets
        columns = ['id', 'day', 'time', 'group', 'stage', 'home', 'away', 'home_score', 'away_score', 'status', 'stadium']
        df = pd.DataFrame(matches, columns=columns)
        
        # Sắp xếp theo thời gian thi đấu cho gọn gàng
        df = df.sort_values(by=['day', 'time'])
        return df
        
    except Exception as e:
        print(f"Lỗi khi kết nối API: {e}")
        return pd.DataFrame()

# =========================================
# 3. GHI ĐÈ DỮ LIỆU MỚI LÊN GOOGLE SHEETS
# =========================================
if __name__ == "__main__":
    df_new_data = fetch_live_data()
    
    if not df_new_data.empty:
        # Xóa sạch dữ liệu cũ trong Tab (Chỉ giữ lại dòng Tiêu đề)
        worksheet.clear()
        
        # Ghi đè toàn bộ DataFrame mới lên
        worksheet.update([df_new_data.columns.values.tolist()] + df_new_data.fillna("").values.tolist())
        print(f"✅ Đã cập nhật thành công {len(df_new_data)} trận đấu lên Google Sheets!")
    else:
        print("❌ Không có dữ liệu để cập nhật.")
