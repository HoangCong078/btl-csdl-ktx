from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash

# Dữ liệu, hằng số và các hàm nghiệp vụ nằm trong du_lieu.py
from du_lieu import *  # noqa: F401,F403

app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "ktx-dev"  # cần có để dùng flash()


# ===================== HIỂN THỊ =====================
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


def hop_le_ngay(chuoi):
    try:
        datetime.strptime(chuoi, "%Y-%m-%d")
        return True
    except ValueError:
        return False


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


def danh_sach_nam(nam):
    nam_nay = datetime.now().year
    return sorted({nam_nay - 1, nam_nay, nam_nay + 1, nam})


# ===================== TRANG CHỦ =====================
@app.route("/")
def trang_chu():
    return redirect(url_for("sinhvien"))


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


# ===================== PHÒNG (gồm xếp người, trả phòng) =====================
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

    ds = []
    for p in ds_phong:
        nguoi = []
        for dk in ds_dangky_o:
            if dk["SoPhong"] == p["SoPhong"] and dk["NgayKetThuc"] is None:
                sv = tim_sv(dk["MaSV"])
                nguoi.append({"MaDKO": dk["MaDKO"], "MaSV": dk["MaSV"],
                              "HoTen": sv["HoTen"] if sv else "(đã xóa)"})
        ds.append({**p, "Nguoi": nguoi, "DangO": len(nguoi)})
    ds_sv_trong = [sv for sv in ds_sv if dang_ky_dang_o(sv["MaSV"]) is None]
    return render_template("phong.html", ds=ds, ds_loai=DS_LOAI_PHONG, ds_sv_trong=ds_sv_trong,
                           form=form, hom_nay=ngay_moc(0))


@app.route("/phong/xoa/<so_phong>", methods=["POST"])
def xoa_phong(so_phong):
    if so_nguoi_dang_o(so_phong) > 0:
        flash(f"Không thể xóa phòng {so_phong} vì đang có người ở.", "danger")
    else:
        ds_phong[:] = [p for p in ds_phong if p["SoPhong"] != so_phong]
        flash(f"Đã xóa phòng {so_phong}.", "warning")
    return redirect(url_for("phong"))


@app.route("/phong/xep", methods=["POST"])
def xep_phong():
    masv, so_phong, ngay = request.form["MaSV"], request.form["SoPhong"], request.form["NgayBatDau"]
    sv, p = tim_sv(masv), tim_phong(so_phong)
    loi = None
    if not hop_le_ngay(ngay):
        loi = "Ngày bắt đầu không hợp lệ."
    elif sv is None:
        loi = "Không tìm thấy sinh viên đã chọn."
    elif p is None:
        loi = "Không tìm thấy phòng đã chọn."
    elif dang_ky_dang_o(masv):
        loi = f"{sv['HoTen']} đang ở phòng {dang_ky_dang_o(masv)['SoPhong']}. Hãy trả phòng cũ trước."
    elif so_nguoi_dang_o(so_phong) >= p["SoNguoiToiDa"]:
        loi = f"Phòng {so_phong} đã đủ {p['SoNguoiToiDa']}/{p['SoNguoiToiDa']} người."
    if loi:
        flash(loi, "danger")
    else:
        ma_moi = max((d["MaDKO"] for d in ds_dangky_o), default=0) + 1
        ds_dangky_o.append({"MaDKO": ma_moi, "MaSV": masv, "SoPhong": so_phong,
                            "NgayBatDau": ngay, "NgayKetThuc": None,
                            "DonGiaThangApDung": p["DonGia"]})  # lấy từ phòng, không nhập tay
        flash(f"Đã xếp {sv['HoTen']} vào phòng {so_phong}.", "success")
    return redirect(url_for("phong"))


@app.route("/phong/tra/<int:ma_dko>", methods=["POST"])
def tra_phong(ma_dko):
    dk = next((d for d in ds_dangky_o if d["MaDKO"] == ma_dko), None)
    if dk is None:
        flash("Không tìm thấy bản đăng ký.", "danger")
    elif dk["NgayKetThuc"] is not None:
        flash("Đã trả phòng rồi.", "danger")
    else:
        dk["NgayKetThuc"] = max(ngay_moc(0), dk["NgayBatDau"])
        flash(f"Đã trả phòng {dk['SoPhong']} cho {dk['MaSV']}.", "warning")
    return redirect(url_for("phong"))


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

    # Gom theo (sinh viên, khách) để đếm số lần đến
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
            # Đơn giá và thành tiền do backend tính, không nhận từ form
            ds_sudung.append(tao_luot_dung(ma_moi, masv, madv, thoi_diem, so_luong))
            flash(f"Đã ghi nhận cho {tim_sv(masv)['HoTen']}: {tim_dv(madv)['TenDV']} x {so_luong}.", "success")
            return redirect(url_for("dichvu"))

    pc = phong_cua()
    ds_sv_ht = [{**sv, "Phong": pc.get(sv["MaSV"], "")} for sv in ds_sv]

    # Bộ lọc thống kê: khoảng ngày (mặc định 30 ngày gần nhất) + phòng + lớp
    tu = request.args.get("tu", ngay_moc(-30))
    den = request.args.get("den", ngay_moc(0))
    loc_phong, loc_lop = request.args.get("phong", ""), request.args.get("lop", "")
    if not (hop_le_ngay(tu) and hop_le_ngay(den)):
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
                           bay_gio=datetime.now().strftime("%Y-%m-%dT%H:%M"))


@app.route("/dichvu/xoa/<int:ma>", methods=["POST"])
def xoa_luot_dung(ma):
    ds_sudung[:] = [s for s in ds_sudung if s["MaSuDung"] != ma]
    flash(f"Đã xóa lượt sử dụng #{ma}.", "warning")
    return redirect(url_for("dichvu"))


# ===================== XE (vé tháng + quẹt xe) =====================
@app.route("/xe")
def xe():
    hom_nay = ngay_moc(0)
    hom_nay_dt = datetime.strptime(hom_nay, "%Y-%m-%d")
    pc = phong_cua()
    bien_con_han = {d["BienSo"] for d in ds_dk_xe if con_han(d)}

    ds_ve = []
    for d in ds_dk_xe:
        sv, x = tim_sv(d["MaSV"]), tim_xe(d["BienSo"])
        ds_ve.append({
            **d, "HoTen": sv["HoTen"] if sv else "(đã xóa)", "LoaiXe": x["LoaiXe"] if x else "",
            "ConHan": con_han(d), "DaCoVeMoi": d["BienSo"] in bien_con_han,
            "SoLuot": luot_trong_ngay(d["MaDKXe"], hom_nay),
            "TiepTheo": "Gửi" if hanh_dong_tiep(d["MaDKXe"]) == "Gui" else "Lấy",
            "PhiTiep": phi_luot_tiep(d["MaDKXe"], hom_nay)})
    ds_ve.sort(key=lambda d: (not d["ConHan"], -d["MaDKXe"]))

    ds_sv_ht = [{**sv, "Phong": pc.get(sv["MaSV"], ""), "SoXe": dem_xe_hieu_luc(sv["MaSV"])} for sv in ds_sv]

    ds_gan_day = []
    for l in sorted(ds_luot_xe, key=lambda x: x["ThoiDiem"], reverse=True)[:8]:
        d = next((x for x in ds_dk_xe if x["MaDKXe"] == l["MaDKXe"]), None)
        sv = tim_sv(d["MaSV"]) if d else None
        ds_gan_day.append({**l, "BienSo": d["BienSo"] if d else "?", "HoTen": sv["HoTen"] if sv else ""})

    return render_template("xe.html", ds_ve=ds_ve, ds_sv=ds_sv_ht, ds_gan_day=ds_gan_day,
                           ds_phong=[p["SoPhong"] for p in ds_phong], ds_lop=DS_LOP, ds_loai=DS_LOAI_XE,
                           toi_da=TOI_DA_XE, gia=GIA_VE_THANG, mien_phi=MIEN_PHI_NGAY,
                           phi=PHI_PHAT_SINH, hom_nay=hom_nay)


@app.route("/xe/quet", methods=["POST"])
def quet_xe():
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
            flash(f"{ten_hd} xe {d['BienSo']} ({ten}) - lượt {thu_tu} trong ngày, thu {f_tien(phi)}.", "warning")
        else:
            flash(f"{ten_hd} xe {d['BienSo']} ({ten}) - lượt {thu_tu} trong ngày, miễn phí.", "success")
    return redirect(url_for("xe"))


@app.route("/xe/dangky", methods=["POST"])
def xe_thang():
    form = request.form
    masv, loai, ngay = form.get("MaSV", ""), form.get("LoaiXe", ""), form.get("NgayBatDau", "")
    bien_so = form.get("BienSo", "").strip().upper()
    if loai == "Xe đạp":
        bien_so = tao_ma_xe_dap(masv)   # xe đạp quản lý theo mã sinh viên
    loi = None
    if not hop_le_ngay(ngay):
        loi = "Ngày bắt đầu không hợp lệ."
    elif ngay > ngay_moc(0):
        loi = "Ngày bắt đầu không được ở tương lai."
    elif tim_sv(masv) is None:
        loi = "Không tìm thấy sinh viên đã chọn."
    elif not bien_so:
        loi = "Vui lòng nhập biển số xe."
    elif loai not in DS_LOAI_XE:
        loi = "Loại xe không hợp lệ."
    elif dem_xe_hieu_luc(masv) >= TOI_DA_XE:
        loi = f"Sinh viên {masv} đã đủ {TOI_DA_XE}/{TOI_DA_XE} xe vé tháng."
    elif dk_xe_hieu_luc_cua_bien(bien_so):
        loi = f"Xe {bien_so} đang có vé còn hạn của {dk_xe_hieu_luc_cua_bien(bien_so)['MaSV']}."
    if loi:
        flash(loi, "danger")
    else:
        if tim_xe(bien_so) is None:
            ds_xe.append({"BienSo": bien_so, "LoaiXe": loai})
        ma_moi = max((d["MaDKXe"] for d in ds_dk_xe), default=0) + 1
        ds_dk_xe.append({"MaDKXe": ma_moi, "MaSV": masv, "BienSo": bien_so, "NgayBatDau": ngay,
            "NgayKetThuc": None, "DonGiaThangApDung": GIA_VE_THANG})
        flash(f"Đã đăng ký vé tháng cho xe {bien_so}.", "success")
    return redirect(url_for("xe"))


@app.route("/xe/huy/<int:ma>", methods=["POST"])
def huy_xe(ma):
    d = next((x for x in ds_dk_xe if x["MaDKXe"] == ma), None)
    if d is None:
        flash("Không tìm thấy vé.", "danger")
    elif d["NgayKetThuc"] is not None:
        flash("Vé này đã hủy rồi.", "danger")
    else:
        d["NgayKetThuc"] = max(ngay_moc(0), d["NgayBatDau"])
        flash(f"Đã hủy vé xe {d['BienSo']}.", "warning")
    return redirect(url_for("xe"))


@app.route("/xe/xoa/<int:ma>", methods=["POST"])
def xoa_luot_xe(ma):
    ds_luot_xe[:] = [l for l in ds_luot_xe if l["MaLuot"] != ma]
    flash(f"Đã xóa lượt quét #{ma}.", "warning")
    return redirect(url_for("xe"))


# ===================== HÓA ĐƠN =====================
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
    return render_template("hoadon.html", ds=ds, thang=thang, nam=nam, ds_nam=danh_sach_nam(nam),
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
                           nam=nam, ds_nam=danh_sach_nam(nam),
                           thang_ht=bay_gio.month if nam == bay_gio.year else 0)


if __name__ == "__main__":
    app.run(debug=True)