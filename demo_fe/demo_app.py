from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "ktx-dev"  # cần có để dùng flash()

DS_LOP = ["B24CQCN01-B", "B24CQCN02-B", "B24CQCN03-B"]

# Dữ liệu giả, sau này Người 2 thay bằng truy vấn MySQL
ds_sv = [
    {"MaSV": "B24DCCN001", "HoTen": "Nguyễn Văn An", "SoCMT": "001205000001",
     "NgaySinh": "2006-03-21", "GioiTinh": "Nam", "SDT": "0901234567",
     "Lop": "B24CQCN01-B", "QueQuan": "Hà Nam"},
    {"MaSV": "B24DCCN002", "HoTen": "Trần Thị Bình", "SoCMT": "001205000002",
     "NgaySinh": "2006-07-09", "GioiTinh": "Nữ", "SDT": "0912345678",
     "Lop": "B24CQCN02-B", "QueQuan": "Nam Định"},
    {"MaSV": "B24DCCN003", "HoTen": "Lê Văn Cường", "SoCMT": "001205000003",
     "NgaySinh": "2005-11-30", "GioiTinh": "Nam", "SDT": "0987654321",
     "Lop": "B24CQCN03-B", "QueQuan": "Thanh Hóa"},
]

DS_LOAI_PHONG = ["Thường", "Chất lượng cao"]

# Dữ liệu giả cho bảng PHONG
ds_phong = [
    {"SoPhong": "P101", "LoaiPhong": "Thường", "DonGia": 500000, "SoNguoiToiDa": 4},
    {"SoPhong": "P102", "LoaiPhong": "Thường", "DonGia": 500000, "SoNguoiToiDa": 2},
    {"SoPhong": "P201", "LoaiPhong": "Chất lượng cao", "DonGia": 900000, "SoNguoiToiDa": 2},
]

# Dữ liệu giả cho bảng DANGKY_O (NgayKetThuc = None nghĩa là đang ở)
ds_dangky_o = [
    {"MaDKO": 1, "MaSV": "B24DCCN001", "SoPhong": "P101", "NgayBatDau": "2026-09-01",
     "NgayKetThuc": None, "DonGiaThangApDung": 500000},
    {"MaDKO": 2, "MaSV": "B24DCCN002", "SoPhong": "P101", "NgayBatDau": "2026-09-01",
     "NgayKetThuc": None, "DonGiaThangApDung": 500000},
    {"MaDKO": 3, "MaSV": "B24DCCN003", "SoPhong": "P102", "NgayBatDau": "2026-09-05",
     "NgayKetThuc": None, "DonGiaThangApDung": 500000},
]


def so_nguoi_dang_o(so_phong):
    """Đếm số người đang ở một phòng (các bản đăng ký chưa có ngày kết thúc)."""
    return sum(1 for dk in ds_dangky_o
               if dk["SoPhong"] == so_phong and dk["NgayKetThuc"] is None)

def tim_sv(masv):
    return next((sv for sv in ds_sv if sv["MaSV"] == masv), None)


def tim_phong(so_phong):
    return next((p for p in ds_phong if p["SoPhong"] == so_phong), None)


def dang_ky_dang_o(masv):
    """Trả về bản đăng ký đang ở của sinh viên, hoặc None nếu không ở đâu."""
    return next((dk for dk in ds_dangky_o
                 if dk["MaSV"] == masv and dk["NgayKetThuc"] is None), None)

# Dữ liệu giả cho bảng KHACH
ds_khach = [
    {"CMTKhach": "038200000001", "HoTen": "Nguyễn Thị Lan", "NgaySinh": "1978-05-12", "SDT": "0903111222"},
    {"CMTKhach": "038200000002", "HoTen": "Trần Văn Hùng", "NgaySinh": "1980-09-03", "SDT": "0903333444"},
    {"CMTKhach": "038200000003", "HoTen": "Lê Thu Hà", "NgaySinh": "2005-02-20", "SDT": ""},
]

# Dữ liệu giả cho bảng LUOT_THAM (ThoiDiemDen dạng "YYYY-MM-DD HH:MM")
ds_luot_tham = [
    {"MaLuotTham": 1, "CMTKhach": "038200000001", "MaSV": "B24DCCN001", "ThoiDiemDen": "2026-10-19 09:30"},
    {"MaLuotTham": 2, "CMTKhach": "038200000001", "MaSV": "B24DCCN001", "ThoiDiemDen": "2026-10-20 08:15"},
    {"MaLuotTham": 3, "CMTKhach": "038200000002", "MaSV": "B24DCCN002", "ThoiDiemDen": "2026-10-14 15:00"},
    {"MaLuotTham": 4, "CMTKhach": "038200000003", "MaSV": "B24DCCN001", "ThoiDiemDen": "2026-10-05 18:20"},
    {"MaLuotTham": 5, "CMTKhach": "038200000002", "MaSV": "B24DCCN002", "ThoiDiemDen": "2026-09-28 10:00"},
    {"MaLuotTham": 6, "CMTKhach": "038200000001", "MaSV": "B24DCCN003", "ThoiDiemDen": "2026-10-20 14:45"},
]


def tim_khach(cmt):
    return next((k for k in ds_khach if k["CMTKhach"] == cmt), None)


def khoang_ky(ky, ngay_tc):
    """Trả về (từ ngày, đến ngày) của tuần hoặc tháng chứa ngay_tc. 'tatca' -> (None, None)."""
    if ky == "tuan":
        tu = ngay_tc - timedelta(days=ngay_tc.weekday())   # thứ Hai
        den = tu + timedelta(days=6)                        # Chủ nhật
    elif ky == "thang":
        tu = ngay_tc.replace(day=1)
        den = (tu + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    else:
        return None, None
    return tu.strftime("%Y-%m-%d"), den.strftime("%Y-%m-%d")


@app.template_filter("gio")
def dinh_dang_gio(chuoi):
    """Đổi 2026-10-19 09:30 thành 09:30 19/10/2026."""
    try:
        return datetime.strptime(chuoi, "%Y-%m-%d %H:%M").strftime("%H:%M %d/%m/%Y")
    except (ValueError, TypeError):
        return chuoi or ""


@app.template_filter("tien")
def dinh_dang_tien(so):
    """Đổi 500000 thành 500.000đ."""
    try:
        return f"{int(so):,}".replace(",", ".") + "đ"
    except (ValueError, TypeError):
        return so


@app.template_filter("ngay")
def dinh_dang_ngay(chuoi):
    """Đổi 2006-03-21 thành 21/03/2006 để hiển thị."""
    try:
        return datetime.strptime(chuoi, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return chuoi or ""

# Dữ liệu giả cho bảng DICHVU
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
            "SoLuong": so_luong, "DonGiaApDung": dv["DonGia"],
            "ThanhTien": so_luong * dv["DonGia"]}


# Dữ liệu giả cho bảng SUDUNG_DV
ds_sudung = [
    tao_luot_dung(1, "B24DCCN001", "DV01", "2026-10-03 18:00", 3),
    tao_luot_dung(2, "B24DCCN001", "DV02", "2026-10-05 12:00", 4),
    tao_luot_dung(3, "B24DCCN001", "DV02", "2026-10-12 12:10", 2),
    tao_luot_dung(4, "B24DCCN002", "DV01", "2026-10-07 19:00", 2),
    tao_luot_dung(5, "B24DCCN002", "DV04", "2026-10-10 09:00", 1),
    tao_luot_dung(6, "B24DCCN002", "DV02", "2026-10-15 18:30", 3),
    tao_luot_dung(7, "B24DCCN003", "DV02", "2026-10-02 12:00", 5),
    tao_luot_dung(8, "B24DCCN003", "DV03", "2026-10-18 07:30", 2),
    tao_luot_dung(9, "B24DCCN003", "DV01", "2026-09-28 20:00", 4),
    tao_luot_dung(10, "B24DCCN001", "DV04", "2026-10-19 15:00", 2),
]

GIA_VE_THANG = 100000
TOI_DA_XE = 2
DS_LOAI_XE = ["Xe đạp", "Xe máy", "Xe điện"]

# Dữ liệu giả cho bảng XE
ds_xe = [
    {"BienSo": "29A1-12345", "LoaiXe": "Xe máy"},
    {"BienSo": "29B2-67890", "LoaiXe": "Xe máy"},
    {"MaDKXe": 2, "MaSV": "B24DCCN001", "BienSo": "XD-B24DCCN001", "NgayBatDau": "2026-09-01",
     "NgayKetThuc": None, "DonGiaThangApDung": GIA_VE_THANG},
    {"BienSo": "29MD-11111", "LoaiXe": "Xe điện"},
]

# Dữ liệu giả cho bảng DANGKY_XE_THANG (NgayKetThuc = None nghĩa là còn hiệu lực)
# B24DCCN001 đã đủ 2 xe để thử chặn xe thứ 3
ds_dk_xe = [
    {"MaDKXe": 1, "MaSV": "B24DCCN001", "BienSo": "29A1-12345", "NgayBatDau": "2026-09-01",
     "NgayKetThuc": None, "DonGiaThangApDung": GIA_VE_THANG},
    {"MaDKXe": 2, "MaSV": "B24DCCN001", "BienSo": "XD-0001", "NgayBatDau": "2026-09-01",
     "NgayKetThuc": None, "DonGiaThangApDung": GIA_VE_THANG},
    {"MaDKXe": 3, "MaSV": "B24DCCN002", "BienSo": "29B2-67890", "NgayBatDau": "2026-09-05",
     "NgayKetThuc": None, "DonGiaThangApDung": GIA_VE_THANG},
]


def dem_xe_hieu_luc(masv):
    """Số xe vé tháng còn hiệu lực của một sinh viên."""
    return sum(1 for d in ds_dk_xe if d["MaSV"] == masv and d["NgayKetThuc"] is None)


def dk_xe_hieu_luc_cua_bien(bien_so):
    """Bản đăng ký còn hiệu lực của một biển số (hoặc None)."""
    return next((d for d in ds_dk_xe
                 if d["BienSo"] == bien_so and d["NgayKetThuc"] is None), None)


def tim_xe(bien_so):
    return next((x for x in ds_xe if x["BienSo"] == bien_so), None)

def tao_ma_xe_dap(masv):
    """Xe đạp không có biển số: dùng mã sinh viên làm mã xe (XD-<MaSV>)."""
    ma = f"XD-{masv}"
    if dk_xe_hieu_luc_cua_bien(ma):
        ma += "-2"   # sinh viên đã có 1 xe đạp còn hiệu lực
    return ma

@app.route("/")
def trang_chu():
    return redirect(url_for("sinhvien"))


@app.route("/sinhvien", methods=["GET", "POST"])
def sinhvien():
    form = {}
    if request.method == "POST":
        form = request.form
        masv = form["MaSV"].strip()
        socmt = form["SoCMT"].strip()

        if any(sv["MaSV"] == masv for sv in ds_sv):
            flash(f"Mã sinh viên {masv} đã tồn tại.", "danger")
        elif any(sv["SoCMT"] == socmt for sv in ds_sv):
            flash(f"Số CMT/CCCD {socmt} đã được dùng bởi sinh viên khác.", "danger")
        else:
            ds_sv.append({
                "MaSV": masv,
                "HoTen": form["HoTen"].strip(),
                "SoCMT": socmt,
                "NgaySinh": form["NgaySinh"],
                "GioiTinh": form["GioiTinh"],
                "SDT": form["SDT"].strip(),
                "Lop": form["Lop"],
                "QueQuan": form["QueQuan"].strip(),
            })
            flash("Thêm sinh viên thành công.", "success")
            return redirect(url_for("sinhvien"))  # PRG: tránh gửi lại khi F5

    # Nếu có lỗi, form vẫn giữ nguyên dữ liệu người dùng đã nhập
    return render_template("sinhvien.html", ds=ds_sv, ds_lop=DS_LOP, form=form)


@app.route("/sinhvien/xoa/<masv>", methods=["POST"])
def xoa_sinhvien(masv):
    if dang_ky_dang_o(masv):
        flash(f"Không thể xóa sinh viên {masv} vì đang ở phòng. Hãy trả phòng trước.", "danger")
    else:
        ds_sv[:] = [sv for sv in ds_sv if sv["MaSV"] != masv]
        flash(f"Đã xóa sinh viên {masv}.", "warning")
    return redirect(url_for("sinhvien"))

@app.route("/phong", methods=["GET", "POST"])
def phong():
    form = {}
    if request.method == "POST":
        form = request.form
        so_phong = form["SoPhong"].strip().upper()

        try:
            don_gia = int(form["DonGia"])
            toi_da = int(form["SoNguoiToiDa"])
        except ValueError:
            flash("Đơn giá và số người tối đa phải là số nguyên.", "danger")
            don_gia = toi_da = 0

        if don_gia and toi_da:
            if any(p["SoPhong"] == so_phong for p in ds_phong):
                flash(f"Phòng {so_phong} đã tồn tại.", "danger")
            elif don_gia <= 0 or toi_da <= 0:
                flash("Đơn giá và số người tối đa phải lớn hơn 0.", "danger")
            else:
                ds_phong.append({"SoPhong": so_phong, "LoaiPhong": form["LoaiPhong"],
                                 "DonGia": don_gia, "SoNguoiToiDa": toi_da})
                flash(f"Đã thêm phòng {so_phong}.", "success")
                return redirect(url_for("phong"))

    # Ghép thêm số người đang ở vào mỗi phòng để hiển thị
    ds_hien_thi = [{**p, "DangO": so_nguoi_dang_o(p["SoPhong"])} for p in ds_phong]
    tong_cho = sum(p["SoNguoiToiDa"] for p in ds_phong)
    tong_dang_o = sum(p["DangO"] for p in ds_hien_thi)

    return render_template("phong.html", ds=ds_hien_thi, ds_loai=DS_LOAI_PHONG,
                           form=form, tong_cho=tong_cho, tong_dang_o=tong_dang_o)


@app.route("/phong/xoa/<so_phong>", methods=["POST"])
def xoa_phong(so_phong):
    if so_nguoi_dang_o(so_phong) > 0:
        flash(f"Không thể xóa phòng {so_phong} vì đang có người ở.", "danger")
    else:
        ds_phong[:] = [p for p in ds_phong if p["SoPhong"] != so_phong]
        flash(f"Đã xóa phòng {so_phong}.", "warning")
    return redirect(url_for("phong"))

@app.route("/dangky-o", methods=["GET", "POST"])
def dangky_o():
    form = {}
    if request.method == "POST":
        form = request.form
        masv = form["MaSV"]
        so_phong = form["SoPhong"]
        ngay = form["NgayBatDau"]
        sv = tim_sv(masv)
        p = tim_phong(so_phong)
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
                phong_cu = dang_ky_dang_o(masv)["SoPhong"]
                loi = (f"Sinh viên {masv} đang ở phòng {phong_cu}. "
                       "Hãy trả phòng cũ trước khi đăng ký phòng mới.")
            elif so_nguoi_dang_o(so_phong) >= p["SoNguoiToiDa"]:
                loi = (f"Phòng {so_phong} đã đủ {p['SoNguoiToiDa']}/{p['SoNguoiToiDa']} người, "
                       "không thể đăng ký thêm.")

        if loi:
            flash(loi, "danger")
        else:
            ma_moi = max((dk["MaDKO"] for dk in ds_dangky_o), default=0) + 1
            ds_dangky_o.append({
                "MaDKO": ma_moi,
                "MaSV": masv,
                "SoPhong": so_phong,
                "NgayBatDau": ngay,
                "NgayKetThuc": None,
                # Đơn giá lấy từ phòng tại thời điểm đăng ký, không cho nhập tay
                "DonGiaThangApDung": p["DonGia"],
            })
            flash(f"Đã đăng ký sinh viên {masv} vào phòng {so_phong}.", "success")
            return redirect(url_for("dangky_o"))

    # Sinh viên chưa ở đâu thì mới được chọn để đăng ký
    ds_sv_trong = [sv for sv in ds_sv if dang_ky_dang_o(sv["MaSV"]) is None]
    ds_phong_ht = []
    for p in ds_phong:
        dang_o = so_nguoi_dang_o(p["SoPhong"])
        ds_phong_ht.append({**p, "DangO": dang_o, "Con": p["SoNguoiToiDa"] - dang_o})

    # Ghép thông tin sinh viên vào mỗi bản đăng ký, bản đang ở xếp lên trên
    ds_dk = []
    for dk in ds_dangky_o:
        sv = tim_sv(dk["MaSV"])
        ds_dk.append({**dk, "HoTen": sv["HoTen"] if sv else "(đã xóa)"})
    ds_dk.sort(key=lambda d: (d["NgayKetThuc"] is not None, -d["MaDKO"]))

    return render_template("dangky_o.html", ds_dk=ds_dk, ds_sv_trong=ds_sv_trong,
                           ds_phong=ds_phong_ht, form=form,
                           hom_nay=datetime.now().strftime("%Y-%m-%d"))


@app.route("/dangky-o/tra/<int:ma_dko>", methods=["POST"])
def tra_phong(ma_dko):
    dk = next((d for d in ds_dangky_o if d["MaDKO"] == ma_dko), None)
    if dk is None:
        flash("Không tìm thấy bản đăng ký.", "danger")
    elif dk["NgayKetThuc"] is not None:
        flash("Bản đăng ký này đã được trả phòng rồi.", "danger")
    else:
        hom_nay = datetime.now().strftime("%Y-%m-%d")
        # Ngày trả không được sớm hơn ngày bắt đầu
        dk["NgayKetThuc"] = max(hom_nay, dk["NgayBatDau"])
        flash(f"Đã trả phòng {dk['SoPhong']} cho sinh viên {dk['MaSV']}.", "warning")
    return redirect(url_for("dangky_o"))

@app.route("/khach", methods=["GET", "POST"])
def khach():
    form = {}
    if request.method == "POST":
        form = request.form
        cmt = form["CMTKhach"].strip()
        masv = form["MaSV"]
        thoi_diem = form["ThoiDiemDen"].replace("T", " ")
        loi = None

        try:
            datetime.strptime(thoi_diem, "%Y-%m-%d %H:%M")
        except ValueError:
            loi = "Thời điểm đến không hợp lệ."

        if loi is None and tim_sv(masv) is None:
            loi = "Không tìm thấy sinh viên được thăm."

        # Khách mới (CMT chưa có) thì bắt buộc nhập họ tên và ngày sinh
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
            ds_luot_tham.append({"MaLuotTham": ma_moi, "CMTKhach": cmt,
                                 "MaSV": masv, "ThoiDiemDen": thoi_diem})
            flash("Đã ghi nhận lượt thăm.", "success")
            return redirect(url_for("khach"))

    # ----- Bộ lọc thống kê: tuần / tháng / tất cả -----
    ky = request.args.get("ky", "tuan")
    if ky not in ("tuan", "thang", "tatca"):
        ky = "tuan"
    hom_nay = datetime.now()
    try:
        ngay_tc = datetime.strptime(request.args.get("ngay", ""), "%Y-%m-%d")
    except ValueError:
        ngay_tc = hom_nay
    tu, den = khoang_ky(ky, ngay_tc)

    ds_loc = [l for l in ds_luot_tham
              if tu is None or tu <= l["ThoiDiemDen"][:10] <= den]

    # Gom nhóm theo (sinh viên, khách) để đếm số lần đến
    nhom = {}
    for l in ds_loc:
        nhom.setdefault((l["MaSV"], l["CMTKhach"]), []).append(l["ThoiDiemDen"])
    ds_thongke = []
    for (masv, cmt), cac_lan in nhom.items():
        sv, k = tim_sv(masv), tim_khach(cmt)
        ds_thongke.append({
            "MaSV": masv, "HoTenSV": sv["HoTen"] if sv else "(đã xóa)",
            "Lop": sv["Lop"] if sv else "",
            "CMTKhach": cmt, "HoTenKhach": k["HoTen"] if k else "",
            "SoLan": len(cac_lan), "LanCuoi": max(cac_lan),
        })
    ds_thongke.sort(key=lambda d: (d["MaSV"], -d["SoLan"]))

    # Chi tiết từng lượt trong kỳ, mới nhất lên trên
    ds_chitiet = []
    for l in sorted(ds_loc, key=lambda x: x["ThoiDiemDen"], reverse=True):
        sv, k = tim_sv(l["MaSV"]), tim_khach(l["CMTKhach"])
        ds_chitiet.append({**l, "HoTenSV": sv["HoTen"] if sv else "(đã xóa)",
                           "HoTenKhach": k["HoTen"] if k else ""})

    return render_template(
        "khach.html", form=form, ds_sv=ds_sv, ds_khach=ds_khach,
        ds_thongke=ds_thongke, ds_chitiet=ds_chitiet,
        ky=ky, ngay=ngay_tc.strftime("%Y-%m-%d"), tu=tu, den=den,
        so_khach=len({l["CMTKhach"] for l in ds_loc}),
        so_sv=len({l["MaSV"] for l in ds_loc}),
        bay_gio=hom_nay.strftime("%Y-%m-%dT%H:%M"),
    )

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
            # Đơn giá và thành tiền do backend tính, không nhận từ form
            ds_sudung.append(tao_luot_dung(ma_moi, masv, madv, thoi_diem, so_luong))
            sv = tim_sv(masv)
            flash(f"Đã ghi nhận cho {sv['HoTen']}: {tim_dv(madv)['TenDV']} x {so_luong}.", "success")
            return redirect(url_for("dichvu"))

    hom_nay = datetime.now()

    # Phòng hiện tại của từng sinh viên (chỉ tính bản đăng ký đang ở)
    phong_cua = {dk["MaSV"]: dk["SoPhong"] for dk in ds_dangky_o if dk["NgayKetThuc"] is None}
    ds_sv_ht = [{**sv, "Phong": phong_cua.get(sv["MaSV"], "")} for sv in ds_sv]

    # ----- Bộ lọc thống kê: khoảng ngày + phòng + lớp -----
    tu = request.args.get("tu", hom_nay.replace(day=1).strftime("%Y-%m-%d"))
    den = request.args.get("den", hom_nay.strftime("%Y-%m-%d"))
    loc_phong = request.args.get("phong", "")
    loc_lop = request.args.get("lop", "")
    try:
        datetime.strptime(tu, "%Y-%m-%d")
        datetime.strptime(den, "%Y-%m-%d")
    except ValueError:
        tu, den = hom_nay.replace(day=1).strftime("%Y-%m-%d"), hom_nay.strftime("%Y-%m-%d")
    if tu > den:
        flash("Ngày bắt đầu phải không muộn hơn ngày kết thúc.", "danger")
        tu, den = den, tu

    # Sinh viên thỏa bộ lọc phòng/lớp
    hop_le = {sv["MaSV"]: sv for sv in ds_sv_ht
              if (not loc_phong or sv["Phong"] == loc_phong)
              and (not loc_lop or sv["Lop"] == loc_lop)}

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
                           "Phong": sv["Phong"] or "—",
                           "TenDV": dv["TenDV"] if dv else madv,
                           "DonViTinh": dv["DonViTinh"] if dv else "", **g})
    ds_thongke.sort(key=lambda d: (d["Phong"], d["MaSV"], d["TenDV"]))
    tong_tien = sum(d["TongTien"] for d in ds_thongke)

    # 8 lượt dùng gần nhất, để kiểm tra và xóa khi nhập nhầm
    ds_gan_day = []
    for s in sorted(ds_sudung, key=lambda x: x["ThoiDiemSuDung"], reverse=True)[:8]:
        sv, dv = tim_sv(s["MaSV"]), tim_dv(s["MaDV"])
        ds_gan_day.append({**s, "HoTenSV": sv["HoTen"] if sv else "(đã xóa)",
                           "TenDV": dv["TenDV"] if dv else s["MaDV"]})

    return render_template("dichvu.html", form=form, ds_sv=ds_sv_ht, ds_dichvu=ds_dichvu,
                           ds_phong=[p["SoPhong"] for p in ds_phong], ds_lop=DS_LOP,
                           ds_thongke=ds_thongke, ds_gan_day=ds_gan_day,
                           tu=tu, den=den, loc_phong=loc_phong, loc_lop=loc_lop,
                           tong_tien=tong_tien, bay_gio=hom_nay.strftime("%Y-%m-%dT%H:%M"))


@app.route("/dichvu/xoa/<int:ma>", methods=["POST"])
def xoa_luot_dung(ma):
    ds_sudung[:] = [s for s in ds_sudung if s["MaSuDung"] != ma]
    flash(f"Đã xóa lượt sử dụng #{ma}.", "warning")
    return redirect(url_for("dichvu"))

@app.route("/xe-thang", methods=["GET", "POST"])
def xe_thang():
    form = {}
    if request.method == "POST":
        form = request.form
        masv = form["MaSV"]
        bien_so = form.get("BienSo", "").strip().upper()
        loai = form["LoaiXe"]
        if loai == "Xe đạp":
            bien_so = tao_ma_xe_dap(masv)   # xe đạp quản lý theo mã sinh viên
        ngay = form["NgayBatDau"]
        loi = None

        try:
            datetime.strptime(ngay, "%Y-%m-%d")
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
                loi = (f"Sinh viên {masv} đã đăng ký đủ {TOI_DA_XE}/{TOI_DA_XE} xe vé tháng, "
                       "không thể đăng ký thêm.")
            elif dk_xe_hieu_luc_cua_bien(bien_so):
                chu = dk_xe_hieu_luc_cua_bien(bien_so)["MaSV"]
                loi = f"Biển số {bien_so} đang được sinh viên {chu} đăng ký vé tháng."

        if loi:
            flash(loi, "danger")
        else:
            if tim_xe(bien_so) is None:
                ds_xe.append({"BienSo": bien_so, "LoaiXe": loai})
            ma_moi = max((d["MaDKXe"] for d in ds_dk_xe), default=0) + 1
            ds_dk_xe.append({"MaDKXe": ma_moi, "MaSV": masv, "BienSo": bien_so,
                             "NgayBatDau": ngay, "NgayKetThuc": None,
                             "DonGiaThangApDung": GIA_VE_THANG})
            flash(f"Đã đăng ký vé tháng cho xe {bien_so} (sinh viên {masv}).", "success")
            return redirect(url_for("xe_thang"))

    phong_cua = {dk["MaSV"]: dk["SoPhong"] for dk in ds_dangky_o if dk["NgayKetThuc"] is None}
    ds_sv_ht = [{**sv, "Phong": phong_cua.get(sv["MaSV"], ""),
                 "SoXe": dem_xe_hieu_luc(sv["MaSV"])} for sv in ds_sv]

    ds_hien_thi = []
    for d in ds_dk_xe:
        sv, xe = tim_sv(d["MaSV"]), tim_xe(d["BienSo"])
        ds_hien_thi.append({**d, "HoTen": sv["HoTen"] if sv else "(đã xóa)",
                            "Phong": phong_cua.get(d["MaSV"], "") or "—",
                            "LoaiXe": xe["LoaiXe"] if xe else ""})
    # Xe còn hiệu lực lên trên
    ds_hien_thi.sort(key=lambda d: (d["NgayKetThuc"] is not None, -d["MaDKXe"]))

    return render_template("xe_thang.html", form=form, ds_sv=ds_sv_ht, ds_dk=ds_hien_thi,
                           ds_phong=[p["SoPhong"] for p in ds_phong], ds_lop=DS_LOP,
                           ds_loai=DS_LOAI_XE, toi_da=TOI_DA_XE, gia=GIA_VE_THANG,
                           hom_nay=datetime.now().strftime("%Y-%m-%d"))


@app.route("/xe-thang/huy/<int:ma>", methods=["POST"])
def huy_xe(ma):
    d = next((x for x in ds_dk_xe if x["MaDKXe"] == ma), None)
    if d is None:
        flash("Không tìm thấy bản đăng ký xe.", "danger")
    elif d["NgayKetThuc"] is not None:
        flash("Vé tháng này đã được hủy trước đó.", "danger")
    else:
        hom_nay = datetime.now().strftime("%Y-%m-%d")
        d["NgayKetThuc"] = max(hom_nay, d["NgayBatDau"])
        flash(f"Đã hủy vé tháng xe {d['BienSo']}.", "warning")
    return redirect(url_for("xe_thang"))

if __name__ == "__main__":
    app.run(debug=True)