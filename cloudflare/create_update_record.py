import requests
import json
import sys

# ====================================================================
# 1. CẤU HÌNH CHUNG
# ====================================================================

API_TOKEN="thay_api_token_cua_ban_vao_day" #API cloud flare
ZONE_ID="thay_zone_id_cua_ban_vao_day" # ZONE ID cloud flare
DOMAIN="domain_cua_ban"  # Tên miền chính của bạn
EXTERNAL_IP = "external_ip_vm"

# Danh sách các subdomain cần tạo/update
SUBDOMAINS = [
    "argocd",
    "gitlab",
    "jenkins",
    "kuma",
    "registry"
]

# Bật đám mây cam (Proxy)? True = Bật, False = Tắt
PROXIED = True

BASE_URL = "https://api.cloudflare.com/client/v4"
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# ====================================================================
# 2. HÀM XỬ LÝ (FUNCTION)
# ====================================================================

def manage_dns_record(subdomain):
    # Xử lý tên đầy đủ
    full_record_name = f"{subdomain}.{DOMAIN}"

    print(f"--------------------------------------------------")
    print(f"📡 Đang xử lý: {full_record_name}")

    # 1. Kiểm tra record đã tồn tại chưa
    # API: List DNS Records
    params = {"type": "A", "name": full_record_name}
    try:
        resp = requests.get(f"{BASE_URL}/zones/{ZONE_ID}/dns_records", headers=HEADERS, params=params)
        data = resp.json()
    except Exception as e:
        print(f"❌ Lỗi kết nối API Cloudflare: {e}")
        return

    # Kiểm tra success
    if not data.get("success"):
        print(f"❌ Lỗi API: {data.get('errors')}")
        return

    results = data.get("result", [])

    # Payload chung cho Create/Update
    record_data = {
        "type": "A",
        "name": full_record_name,
        "content": EXTERNAL_IP,
        "ttl": 1,  # 1 = Automatic
        "proxied": PROXIED
    }

    if not results:
        # --- TRƯỜNG HỢP 1: TẠO MỚI (CREATE) ---
        print(f"🆕 Record chưa tồn tại. Đang tạo mới -> {EXTERNAL_IP}...")
        create_resp = requests.post(
            f"{BASE_URL}/zones/{ZONE_ID}/dns_records",
            headers=HEADERS,
            json=record_data
        )
        if create_resp.json().get("success"):
            print("✅ Đã TẠO thành công!")
        else:
            print(f"❌ Tạo thất bại: {create_resp.text}")

    else:
        # --- TRƯỜNG HỢP 2: CẬP NHẬT (UPDATE) ---
        record_id = results[0]["id"]
        existing_ip = results[0]["content"]

        if existing_ip == EXTERNAL_IP:
            print(f"👌 IP chưa đổi ({existing_ip}). Bỏ qua.")
        else:
            print(f"🔄 IP cũ ({existing_ip}) khác IP mới. Đang cập nhật -> {EXTERNAL_IP}...")
            update_resp = requests.put(
                f"{BASE_URL}/zones/{ZONE_ID}/dns_records/{record_id}",
                headers=HEADERS,
                json=record_data
            )
            if update_resp.json().get("success"):
                print("✅ Đã CẬP NHẬT thành công!")
            else:
                print(f"❌ Cập nhật thất bại: {update_resp.text}")

# ====================================================================
# 3. CHẠY CHƯƠNG TRÌNH
# ====================================================================

if __name__ == "__main__":
    # Lấy IP một lần dùng chung cho tất cả
    print(f"🚀 Bắt đầu đồng bộ DNS Cloudflare")
    print(f"🌍 IP Public hiện tại: {EXTERNAL_IP}")
    print(f"📋 Danh sách record: {SUBDOMAINS}")

    for sub in SUBDOMAINS:
        manage_dns_record(sub)

    print("--------------------------------------------------")
    print("🎉 Hoàn tất!")
