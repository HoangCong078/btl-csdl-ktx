"""Dữ liệu giả và nghiệp vụ của KTX (chạy trong bộ nhớ, tắt server là mất).
Người 2 thay phần dữ liệu bằng truy vấn MySQL, giữ nguyên tên hàm và tên khóa."""
from datetime import datetime, timedelta

# ===================== HẰNG SỐ =====================
GIA_VE_THANG = 100000
TOI_DA_XE = 2           # mỗi sinh viên tối đa 2 xe còn hạn
MIEN_PHI_NGAY = 2       # 2 lượt gửi/lấy miễn phí mỗi xe mỗi ngày
PHI_PHAT_SINH = 3000    # từ lượt thứ 3 trong ngày
DS_LOP = ["B24CQCN01-B", "B24CQCN02-B", "B24CQCN03-B"]
DS_LOAI_PHONG = ["Thường", "Chất lượng cao"]
DS_LOAI_XE = ["Xe đạp", "Xe máy", "Xe điện"]


def ngay_moc(offset=0):
    """Ngày YYYY-MM-DD lệch offset ngày so với hôm nay (để dữ liệu mẫu luôn demo được)."""
    return (datetime.now() + timedelta(days=offset)).strftime("%Y-%m-%d")


def moc(offset=0, gio="08:00"):
    return f"{ngay_moc(offset)} {gio}"


# ===================== DỮ LIỆU GIẢ =====================
ds_sv = [
    {"MaSV": "B24DCCN001", "HoTen": "Nguyễn Văn An", "SoCMT": "001206000001", "NgaySinh": "2006-03-21",
     "GioiTinh": "Nam", "SDT": "0901234567", "Lop": "B24CQCN01-B", "QueQuan": "Hà Nam"},
    {"MaSV": "B24DCCN002", "HoTen": "Trần Thị Bình", "SoCMT": "001206000002", "NgaySinh": "2006-07-09",
     "GioiTinh": "Nữ", "SDT": "0912345678", "Lop": "B24CQCN02-B", "QueQuan": "Nam Định"},
    {"MaSV": "B24DCCN003", "HoTen": "Lê Văn Cường", "SoCMT": "001205000003", "NgaySinh": "2005-11-30",
     "GioiTinh": "Nam", "SDT": "0987654321", "Lop": "B24CQCN03-B", "QueQuan": "Thanh Hóa"},
    {"MaSV": "B24DCCN004", "HoTen": "Phạm Thị Dung", "SoCMT": "001206000004", "NgaySinh": "2006-01-15",
     "GioiTinh": "Nữ", "SDT": "0933111222", "Lop": "B24CQCN01-B", "QueQuan": "Hải Dương"},
    {"MaSV": "B24DCCN005", "HoTen": "Hoàng Minh Đức", "SoCMT": "001206000005", "NgaySinh": "2006-09-02",
     "GioiTinh": "Nam", "SDT": "0944555666", "Lop": "B24CQCN02-B", "QueQuan": "Nghệ An"},
    {"MaSV": "B24DCCN006", "HoTen": "Vũ Thị Hà", "SoCMT": "001206000006", "NgaySinh": "2006-05-27",
     "GioiTinh": "Nữ", "SDT": "", "Lop": "B24CQCN03-B", "QueQuan": "Bắc Ninh"},
]

ds_phong = [
    {"SoPhong": "P101", "LoaiPhong": "Thường", "DonGia": 500000, "SoNguoiToiDa": 4},
    {"SoPhong": "P102", "LoaiPhong": "Thường", "DonGia": 500000, "SoNguoiToiDa": 2},
    {"SoPhong": "P201", "LoaiPhong": "Chất lượng cao", "DonGia": 900000, "SoNguoiToiDa": 2},
]

# NgayKetThuc = None nghĩa là đang ở
ds_dangky_o = [
    {"MaDKO": 1, "MaSV": "B24DCCN001", "SoPhong": "P101", "NgayBatDau": ngay_moc(-60), "NgayKetThuc": None, "DonGiaThangApDung": 500000},
    {"MaDKO": 2, "MaSV": "B24DCCN003", "SoPhong": "P101", "NgayBatDau": ngay_moc(-60), "NgayKetThuc": None, "DonGiaThangApDung": 500000},
    {"MaDKO": 3, "MaSV": "B24DCCN005", "SoPhong": "P101", "NgayBatDau": ngay_moc(-50), "NgayKetThuc": None, "DonGiaThangApDung": 500000},
    {"MaDKO": 4, "MaSV": "B24DCCN002", "SoPhong": "P102", "NgayBatDau": ngay_moc(-60), "NgayKetThuc": None, "DonGiaThangApDung": 500000},
    {"MaDKO": 5, "MaSV": "B24DCCN004", "SoPhong": "P102", "NgayBatDau": ngay_moc(-45), "NgayKetThuc": None, "DonGiaThangApDung": 500000},
]

ds_khach = [
    {"CMTKhach": "038200000001", "HoTen": "Nguyễn Thị Lan", "NgaySinh": "1978-05-12", "SDT": "0903111222"},
    {"CMTKhach": "038200000002", "HoTen": "Trần Văn Hùng", "NgaySinh": "1980-09-03", "SDT": "0903333444"},
    {"CMTKhach": "038200000003", "HoTen": "Lê Thu Hà", "NgaySinh": "2005-02-20", "SDT": ""},
]

ds_luot_tham = [
    {"MaLuotTham": 1, "CMTKhach": "038200000001", "MaSV": "B24DCCN001", "ThoiDiemDen": moc(0, "09:30")},
    {"MaLuotTham": 2, "CMTKhach": "038200000001", "MaSV": "B24DCCN001", "ThoiDiemDen": moc(-1, "08:15")},
    {"MaLuotTham": 3, "CMTKhach": "038200000002", "MaSV": "B24DCCN002", "ThoiDiemDen": moc(-2, "15:00")},
    {"MaLuotTham": 4, "CMTKhach": "038200000003", "MaSV": "B24DCCN001", "ThoiDiemDen": moc(-9, "18:20")},
    {"MaLuotTham": 5, "CMTKhach": "038200000002", "MaSV": "B24DCCN002", "ThoiDiemDen": moc(-40, "10:00")},
    {"MaLuotTham": 6, "CMTKhach": "038200000001", "MaSV": "B24DCCN003", "ThoiDiemDen": moc(0, "14:45")},
]

ds_dichvu = [
    {"MaDV": "DV01", "TenDV": "Giặt là", "LoaiDV": "Giặt là", "DonGia": 15000, "DonViTinh": "kg"},
    {"MaDV": "DV02", "TenDV": "Ăn uống", "LoaiDV": "Ăn uống", "DonGia": 30000, "DonViTinh": "suất"},
    {"MaDV": "DV03", "TenDV": "Trông xe vãng lai", "LoaiDV": "Trông xe", "DonGia": 3000, "DonViTinh": "lượt"},
    {"MaDV": "DV04", "TenDV": "Cho thuê xe", "LoaiDV": "Cho thuê xe", "DonGia": 50000, "DonViTinh": "lần"},
]


def tim_dv(madv):
    return next((d for d in ds_dichvu if d["MaDV"] == madv), None)


def tao_luot_dung(ma, masv, madv, thoi_diem, so_luong):
    """Một bản ghi SUDUNG_DV: đơn giá lấy từ DICHVU, thành tiền = số lượng x đơn giá."""
    dv = tim_dv(madv)
    return {"MaSuDung": ma, "MaSV": masv, "MaDV": madv, "ThoiDiemSuDung": thoi_diem,
            "SoLuong": so_luong, "DonGiaApDung": dv["DonGia"], "ThanhTien": so_luong * dv["DonGia"]}


ds_sudung = [
    tao_luot_dung(1, "B24DCCN001", "DV01", moc(-20, "18:00"), 3),
    tao_luot_dung(2, "B24DCCN001", "DV02", moc(-18, "12:00"), 4),
    tao_luot_dung(3, "B24DCCN001", "DV02", moc(-10, "12:10"), 2),
    tao_luot_dung(4, "B24DCCN002", "DV01", moc(-15, "19:00"), 2),
    tao_luot_dung(5, "B24DCCN002", "DV04", moc(-12, "09:00"), 1),
    tao_luot_dung(6, "B24DCCN002", "DV02", moc(-5, "18:30"), 3),
    tao_luot_dung(7, "B24DCCN003", "DV02", moc(-22, "12:00"), 5),
    tao_luot_dung(8, "B24DCCN003", "DV03", moc(-3, "07:30"), 2),
    tao_luot_dung(9, "B24DCCN003", "DV01", moc(-45, "20:00"), 4),
    tao_luot_dung(10, "B24DCCN001", "DV04", moc(-1, "15:00"), 2),
    tao_luot_dung(11, "B24DCCN004", "DV02", moc(0, "12:00"), 1),
    tao_luot_dung(12, "B24DCCN005", "DV01", moc(-2, "19:30"), 2),
]

ds_xe = [
    {"BienSo": "29A1-12345", "LoaiXe": "Xe máy"},
    {"BienSo": "29B2-67890", "LoaiXe": "Xe máy"},
    {"BienSo": "XD-B24DCCN001", "LoaiXe": "Xe đạp"},
    {"BienSo": "29MD-11111", "LoaiXe": "Xe điện"},
]

# NgayKetThuc = None nghĩa là vé còn hiệu lực; hủy vé thì điền ngày kết thúc.
# B24DCCN001 đủ 2 xe (thử chặn xe thứ 3); vé xe 29MD-11111 của B24DCCN003 đã hủy.
ds_dk_xe = [
    {"MaDKXe": 1, "MaSV": "B24DCCN001", "BienSo": "29A1-12345", "NgayBatDau": ngay_moc(-40),
     "NgayKetThuc": None, "DonGiaThangApDung": GIA_VE_THANG},
    {"MaDKXe": 2, "MaSV": "B24DCCN001", "BienSo": "XD-B24DCCN001", "NgayBatDau": ngay_moc(-40),
     "NgayKetThuc": None, "DonGiaThangApDung": GIA_VE_THANG},
    {"MaDKXe": 3, "MaSV": "B24DCCN002", "BienSo": "29B2-67890", "NgayBatDau": ngay_moc(-30),
     "NgayKetThuc": None, "DonGiaThangApDung": GIA_VE_THANG},
    {"MaDKXe": 4, "MaSV": "B24DCCN003", "BienSo": "29MD-11111", "NgayBatDau": ngay_moc(-45),
     "NgayKetThuc": ngay_moc(-30), "DonGiaThangApDung": GIA_VE_THANG},
]

# Xe 29A1-12345: hôm qua 4 lượt (lượt 3, 4 mất phí), hôm nay 2 lượt -> lượt tiếp theo mất 3.000đ
ds_luot_xe = [
    {"MaLuot": 1, "MaDKXe": 1, "ThoiDiem": f"{ngay_moc(-1)} 06:50:00", "LoaiHanhDong": "Gui", "PhiPhatSinh": 0},
    {"MaLuot": 2, "MaDKXe": 1, "ThoiDiem": f"{ngay_moc(-1)} 07:30:00", "LoaiHanhDong": "Lay", "PhiPhatSinh": 0},
    {"MaLuot": 3, "MaDKXe": 1, "ThoiDiem": f"{ngay_moc(-1)} 12:00:00", "LoaiHanhDong": "Gui", "PhiPhatSinh": 3000},
    {"MaLuot": 4, "MaDKXe": 1, "ThoiDiem": f"{ngay_moc(-1)} 12:30:00", "LoaiHanhDong": "Lay", "PhiPhatSinh": 3000},
    {"MaLuot": 5, "MaDKXe": 2, "ThoiDiem": f"{ngay_moc(-1)} 07:05:00", "LoaiHanhDong": "Gui", "PhiPhatSinh": 0},
    {"MaLuot": 6, "MaDKXe": 2, "ThoiDiem": f"{ngay_moc(-1)} 17:20:00", "LoaiHanhDong": "Lay", "PhiPhatSinh": 0},
    {"MaLuot": 7, "MaDKXe": 3, "ThoiDiem": f"{ngay_moc(-1)} 07:10:00", "LoaiHanhDong": "Gui", "PhiPhatSinh": 0},
    {"MaLuot": 8, "MaDKXe": 3, "ThoiDiem": f"{ngay_moc(-1)} 17:25:00", "LoaiHanhDong": "Lay", "PhiPhatSinh": 0},
    {"MaLuot": 9, "MaDKXe": 1, "ThoiDiem": f"{ngay_moc(0)} 06:50:00", "LoaiHanhDong": "Gui", "PhiPhatSinh": 0},
    {"MaLuot": 10, "MaDKXe": 1, "ThoiDiem": f"{ngay_moc(0)} 07:30:00", "LoaiHanhDong": "Lay", "PhiPhatSinh": 0},
]

ds_da_thu = set()   # {(MaSV, thang, nam)}: các hóa đơn đã thu tiền


# ===================== TRA CỨU =====================
def tim_sv(masv):
    return next((s for s in ds_sv if s["MaSV"] == masv), None)


def tim_phong(so_phong):
    return next((p for p in ds_phong if p["SoPhong"] == so_phong), None)


def tim_khach(cmt):
    return next((k for k in ds_khach if k["CMTKhach"] == cmt), None)


def tim_xe(bien_so):
    return next((x for x in ds_xe if x["BienSo"] == bien_so), None)


# ===================== PHÒNG Ở =====================
def so_nguoi_dang_o(so_phong):
    return sum(1 for dk in ds_dangky_o if dk["SoPhong"] == so_phong and dk["NgayKetThuc"] is None)


def dang_ky_dang_o(masv):
    return next((dk for dk in ds_dangky_o if dk["MaSV"] == masv and dk["NgayKetThuc"] is None), None)


def phong_cua():
    """Dict MaSV -> số phòng hiện tại."""
    return {dk["MaSV"]: dk["SoPhong"] for dk in ds_dangky_o if dk["NgayKetThuc"] is None}


# ===================== XE VÉ THÁNG =====================
def con_han(d, ngay=None):
    """Vé còn hiệu lực khi ngày nằm trong [NgayBatDau, NgayKetThuc]; NgayKetThuc NULL = chưa hủy."""
    ngay = ngay or ngay_moc(0)
    return d["NgayBatDau"] <= ngay <= (d["NgayKetThuc"] or "9999-12-31")


def dem_xe_hieu_luc(masv):
    return sum(1 for d in ds_dk_xe if d["MaSV"] == masv and con_han(d))


def dk_xe_hieu_luc_cua_bien(bien_so):
    return next((d for d in ds_dk_xe if d["BienSo"] == bien_so and con_han(d)), None)


def tao_ma_xe_dap(masv):
    """Xe đạp không có biển số: dùng mã sinh viên làm mã xe (XD-<MaSV>)."""
    ma = f"XD-{masv}"
    if dk_xe_hieu_luc_cua_bien(ma):
        ma += "-2"
    return ma


def chuan_hoa(chuoi):
    return chuoi.strip().upper().replace(" ", "")


def luot_trong_ngay(ma_dkxe, ngay):
    return sum(1 for l in ds_luot_xe if l["MaDKXe"] == ma_dkxe and l["ThoiDiem"][:10] == ngay)


def hanh_dong_tiep(ma_dkxe):
    """Lượt đầu của xe là Gửi, sau đó luân phiên Lấy / Gửi."""
    cac_luot = [l for l in ds_luot_xe if l["MaDKXe"] == ma_dkxe]
    if not cac_luot:
        return "Gui"
    cuoi = max(cac_luot, key=lambda l: l["ThoiDiem"])
    return "Lay" if cuoi["LoaiHanhDong"] == "Gui" else "Gui"


def phi_luot_tiep(ma_dkxe, ngay):
    return PHI_PHAT_SINH if luot_trong_ngay(ma_dkxe, ngay) >= MIEN_PHI_NGAY else 0


def nhan_dien_xe(ma_quet):
    """Camera quét biển số, hoặc thẻ sinh viên (xe đạp). Trả về (bản đăng ký, lỗi)."""
    ma = chuan_hoa(ma_quet)
    if not ma:
        return None, "Chưa nhận được mã quét."
    for d in ds_dk_xe:
        if chuan_hoa(d["BienSo"]) == ma and con_han(d):
            return d, None
    if any(chuan_hoa(d["BienSo"]) == ma for d in ds_dk_xe):
        return None, f"Vé tháng của xe {ma_quet.strip()} đã hết hạn, cần đăng ký lại."
    sv = next((s for s in ds_sv if chuan_hoa(s["MaSV"]) == ma), None)
    if sv:
        xe_dap = [d for d in ds_dk_xe
                  if d["MaSV"] == sv["MaSV"] and con_han(d)
                  and (tim_xe(d["BienSo"]) or {}).get("LoaiXe") == "Xe đạp"]
        if not xe_dap:
            return None, f"Sinh viên {sv['MaSV']} không có xe đạp vé tháng còn hạn."
        return min(xe_dap, key=lambda d: d["MaDKXe"]), None
    return None, f"Vé tháng của xe {ma_quet.strip()} đã bị hủy, cần đăng ký lại."


# ===================== THỜI GIAN VÀ HÓA ĐƠN =====================
def khoang_ky(ky, ngay_tc):
    """(từ ngày, đến ngày) của tuần (thứ Hai - Chủ nhật) hoặc tháng chứa ngay_tc."""
    if ky == "tuan":
        tu = ngay_tc - timedelta(days=ngay_tc.weekday())
        den = tu + timedelta(days=6)
    elif ky == "thang":
        tu = ngay_tc.replace(day=1)
        den = (tu + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    else:
        return None, None
    return tu.strftime("%Y-%m-%d"), den.strftime("%Y-%m-%d")


def dau_cuoi_thang(thang, nam):
    dau = datetime(nam, thang, 1)
    cuoi = (dau + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    return dau.strftime("%Y-%m-%d"), cuoi.strftime("%Y-%m-%d")


def tinh_hoa_don(masv, thang, nam):
    """Trả về (danh sách dòng chi tiết, dict tổng) của một sinh viên trong một tháng."""
    dau, cuoi = dau_cuoi_thang(thang, nam)
    ct = []

    # 1) Tiền phòng chẵn tháng: bản đăng ký nào giao với tháng thì tính đủ đơn giá tháng
    for dk in ds_dangky_o:
        het = dk["NgayKetThuc"] or "9999-12-31"
        if dk["MaSV"] == masv and dk["NgayBatDau"] <= cuoi and het >= dau:
            ct.append({"Loai": "Phong", "DienGiai": f"Tiền phòng {dk['SoPhong']} (tính chẵn tháng)",
                       "SoLuong": 1, "ThanhTien": dk["DonGiaThangApDung"]})

    # 2) Dịch vụ: gom theo từng dịch vụ
    nhom = {}
    for s in ds_sudung:
        if s["MaSV"] == masv and dau <= s["ThoiDiemSuDung"][:10] <= cuoi:
            g = nhom.setdefault(s["MaDV"], {"SoLuong": 0, "ThanhTien": 0})
            g["SoLuong"] += s["SoLuong"]
            g["ThanhTien"] += s["ThanhTien"]
    for madv, g in nhom.items():
        dv = tim_dv(madv)
        ct.append({"Loai": "DichVu",
                   "DienGiai": f"Dịch vụ {dv['TenDV'] if dv else madv} ({dv['DonViTinh'] if dv else ''})",
                   "SoLuong": g["SoLuong"], "ThanhTien": g["ThanhTien"]})

    # 3) Vé tháng xe: mỗi tháng vé còn hiệu lực thì tính 1 lần (giống tiền phòng chẵn tháng)
    for d in ds_dk_xe:
        het = d["NgayKetThuc"] or "9999-12-31"
        if d["MaSV"] == masv and d["NgayBatDau"] <= cuoi and het >= dau:
            ct.append({"Loai": "XeThang", "DienGiai": f"Vé tháng xe {d['BienSo']}",
                       "SoLuong": 1, "ThanhTien": d["DonGiaThangApDung"]})

    # 4) Phí gửi/lấy xe phát sinh (từ lượt thứ 3 trong ngày)
    ma_dk = {d["MaDKXe"] for d in ds_dk_xe if d["MaSV"] == masv}
    luot_phi = [l for l in ds_luot_xe
                if l["MaDKXe"] in ma_dk and l["PhiPhatSinh"] > 0 and dau <= l["ThoiDiem"][:10] <= cuoi]
    if luot_phi:
        ct.append({"Loai": "XePhatSinh", "DienGiai": "Phí gửi/lấy xe phát sinh",
                   "SoLuong": len(luot_phi), "ThanhTien": sum(l["PhiPhatSinh"] for l in luot_phi)})

    def cong(loai):
        return sum(c["ThanhTien"] for c in ct if c["Loai"] == loai)

    tong = {"TienPhong": cong("Phong"), "TienDV": cong("DichVu"),
            "TienVe": cong("XeThang"), "TienPhi": cong("XePhatSinh")}
    tong["Tong"] = sum(tong.values())
    return ct, tong