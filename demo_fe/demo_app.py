from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "ktx-dev"  # cần có để dùng flash()

# ===================== HẰNG SỐ =====================
GIA_VE_THANG = 100000
TOI_DA_XE = 2
MIEN_PHI_NGAY = 2
PHI_PHAT_SINH = 3000
DS_LOP = ["B24CQCN01-B", "B24CQCN02-B", "B24CQCN03-B"]
DS_LOAI_PHONG = ["Thường", "Chất lượng cao"]
DS_LOAI_XE = ["Xe đạp", "Xe máy", "Xe điện"]


def ngay_moc(offset=0):
    """Ngày (YYYY-MM-DD) lệch offset ngày so với hôm nay. Dữ liệu mẫu tính theo hôm nay để luôn demo được."""
    return (datetime.now() + timedelta(days=offset)).strftime("%Y-%m-%d")


def moc(offset=0, gio="08:00"):
    return f"{ngay_moc(offset)} {gio}"

HAN_VE_NGAY = 30


def ngay_het_han(ngay_bd):
    """Vé tháng có hạn 30 ngày: ngày bắt đầu + 29 ngày."""
    d = datetime.strptime(ngay_bd, "%Y-%m-%d") + timedelta(days=HAN_VE_NGAY - 1)
    return d.strftime("%Y-%m-%d")


# ===================== DỮ LIỆU GIẢ (Người 2 sẽ thay bằng MySQL) =====================
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
    """Tạo 1 bản ghi SUDUNG_DV: đơn giá lấy từ DICHVU, thành tiền = số lượng x đơn giá."""
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

# B24DCCN001 đã đủ 2 xe, để thử chặn xe thứ 3
# Vé tháng hạn 30 ngày: NgayKetThuc = NgayBatDau + 29.
# B24DCCN001 đủ 2 xe còn hạn (thử chặn xe thứ 3); xe 29MD-11111 của B24DCCN003 đã hết hạn (thử "Đăng ký lại").
ds_dk_xe = [
    {"MaDKXe": 1, "MaSV": "B24DCCN001", "BienSo": "29A1-12345", "NgayBatDau": ngay_moc(-10),
     "NgayKetThuc": ngay_het_han(ngay_moc(-10)), "DonGiaThangApDung": GIA_VE_THANG},
    {"MaDKXe": 2, "MaSV": "B24DCCN001", "BienSo": "XD-B24DCCN001", "NgayBatDau": ngay_moc(-10),
     "NgayKetThuc": ngay_het_han(ngay_moc(-10)), "DonGiaThangApDung": GIA_VE_THANG},
    {"MaDKXe": 3, "MaSV": "B24DCCN002", "BienSo": "29B2-67890", "NgayBatDau": ngay_moc(-5),
     "NgayKetThuc": ngay_het_han(ngay_moc(-5)), "DonGiaThangApDung": GIA_VE_THANG},
    {"MaDKXe": 4, "MaSV": "B24DCCN003", "BienSo": "29MD-11111", "NgayBatDau": ngay_moc(-45),
     "NgayKetThuc": ngay_het_han(ngay_moc(-45)), "DonGiaThangApDung": GIA_VE_THANG},
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


# ===================== HÀM HỖ TRỢ =====================
def tim_sv(masv):
    return next((s for s in ds_sv if s["MaSV"] == masv), None)


def tim_phong(so_phong):
    return next((p for p in ds_phong if p["SoPhong"] == so_phong), None)


def tim_khach(cmt):
    return next((k for k in ds_khach if k["CMTKhach"] == cmt), None)


def tim_xe(bien_so):
    return next((x for x in ds_xe if x["BienSo"] == bien_so), None)


def so_nguoi_dang_o(so_phong):
    return sum(1 for dk in ds_dangky_o if dk["SoPhong"] == so_phong and dk["NgayKetThuc"] is None)


def dang_ky_dang_o(masv):
    return next((dk for dk in ds_dangky_o if dk["MaSV"] == masv and dk["NgayKetThuc"] is None), None)


def phong_cua():
    """Dict MaSV -> số phòng hiện tại."""
    return {dk["MaSV"]: dk["SoPhong"] for dk in ds_dangky_o if dk["NgayKetThuc"] is None}


def con_han(d, ngay=None):
    """Vé tháng còn hiệu lực khi ngày nằm trong [NgayBatDau, NgayKetThuc]."""
    ngay = ngay or ngay_moc(0)
    return d["NgayBatDau"] <= ngay <= d["NgayKetThuc"]

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
    return None, (f"Không nhận diện được '{ma_quet.strip()}': không phải xe vé tháng. "
                  "Xe vãng lai thu tiền trực tiếp, không lưu hệ thống.")


# ===================== FILTER HIỂN THỊ =====================
@app.template_filter("ngay")
def f_ngay(chuoi):
    try:
        return datetime.strptime(chuoi, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return chuoi or ""


@app.template_filter("gio")
def f_gio(chuoi):
    try:
        return datetime.strptime(chuoi, "%Y-%m-%d %H:%M").strftime("%H:%M %d/%m/%Y")
    except (ValueError, TypeError):
        return chuoi or ""


@app.template_filter("gio_giay")
def f_gio_giay(chuoi):
    try:
        return datetime.strptime(chuoi, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S %d/%m/%Y")
    except (ValueError, TypeError):
        return chuoi or ""


@app.template_filter("tien")
def f_tien(so):
    try:
        return f"{int(so):,}".replace(",", ".") + "đ"
    except (ValueError, TypeError):
        return so


@app.context_processor
def chung():
    return {"hom_nay_hien_thi": datetime.now().strftime("%d/%m/%Y")}


# ===================== TỔNG QUAN =====================
@app.route("/")
def trang_chu():
    hom_nay = ngay_moc(0)
    tong_cho = sum(p["SoNguoiToiDa"] for p in ds_phong)
    dang_o = sum(so_nguoi_dang_o(p["SoPhong"]) for p in ds_phong)
    khach_hn = sum(1 for l in ds_luot_tham if l["ThoiDiemDen"][:10] == hom_nay)
    luot_hn = [l for l in ds_luot_xe if l["ThoiDiem"][:10] == hom_nay]
    dau_thang = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    dv_thang = sum(s["ThanhTien"] for s in ds_sudung if s["ThoiDiemSuDung"][:10] >= dau_thang)

    ds_phong_ht = [{**p, "DangO": so_nguoi_dang_o(p["SoPhong"])} for p in ds_phong]

    hoat_dong = []
    for l in sorted(ds_luot_xe, key=lambda x: x["ThoiDiem"], reverse=True)[:4]:
        d = next((x for x in ds_dk_xe if x["MaDKXe"] == l["MaDKXe"]), None)
        hoat_dong.append({"Gio": l["ThoiDiem"], "Icon": "bicycle", "Mau": "xanh",
                          "Noi": f"{'Gửi' if l['LoaiHanhDong'] == 'Gui' else 'Lấy'} xe {d['BienSo'] if d else '?'}"})
    for l in sorted(ds_luot_tham, key=lambda x: x["ThoiDiemDen"], reverse=True)[:3]:
        k, sv = tim_khach(l["CMTKhach"]), tim_sv(l["MaSV"])
        hoat_dong.append({"Gio": l["ThoiDiemDen"] + ":00", "Icon": "person-badge", "Mau": "tim",
                          "Noi": f"{k['HoTen'] if k else ''} thăm {sv['HoTen'] if sv else ''}"})
    for s in sorted(ds_sudung, key=lambda x: x["ThoiDiemSuDung"], reverse=True)[:3]:
        sv, dv = tim_sv(s["MaSV"]), tim_dv(s["MaDV"])
        hoat_dong.append({"Gio": s["ThoiDiemSuDung"] + ":00", "Icon": "basket", "Mau": "cam",
                          "Noi": f"{sv['HoTen'] if sv else ''} dùng {dv['TenDV'] if dv else ''} x{s['SoLuong']}"})
    hoat_dong.sort(key=lambda x: x["Gio"], reverse=True)

    return render_template("dashboard.html", so_sv=len(ds_sv), dang_o=dang_o, tong_cho=tong_cho,
                           khach_hn=khach_hn, luot_hn=len(luot_hn),
                           phi_hn=sum(l["PhiPhatSinh"] for l in luot_hn), dv_thang=dv_thang,
                           ds_phong=ds_phong_ht, hoat_dong=hoat_dong[:8])


# ===================== SINH VIÊN =====================
@app.route("/sinhvien", methods=["GET", "POST"])
def sinhvien():
    form = {}
    if request.method == "POST":
        form = request.form
        masv, socmt = form["MaSV"].strip(), form["SoCMT"].strip()
        if any(sv["MaSV"] == masv for sv in ds_sv):
            flash(f"Mã sinh viên {masv} đã tồn tại.", "danger")
        elif any(sv["SoCMT"] == socmt for sv in ds_sv):
            flash(f"Số CMT/CCCD {socmt} đã được dùng bởi sinh viên khác.", "danger")
        else:
            ds_sv.append({"MaSV": masv, "HoTen": form["HoTen"].strip(), "SoCMT": socmt,
                          "NgaySinh": form["NgaySinh"], "GioiTinh": form["GioiTinh"],
                          "SDT": form["SDT"].strip(), "Lop": form["Lop"],
                          "QueQuan": form["QueQuan"].strip()})
            flash("Thêm sinh viên thành công.", "success")
            return redirect(url_for("sinhvien"))
    pc = phong_cua()
    ds = [{**sv, "Phong": pc.get(sv["MaSV"], "")} for sv in ds_sv]
    return render_template("sinhvien.html", ds=ds, ds_lop=DS_LOP, form=form)


@app.route("/sinhvien/xoa/<masv>", methods=["POST"])
def xoa_sinhvien(masv):
    if dang_ky_dang_o(masv):
        flash(f"Không thể xóa sinh viên {masv} vì đang ở phòng. Hãy trả phòng trước.", "danger")
    else:
        ds_sv[:] = [sv for sv in ds_sv if sv["MaSV"] != masv]
        flash(f"Đã xóa sinh viên {masv}.", "warning")
    return redirect(url_for("sinhvien"))


# ===================== PHÒNG Ở =====================
@app.route("/phong", methods=["GET", "POST"])
def phong():
    form = {}
    if request.method == "POST":
        form = request.form
        so_phong = form["SoPhong"].strip().upper()
        try:
            don_gia, toi_da = int(form["DonGia"]), int(form["SoNguoiToiDa"])
        except ValueError:
            don_gia = toi_da = 0
            flash("Đơn giá và số người tối đa phải là số nguyên.", "danger")
        if don_gia and toi_da:
            if tim_phong(so_phong):
                flash(f"Phòng {so_phong} đã tồn tại.", "danger")
            elif don_gia <= 0 or toi_da <= 0:
                flash("Đơn giá và số người tối đa phải lớn hơn 0.", "danger")
            else:
                ds_phong.append({"SoPhong": so_phong, "LoaiPhong": form["LoaiPhong"],
                                 "DonGia": don_gia, "SoNguoiToiDa": toi_da})
                flash(f"Đã thêm phòng {so_phong}.", "success")
                return redirect(url_for("phong"))
    ds = [{**p, "DangO": so_nguoi_dang_o(p["SoPhong"])} for p in ds_phong]
    tong_cho = sum(p["SoNguoiToiDa"] for p in ds_phong)
    tong_dang_o = sum(p["DangO"] for p in ds)
    return render_template("phong.html", ds=ds, ds_loai=DS_LOAI_PHONG, form=form,
                           tong_cho=tong_cho, tong_dang_o=tong_dang_o)


@app.route("/phong/xoa/<so_phong>", methods=["POST"])
def xoa_phong(so_phong):
    if so_nguoi_dang_o(so_phong) > 0:
        flash(f"Không thể xóa phòng {so_phong} vì đang có người ở.", "danger")
    else:
        ds_phong[:] = [p for p in ds_phong if p["SoPhong"] != so_phong]
        flash(f"Đã xóa phòng {so_phong}.", "warning")
    return redirect(url_for("phong"))


# ===================== ĐĂNG KÝ Ở / TRẢ PHÒNG =====================
@app.route("/dangky-o", methods=["GET", "POST"])
def dangky_o():
    form = {}
    if request.method == "POST":
        form = request.form
        masv, so_phong, ngay = form["MaSV"], form["SoPhong"], form["NgayBatDau"]
        sv, p = tim_sv(masv), tim_phong(so_phong)
        loi = None
        try:
            datetime.strptime(ngay, "%Y-%m-%d")
        except ValueError:
            loi = "Ngày bắt đầu không hợp lệ."
        if loi is None:
            if sv is None:
                loi = "Không tìm thấy sinh viên đã chọn."
            elif p is None:
                loi = "Không tìm thấy phòng đã chọn."
            elif dang_ky_dang_o(masv):
                loi = (f"Sinh viên {masv} đang ở phòng {dang_ky_dang_o(masv)['SoPhong']}. "
                       "Hãy trả phòng cũ trước khi đăng ký phòng mới.")
            elif so_nguoi_dang_o(so_phong) >= p["SoNguoiToiDa"]:
                loi = (f"Phòng {so_phong} đã đủ {p['SoNguoiToiDa']}/{p['SoNguoiToiDa']} người, "
                       "không thể đăng ký thêm.")
        if loi:
            flash(loi, "danger")
        else:
            ma_moi = max((d["MaDKO"] for d in ds_dangky_o), default=0) + 1
            ds_dangky_o.append({"MaDKO": ma_moi, "MaSV": masv, "SoPhong": so_phong,
                                "NgayBatDau": ngay, "NgayKetThuc": None,
                                "DonGiaThangApDung": p["DonGia"]})  # lấy từ phòng, không nhập tay
            flash(f"Đã xếp {sv['HoTen']} vào phòng {so_phong}.", "success")
            return redirect(url_for("dangky_o"))

    ds_sv_trong = [sv for sv in ds_sv if dang_ky_dang_o(sv["MaSV"]) is None]
    ds_phong_ht = []
    for p in ds_phong:
        dang_o = so_nguoi_dang_o(p["SoPhong"])
        ds_phong_ht.append({**p, "DangO": dang_o, "Con": p["SoNguoiToiDa"] - dang_o})
    ds_dk = []
    for dk in ds_dangky_o:
        sv = tim_sv(dk["MaSV"])
        ds_dk.append({**dk, "HoTen": sv["HoTen"] if sv else "(đã xóa)"})
    ds_dk.sort(key=lambda d: (d["NgayKetThuc"] is not None, -d["MaDKO"]))
    return render_template("dangky_o.html", ds_dk=ds_dk, ds_sv_trong=ds_sv_trong,
                           ds_phong=ds_phong_ht, form=form, hom_nay=ngay_moc(0))


@app.route("/dangky-o/tra/<int:ma_dko>", methods=["POST"])
def tra_phong(ma_dko):
    dk = next((d for d in ds_dangky_o if d["MaDKO"] == ma_dko), None)
    if dk is None:
        flash("Không tìm thấy bản đăng ký.", "danger")
    elif dk["NgayKetThuc"] is not None:
        flash("Bản đăng ký này đã được trả phòng rồi.", "danger")
    else:
        dk["NgayKetThuc"] = max(ngay_moc(0), dk["NgayBatDau"])
        flash(f"Đã trả phòng {dk['SoPhong']} cho sinh viên {dk['MaSV']}.", "warning")
    return redirect(url_for("dangky_o"))


# ===================== KHÁCH THĂM =====================
@app.route("/khach", methods=["GET", "POST"])
def khach():
    form = {}
    if request.method == "POST":
        form = request.form
        cmt, masv = form["CMTKhach"].strip(), form["MaSV"]
        thoi_diem = form["ThoiDiemDen"].replace("T", " ")
        loi = None
        try:
            datetime.strptime(thoi_diem, "%Y-%m-%d %H:%M")
        except ValueError:
            loi = "Thời điểm đến không hợp lệ."
        if loi is None and tim_sv(masv) is None:
            loi = "Không tìm thấy sinh viên được thăm."
        if loi is None and tim_khach(cmt) is None:
            if not form["HoTen"].strip() or not form["NgaySinh"]:
                loi = "Khách mới cần nhập đủ họ tên và ngày sinh."
        if loi:
            flash(loi, "danger")
        else:
            if tim_khach(cmt) is None:
                ds_khach.append({"CMTKhach": cmt, "HoTen": form["HoTen"].strip(),
                                 "NgaySinh": form["NgaySinh"], "SDT": form["SDT"].strip()})
            ma_moi = max((l["MaLuotTham"] for l in ds_luot_tham), default=0) + 1
            ds_luot_tham.append({"MaLuotTham": ma_moi, "CMTKhach": cmt, "MaSV": masv, "ThoiDiemDen": thoi_diem})
            flash("Đã ghi nhận lượt thăm.", "success")
            return redirect(url_for("khach"))

    ky = request.args.get("ky", "tuan")
    if ky not in ("tuan", "thang", "tatca"):
        ky = "tuan"
    bay_gio = datetime.now()
    try:
        ngay_tc = datetime.strptime(request.args.get("ngay", ""), "%Y-%m-%d")
    except ValueError:
        ngay_tc = bay_gio
    tu, den = khoang_ky(ky, ngay_tc)
    ds_loc = [l for l in ds_luot_tham if tu is None or tu <= l["ThoiDiemDen"][:10] <= den]

    nhom = {}
    for l in ds_loc:
        nhom.setdefault((l["MaSV"], l["CMTKhach"]), []).append(l["ThoiDiemDen"])
    ds_thongke = []
    for (masv, cmt), cac_lan in nhom.items():
        sv, k = tim_sv(masv), tim_khach(cmt)
        ds_thongke.append({"MaSV": masv, "HoTenSV": sv["HoTen"] if sv else "(đã xóa)",
                           "Lop": sv["Lop"] if sv else "", "CMTKhach": cmt,
                           "HoTenKhach": k["HoTen"] if k else "",
                           "SoLan": len(cac_lan), "LanCuoi": max(cac_lan)})
    ds_thongke.sort(key=lambda d: (d["MaSV"], -d["SoLan"]))

    ds_chitiet = []
    for l in sorted(ds_loc, key=lambda x: x["ThoiDiemDen"], reverse=True):
        sv, k = tim_sv(l["MaSV"]), tim_khach(l["CMTKhach"])
        ds_chitiet.append({**l, "HoTenSV": sv["HoTen"] if sv else "(đã xóa)",
                           "HoTenKhach": k["HoTen"] if k else ""})

    return render_template("khach.html", form=form, ds_sv=ds_sv, ds_khach=ds_khach,
                           ds_thongke=ds_thongke, ds_chitiet=ds_chitiet, ky=ky,
                           ngay=ngay_tc.strftime("%Y-%m-%d"), tu=tu, den=den,
                           so_khach=len({l["CMTKhach"] for l in ds_loc}),
                           so_sv=len({l["MaSV"] for l in ds_loc}),
                           bay_gio=bay_gio.strftime("%Y-%m-%dT%H:%M"))


# ===================== DỊCH VỤ =====================
@app.route("/dichvu", methods=["GET", "POST"])
def dichvu():
    form = {}
    if request.method == "POST":
        form = request.form
        masv, madv = form["MaSV"], form["MaDV"]
        thoi_diem = form["ThoiDiemSuDung"].replace("T", " ")
        loi = None
        try:
            so_luong = int(form["SoLuong"])
            if so_luong <= 0:
                loi = "Số lượng phải lớn hơn 0."
        except ValueError:
            loi = "Số lượng phải là số nguyên."
        if loi is None:
            try:
                datetime.strptime(thoi_diem, "%Y-%m-%d %H:%M")
            except ValueError:
                loi = "Thời điểm sử dụng không hợp lệ."
        if loi is None and tim_sv(masv) is None:
            loi = "Không tìm thấy sinh viên đã chọn."
        if loi is None and tim_dv(madv) is None:
            loi = "Không tìm thấy dịch vụ đã chọn."
        if loi:
            flash(loi, "danger")
        else:
            ma_moi = max((s["MaSuDung"] for s in ds_sudung), default=0) + 1
            ds_sudung.append(tao_luot_dung(ma_moi, masv, madv, thoi_diem, so_luong))
            flash(f"Đã ghi nhận cho {tim_sv(masv)['HoTen']}: {tim_dv(madv)['TenDV']} x {so_luong}.", "success")
            return redirect(url_for("dichvu"))

    hom_nay = datetime.now()
    pc = phong_cua()
    ds_sv_ht = [{**sv, "Phong": pc.get(sv["MaSV"], "")} for sv in ds_sv]

    # Mặc định thống kê 30 ngày gần nhất
    tu = request.args.get("tu", ngay_moc(-30))
    den = request.args.get("den", ngay_moc(0))
    loc_phong, loc_lop = request.args.get("phong", ""), request.args.get("lop", "")
    try:
        datetime.strptime(tu, "%Y-%m-%d")
        datetime.strptime(den, "%Y-%m-%d")
    except ValueError:
        tu, den = ngay_moc(-30), ngay_moc(0)
    if tu > den:
        flash("Ngày bắt đầu phải không muộn hơn ngày kết thúc.", "danger")
        tu, den = den, tu

    hop_le = {sv["MaSV"]: sv for sv in ds_sv_ht
              if (not loc_phong or sv["Phong"] == loc_phong) and (not loc_lop or sv["Lop"] == loc_lop)}
    nhom = {}
    for s in ds_sudung:
        if s["MaSV"] in hop_le and tu <= s["ThoiDiemSuDung"][:10] <= den:
            g = nhom.setdefault((s["MaSV"], s["MaDV"]), {"SoLuong": 0, "TongTien": 0})
            g["SoLuong"] += s["SoLuong"]
            g["TongTien"] += s["ThanhTien"]
    ds_thongke = []
    for (masv, madv), g in nhom.items():
        sv, dv = hop_le[masv], tim_dv(madv)
        ds_thongke.append({"MaSV": masv, "HoTenSV": sv["HoTen"], "Lop": sv["Lop"],
                           "Phong": sv["Phong"] or "—", "TenDV": dv["TenDV"] if dv else madv,
                           "DonViTinh": dv["DonViTinh"] if dv else "", **g})
    ds_thongke.sort(key=lambda d: (d["Phong"], d["MaSV"], d["TenDV"]))

    ds_gan_day = []
    for s in sorted(ds_sudung, key=lambda x: x["ThoiDiemSuDung"], reverse=True)[:8]:
        sv, dv = tim_sv(s["MaSV"]), tim_dv(s["MaDV"])
        ds_gan_day.append({**s, "HoTenSV": sv["HoTen"] if sv else "(đã xóa)",
                           "TenDV": dv["TenDV"] if dv else s["MaDV"]})

    return render_template("dichvu.html", form=form, ds_sv=ds_sv_ht, ds_dichvu=ds_dichvu,
                           ds_phong=[p["SoPhong"] for p in ds_phong], ds_lop=DS_LOP,
                           ds_thongke=ds_thongke, ds_gan_day=ds_gan_day, tu=tu, den=den,
                           loc_phong=loc_phong, loc_lop=loc_lop,
                           tong_tien=sum(d["TongTien"] for d in ds_thongke),
                           bay_gio=hom_nay.strftime("%Y-%m-%dT%H:%M"))


@app.route("/dichvu/xoa/<int:ma>", methods=["POST"])
def xoa_luot_dung(ma):
    ds_sudung[:] = [s for s in ds_sudung if s["MaSuDung"] != ma]
    flash(f"Đã xóa lượt sử dụng #{ma}.", "warning")
    return redirect(url_for("dichvu"))


# ===================== GỬI XE THÁNG =====================
@app.route("/xe-thang", methods=["GET", "POST"])
def xe_thang():
    form = {}
    if request.method == "POST":
        form = request.form
        masv, loai, ngay = form["MaSV"], form["LoaiXe"], form["NgayBatDau"]
        bien_so = form.get("BienSo", "").strip().upper()
        if loai == "Xe đạp":
            bien_so = tao_ma_xe_dap(masv)   # xe đạp quản lý theo mã sinh viên
        loi = None
        try:
            datetime.strptime(ngay, "%Y-%m-%d")
            if ngay > ngay_moc(0):
                loi = "Ngày bắt đầu không được ở tương lai."
        except ValueError:
            loi = "Ngày bắt đầu không hợp lệ."
        if loi is None:
            if tim_sv(masv) is None:
                loi = "Không tìm thấy sinh viên đã chọn."
            elif not bien_so:
                loi = "Vui lòng nhập biển số xe."
            elif loai not in DS_LOAI_XE:
                loi = "Loại xe không hợp lệ."
            elif dem_xe_hieu_luc(masv) >= TOI_DA_XE:
                loi = f"Sinh viên {masv} đã đăng ký đủ {TOI_DA_XE}/{TOI_DA_XE} xe vé tháng, không thể đăng ký thêm."
            elif dk_xe_hieu_luc_cua_bien(bien_so):
                loi = f"Biển số {bien_so} đang được sinh viên {dk_xe_hieu_luc_cua_bien(bien_so)['MaSV']} đăng ký vé tháng."
        if loi:
            flash(loi, "danger")
        else:
            if tim_xe(bien_so) is None:
                ds_xe.append({"BienSo": bien_so, "LoaiXe": loai})
            ma_moi = max((d["MaDKXe"] for d in ds_dk_xe), default=0) + 1
            ds_dk_xe.append({"MaDKXe": ma_moi, "MaSV": masv, "BienSo": bien_so, "NgayBatDau": ngay,
                             "NgayKetThuc": ngay_het_han(ngay), "DonGiaThangApDung": GIA_VE_THANG})
            flash(f"Đã đăng ký vé tháng cho xe {bien_so} (sinh viên {masv}), hạn đến {ngay_het_han(ngay)[8:10]}/{ngay_het_han(ngay)[5:7]}.", "success")
            return redirect(url_for("xe_thang"))

    pc = phong_cua()
    hom_nay_dt = datetime.strptime(ngay_moc(0), "%Y-%m-%d")
    ds_sv_ht = [{**sv, "Phong": pc.get(sv["MaSV"], ""), "SoXe": dem_xe_hieu_luc(sv["MaSV"])} for sv in ds_sv]
    bien_con_han = {d["BienSo"] for d in ds_dk_xe if con_han(d)}
    ds_hien_thi = []
    for d in ds_dk_xe:
        sv, xe = tim_sv(d["MaSV"]), tim_xe(d["BienSo"])
        ds_hien_thi.append({
            **d, "HoTen": sv["HoTen"] if sv else "(đã xóa)",
            "Phong": pc.get(d["MaSV"], "") or "—", "LoaiXe": xe["LoaiXe"] if xe else "",
            "ConHan": con_han(d),
            "DaCoVeMoi": d["BienSo"] in bien_con_han,
            "ConNgay": (datetime.strptime(d["NgayKetThuc"], "%Y-%m-%d") - hom_nay_dt).days})
    ds_hien_thi.sort(key=lambda d: (not d["ConHan"], -d["MaDKXe"]))
    return render_template("xe_thang.html", form=form, ds_sv=ds_sv_ht, ds_dk=ds_hien_thi,
                           ds_phong=[p["SoPhong"] for p in ds_phong], ds_lop=DS_LOP,
                           ds_loai=DS_LOAI_XE, toi_da=TOI_DA_XE, gia=GIA_VE_THANG, hom_nay=ngay_moc(0))


# ===================== QUẸT XE =====================
@app.route("/quet-xe", methods=["GET", "POST"])
def quet_xe():
    if request.method == "POST":
        d, loi = nhan_dien_xe(request.form.get("MaQuet", ""))
        if loi:
            flash(loi, "danger")
        else:
            bay_gio = datetime.now()
            ngay = bay_gio.strftime("%Y-%m-%d")
            hanh_dong = hanh_dong_tiep(d["MaDKXe"])
            phi = phi_luot_tiep(d["MaDKXe"], ngay)        # backend tự tính, không nhận từ form
            thu_tu = luot_trong_ngay(d["MaDKXe"], ngay) + 1
            ma_moi = max((l["MaLuot"] for l in ds_luot_xe), default=0) + 1
            ds_luot_xe.append({"MaLuot": ma_moi, "MaDKXe": d["MaDKXe"],
                               "ThoiDiem": bay_gio.strftime("%Y-%m-%d %H:%M:%S"),
                               "LoaiHanhDong": hanh_dong, "PhiPhatSinh": phi})
            sv = tim_sv(d["MaSV"])
            ten = sv["HoTen"] if sv else d["MaSV"]
            ten_hd = "GỬI" if hanh_dong == "Gui" else "LẤY"
            if phi:
                flash(f"{ten_hd} xe {d['BienSo']} ({ten}) - lượt thứ {thu_tu} trong ngày, "
                      f"thu phí phát sinh {phi:,}đ.".replace(",", "."), "warning")
            else:
                flash(f"{ten_hd} xe {d['BienSo']} ({ten}) - lượt thứ {thu_tu} trong ngày, miễn phí.", "success")
        return redirect(url_for("quet_xe"))

    hom_nay = ngay_moc(0)
    pc = phong_cua()
    ds_gia_lap = []
    for d in ds_dk_xe:
        if not con_han(d):
            continue
        xe, sv = tim_xe(d["BienSo"]), tim_sv(d["MaSV"])
        la_xe_dap = bool(xe) and xe["LoaiXe"] == "Xe đạp"
        ds_gia_lap.append({
            "Nhan": d["BienSo"], "HoTen": sv["HoTen"] if sv else d["MaSV"],
            "LoaiXe": xe["LoaiXe"] if xe else "", "MaQuet": d["MaSV"] if la_xe_dap else d["BienSo"],
            "Nguon": "Quẹt thẻ SV" if la_xe_dap else "Camera biển số",
            "SoLuot": luot_trong_ngay(d["MaDKXe"], hom_nay),
            "TiepTheo": "Gửi" if hanh_dong_tiep(d["MaDKXe"]) == "Gui" else "Lấy",
            "PhiTiep": phi_luot_tiep(d["MaDKXe"], hom_nay)})
    ds_gan_day = []
    for l in sorted(ds_luot_xe, key=lambda x: x["ThoiDiem"], reverse=True)[:10]:
        d = next((x for x in ds_dk_xe if x["MaDKXe"] == l["MaDKXe"]), None)
        sv = tim_sv(d["MaSV"]) if d else None
        ds_gan_day.append({**l, "BienSo": d["BienSo"] if d else "?", "HoTen": sv["HoTen"] if sv else "",
                           "Phong": pc.get(d["MaSV"], "—") if d else "—"})
    luot_hn = [l for l in ds_luot_xe if l["ThoiDiem"][:10] == hom_nay]
    return render_template("quet_xe.html", ds_gia_lap=ds_gia_lap, ds_gan_day=ds_gan_day,
                           so_luot=len(luot_hn), tong_phi=sum(l["PhiPhatSinh"] for l in luot_hn),
                           mien_phi=MIEN_PHI_NGAY, phi=PHI_PHAT_SINH)


@app.route("/quet-xe/xoa/<int:ma>", methods=["POST"])
def xoa_luot_xe(ma):
    ds_luot_xe[:] = [l for l in ds_luot_xe if l["MaLuot"] != ma]
    flash(f"Đã xóa lượt quét #{ma}.", "warning")
    return redirect(url_for("quet_xe"))

# ===================== HÓA ĐƠN =====================
ds_da_thu = set()   # {(MaSV, thang, nam)} các hóa đơn đã thu tiền


def dau_cuoi_thang(thang, nam):
    dau = datetime(nam, thang, 1)
    cuoi = (dau + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    return dau.strftime("%Y-%m-%d"), cuoi.strftime("%Y-%m-%d")


def doc_ky():
    """Đọc tháng/năm từ ?thang=&nam=, mặc định tháng hiện tại."""
    bay_gio = datetime.now()
    try:
        thang = int(request.args.get("thang", bay_gio.month))
        nam = int(request.args.get("nam", bay_gio.year))
        if not (1 <= thang <= 12 and 2000 <= nam <= 2100):
            raise ValueError
    except ValueError:
        thang, nam = bay_gio.month, bay_gio.year
    return thang, nam


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

    # 3) Vé tháng xe: tính vào tháng của ngày bắt đầu
    for d in ds_dk_xe:
        if d["MaSV"] == masv and dau <= d["NgayBatDau"] <= cuoi:
            ct.append({"Loai": "XeThang", "DienGiai": f"Vé tháng xe {d['BienSo']} (từ {d['NgayBatDau'][8:10]}/{d['NgayBatDau'][5:7]})",
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


@app.route("/hoadon")
def hoadon():
    thang, nam = doc_ky()
    loc_phong, loc_lop = request.args.get("phong", ""), request.args.get("lop", "")
    pc = phong_cua()
    ds = []
    for sv in ds_sv:
        if loc_phong and pc.get(sv["MaSV"], "") != loc_phong:
            continue
        if loc_lop and sv["Lop"] != loc_lop:
            continue
        _, tong = tinh_hoa_don(sv["MaSV"], thang, nam)
        if tong["Tong"] == 0:
            continue
        ds.append({**sv, "Phong": pc.get(sv["MaSV"], "") or "—", **tong,
                   "DaThu": (sv["MaSV"], thang, nam) in ds_da_thu})
    tong_cong = sum(d["Tong"] for d in ds)
    da_thu = sum(d["Tong"] for d in ds if d["DaThu"])
    return render_template("hoadon.html", ds=ds, thang=thang, nam=nam,
                           ds_nam=[nam - 1, nam, nam + 1] if nam == datetime.now().year else [nam],
                           ds_phong=[p["SoPhong"] for p in ds_phong], ds_lop=DS_LOP,
                           loc_phong=loc_phong, loc_lop=loc_lop,
                           tong_cong=tong_cong, da_thu=da_thu, chua_thu=tong_cong - da_thu)


@app.route("/hoadon/<masv>")
def hoadon_chitiet(masv):
    sv = tim_sv(masv)
    if sv is None:
        flash("Không tìm thấy sinh viên.", "danger")
        return redirect(url_for("hoadon"))
    thang, nam = doc_ky()
    ct, tong = tinh_hoa_don(masv, thang, nam)
    return render_template("hoadon_chitiet.html", sv=sv, ct=ct, tong=tong, thang=thang, nam=nam,
                           phong=phong_cua().get(masv, "") or "—",
                           da_thu=(masv, thang, nam) in ds_da_thu)


@app.route("/hoadon/<masv>/thu", methods=["POST"])
def hoadon_thu(masv):
    try:
        thang, nam = int(request.form["thang"]), int(request.form["nam"])
    except (KeyError, ValueError):
        flash("Thiếu thông tin tháng/năm.", "danger")
        return redirect(url_for("hoadon"))
    khoa = (masv, thang, nam)
    if khoa in ds_da_thu:
        ds_da_thu.discard(khoa)
        flash("Đã bỏ đánh dấu đã thu.", "warning")
    else:
        ds_da_thu.add(khoa)
        flash(f"Đã ghi nhận thu tiền tháng {thang}/{nam} của {masv}.", "success")
    return redirect(url_for("hoadon_chitiet", masv=masv, thang=thang, nam=nam))


# ===================== DOANH THU DỊCH VỤ =====================
@app.route("/doanhthu")
def doanhthu():
    bay_gio = datetime.now()
    try:
        nam = int(request.args.get("nam", bay_gio.year))
        if not 2000 <= nam <= 2100:
            raise ValueError
    except ValueError:
        nam = bay_gio.year
    hang = []
    tong_thang = [0] * 12
    for dv in ds_dichvu:
        theo_thang = [0] * 12
        for s in ds_sudung:
            if s["MaDV"] == dv["MaDV"] and s["ThoiDiemSuDung"][:4] == str(nam):
                theo_thang[int(s["ThoiDiemSuDung"][5:7]) - 1] += s["ThanhTien"]
        for i, v in enumerate(theo_thang):
            tong_thang[i] += v
        hang.append({"MaDV": dv["MaDV"], "TenDV": dv["TenDV"], "DonViTinh": dv["DonViTinh"],
                     "Thang": theo_thang, "Tong": sum(theo_thang)})
    return render_template("doanhthu.html", hang=hang, tong_thang=tong_thang, tong_nam=sum(tong_thang),
                           nam=nam, ds_nam=[bay_gio.year - 1, bay_gio.year, bay_gio.year + 1],
                           thang_ht=bay_gio.month if nam == bay_gio.year else 0)


if __name__ == "__main__":
    app.run(debug=True)