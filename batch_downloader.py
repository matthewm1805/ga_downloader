import subprocess
import re
import os
import concurrent.futures

# Đường dẫn file dezoomify-rs.exe
DEZOOMIFY_PATH = "./dezoomify-rs.exe"  # Đổi nếu cần
MAX_WORKERS = 4  # Số luồng tải đồng thời

def get_input():
    """Yêu cầu người dùng nhập URL trực tiếp hoặc kéo file vào CMD"""
    user_input = input("📂 Kéo file input.txt hoặc nhập URL trực tiếp rồi nhấn Enter (nhấn Ctrl+C để thoát): ").strip()
    
    # Xóa dấu ngoặc kép nếu có (do Windows tự thêm khi kéo thả)
    if user_input.startswith('"') and user_input.endswith('"'):
        user_input = user_input[1:-1]

    # Kiểm tra xem input có phải là URL không
    if re.match(r'^https?://\S+', user_input):
        return "url", user_input
    
    # Nếu không phải URL, coi như là đường dẫn file
    if not os.path.exists(user_input):
        print("❌ Lỗi: File không tồn tại hoặc URL không hợp lệ. Hãy kiểm tra lại.")
        return None, None
    return "file", user_input

def read_urls_from_file(file_path):
    """Đọc tất cả URL từ file txt"""
    with open(file_path, 'r', encoding='utf-8') as file:
        urls = re.findall(r'https?://\S+', file.read())  # Tìm tất cả URL
    return urls

def download_image_with_dezoomify(url):
    """Chạy dezoomify-rs.exe để tải ảnh từ URL với mức zoom tối ưu"""
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
                    choice = 4 if 4 in zoom_levels else max(zoom_levels)
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

def main():
    while True:
        try:
            input_type, input_value = get_input()
            
            if input_type and input_value:
                if input_type == "url":
                    urls = [input_value]  # Chỉ một URL duy nhất
                else:  # input_type == "file"
                    urls = read_urls_from_file(input_value)

                with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    executor.map(download_image_with_dezoomify, urls)

                print("🎉 Hoàn tất tải tất cả ảnh!")
                print("-" * 50)  # Thêm đường kẻ để phân biệt các lần chạy

        except KeyboardInterrupt:
            print("\n👋 Đã thoát chương trình!")
            break
        except Exception as e:
            print(f"❌ Lỗi không mong muốn: {e}")
            print("-" * 50)

if __name__ == "__main__":
    main()
