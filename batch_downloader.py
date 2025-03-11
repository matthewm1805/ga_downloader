import subprocess
import re
import os
import concurrent.futures

# Đường dẫn file dezoomify-rs.exe
DEZOOMIFY_PATH = "./dezoomify-rs.exe"  # Đổi nếu cần
MAX_WORKERS = 4  # Số luồng tải đồng thời

def get_input_file():
    """ Yêu cầu người dùng kéo file vào CMD """
    file_path = input("📂 Hãy kéo file input.txt vào đây và nhấn Enter: ").strip()
    
    # Xóa dấu ngoặc kép nếu có (do Windows tự thêm khi kéo thả)
    if file_path.startswith('"') and file_path.endswith('"'):
        file_path = file_path[1:-1]

    if not os.path.exists(file_path):
        print("❌ Lỗi: File không tồn tại. Hãy kiểm tra lại.")
        return None
    return file_path

def read_urls_from_file(file_path):
    """ Đọc tất cả URL từ file txt """
    with open(file_path, 'r', encoding='utf-8') as file:
        urls = re.findall(r'https?://\S+', file.read())  # Tìm tất cả URL
    return urls

def download_image_with_dezoomify(url):
    """ Chạy dezoomify-rs.exe để tải ảnh từ URL với mức zoom tối ưu """
    if not os.path.exists(DEZOOMIFY_PATH):
        print(f"❌ Lỗi: Không tìm thấy {DEZOOMIFY_PATH}")
        return

    try:
        print(f"🔗 Bắt đầu tải: {url}")

        process = subprocess.Popen(
            [DEZOOMIFY_PATH, url], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
            text=True
        )

        zoom_levels = []
        for line in iter(process.stdout.readline, ''):
            print(line.strip())

            if "Which level do you want to download?" in line:
                if zoom_levels:
                    choice = 3 if 3 in zoom_levels else max(zoom_levels)
                    print(f"✅ Chọn mức zoom: {choice}")
                    process.stdin.write(f"{choice}\n")
                    process.stdin.flush()
                break

            match = re.findall(r'(\d+)\..+?\(\s*(\d+) x\s*(\d+)', line)
            if match:
                zoom_levels.extend(int(opt[0]) for opt in match)

        process.communicate()
        print(f"✅ Hoàn thành tải: {url}")

    except Exception as e:
        print(f"❌ Lỗi khi tải {url}: {e}")

if __name__ == "__main__":
    input_file = get_input_file()
    if input_file:
        urls = read_urls_from_file(input_file)

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            executor.map(download_image_with_dezoomify, urls)

        print("🎉 Hoàn tất tải tất cả ảnh!")
