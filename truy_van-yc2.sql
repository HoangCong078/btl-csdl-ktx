-- BTL CSDL - Project 2: Quan ly ky tuc xa
-- Nguoi 2: Bon truy van theo yeu cau YC2
-- Chay sau KTX_phanDDL.sql va du_lieu_mau.sql

USE KTX;
-- Dong bo chuoi trong phien lam viec voi collation cua CSDL.
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- =========================================================
-- TRUY VAN 1: TONG TIEN MOI SINH VIEN PHAI TRA TRONG THANG
-- =========================================================

-- Doi hai gia tri nay de xem thang khac.
SET @thang = MONTH(CURDATE());
SET @nam = YEAR(CURDATE());

-- NULL: xem tat ca; hoac dien ma nhu 'B24DCCN001'.
SET @ma_sv = NULL;
-- Chi can doi NULL thanh 'B24DCCN001' de loc; WHERE tu chuan hoa collation.

SET @dau_thang = STR_TO_DATE(
    CONCAT(@nam, '-', @thang, '-01'),
    '%Y-%c-%d'
);
SET @thang_sau = DATE_ADD(@dau_thang, INTERVAL 1 MONTH);

WITH cac_khoan AS (
    -- 1. Tien phong: dang ky giao voi thang thi tinh du thang.
    SELECT
        MaSV,
        'Phong' AS LoaiPhi,
        DonGiaThangApDung AS ThanhTien
    FROM DANGKY_O
    WHERE NgayBatDau < @thang_sau
      AND (
          NgayKetThuc IS NULL
          OR NgayKetThuc >= @dau_thang
      )

    UNION ALL

    -- 2. Tien dich vu theo gia da luu luc su dung.
    SELECT
        MaSV,
        'DichVu',
        SoLuong * DonGiaApDung
    FROM SUDUNG_DV
    WHERE ThoiDiemSuDung >= @dau_thang
      AND ThoiDiemSuDung < @thang_sau

    UNION ALL

    -- 3. Tien ve thang cua cac xe co hieu luc trong thang.
    SELECT
        MaSV,
        'XeThang',
        DonGiaThangApDung
    FROM DANGKY_XE_THANG
    WHERE NgayBatDau < @thang_sau
      AND (
          NgayKetThuc IS NULL
          OR NgayKetThuc >= @dau_thang
      )

    UNION ALL

    -- 4. Phi gui/lay xe phat sinh.
    SELECT
        d.MaSV,
        'XePhatSinh',
        l.PhiPhatSinh
    FROM LUOT_RA_VAO_XE l
    JOIN DANGKY_XE_THANG d ON d.MaDKXe = l.MaDKXe
    WHERE l.ThoiDiem >= @dau_thang
      AND l.ThoiDiem < @thang_sau
      AND l.PhiPhatSinh > 0
),
tong_theo_sv AS (
    SELECT
        MaSV,
        SUM(CASE WHEN LoaiPhi = 'Phong'
                 THEN ThanhTien ELSE 0 END) AS TienPhong,
        SUM(CASE WHEN LoaiPhi = 'DichVu'
                 THEN ThanhTien ELSE 0 END) AS TienDichVu,
        SUM(CASE WHEN LoaiPhi = 'XeThang'
                 THEN ThanhTien ELSE 0 END) AS TienVeXe,
        SUM(CASE WHEN LoaiPhi = 'XePhatSinh'
                 THEN ThanhTien ELSE 0 END) AS PhiXePhatSinh,
        SUM(ThanhTien) AS TongPhaiTra
    FROM cac_khoan
    GROUP BY MaSV
)
SELECT
    s.MaSV,
    s.HoTen,
    s.SoCMT,
    s.NgaySinh,
    s.Lop,
    s.QueQuan,
    @thang AS Thang,
    @nam AS Nam,
    t.TienPhong,
    t.TienDichVu,
    t.TienVeXe,
    t.PhiXePhatSinh,
    t.TongPhaiTra
FROM SINHVIEN s
JOIN tong_theo_sv t ON t.MaSV = s.MaSV
WHERE @ma_sv IS NULL
   OR s.MaSV = CONVERT(@ma_sv USING utf8mb4) COLLATE utf8mb4_unicode_ci
ORDER BY s.MaSV;

-- =========================================================
-- TRUY VAN 2: TIEN TUNG DICH VU CUA MOI SINH VIEN
-- TRONG KHOANG TU NGAY DEN NGAY
-- =========================================================

SET @tu_ngay = DATE_SUB(CURDATE(), INTERVAL 30 DAY);
SET @den_ngay = CURDATE();

SELECT
    s.MaSV,
    s.HoTen,
    s.Lop,
    v.MaDV,
    v.TenDV,
    v.DonViTinh,
    SUM(u.SoLuong) AS TongSoLuong,
    SUM(u.SoLuong * u.DonGiaApDung) AS TongTien
FROM SUDUNG_DV u
JOIN SINHVIEN s ON s.MaSV = u.MaSV
JOIN DICHVU v ON v.MaDV = u.MaDV
WHERE u.ThoiDiemSuDung >= @tu_ngay
  AND u.ThoiDiemSuDung < DATE_ADD(@den_ngay, INTERVAL 1 DAY)
GROUP BY
    s.MaSV, s.HoTen, s.Lop,
    v.MaDV, v.TenDV, v.DonViTinh
ORDER BY s.MaSV, v.MaDV;

-- =========================================================
-- TRUY VAN 3: SINH VIEN, KHACH THAM VA SO LAN DEN THAM
-- =========================================================

-- Chon 'tuan' hoac 'thang'.
SET @ky_tham = _utf8mb4'thang' COLLATE utf8mb4_unicode_ci;

-- Ngay bat ky nam trong tuan/thang can xem.
SET @ngay_moc = CURDATE();

SET @tu_tham = CASE
    WHEN @ky_tham = 'tuan'
        THEN DATE_SUB(
            @ngay_moc,
            INTERVAL WEEKDAY(@ngay_moc) DAY
        )
    ELSE CAST(DATE_FORMAT(@ngay_moc, '%Y-%m-01') AS DATE)
END;

-- Moc ket thuc khong duoc tinh vao khoang.
SET @den_tham = CASE
    WHEN @ky_tham = 'tuan'
        THEN DATE_ADD(@tu_tham, INTERVAL 7 DAY)
    ELSE DATE_ADD(@tu_tham, INTERVAL 1 MONTH)
END;

SELECT
    s.MaSV,
    s.HoTen AS HoTenSinhVien,
    s.Lop,
    k.CMTKhach,
    k.HoTen AS HoTenKhach,
    k.NgaySinh AS NgaySinhKhach,
    k.SDT AS SDTKhach,
    COUNT(*) AS SoLanDenTham,
    MAX(l.ThoiDiemDen) AS LanDenGanNhat
FROM LUOT_THAM l
JOIN SINHVIEN s ON s.MaSV = l.MaSV
JOIN KHACH k ON k.CMTKhach = l.CMTKhach
WHERE l.ThoiDiemDen >= @tu_tham
  AND l.ThoiDiemDen < @den_tham
GROUP BY
    s.MaSV, s.HoTen, s.Lop,
    k.CMTKhach, k.HoTen, k.NgaySinh, k.SDT
ORDER BY s.MaSV, SoLanDenTham DESC, k.CMTKhach;

-- =========================================================
-- TRUY VAN 4: DOANH THU TUNG DICH VU THEO 12 THANG
-- =========================================================

SET @nam_doanh_thu = YEAR(CURDATE());
SET @dau_nam = MAKEDATE(@nam_doanh_thu, 1);
SET @nam_sau = DATE_ADD(@dau_nam, INTERVAL 1 YEAR);

WITH RECURSIVE cac_thang AS (
    SELECT 1 AS Thang

    UNION ALL

    SELECT Thang + 1
    FROM cac_thang
    WHERE Thang < 12
),
doanh_thu AS (
    SELECT
        MaDV,
        MONTH(ThoiDiemSuDung) AS Thang,
        SUM(SoLuong * DonGiaApDung) AS TongTien
    FROM SUDUNG_DV
    WHERE ThoiDiemSuDung >= @dau_nam
      AND ThoiDiemSuDung < @nam_sau
    GROUP BY MaDV, MONTH(ThoiDiemSuDung)
)
SELECT
    v.MaDV,
    v.TenDV,
    v.DonViTinh,
    @nam_doanh_thu AS Nam,
    t.Thang,
    COALESCE(d.TongTien, 0) AS DoanhThu
FROM DICHVU v
CROSS JOIN cac_thang t
LEFT JOIN doanh_thu d
    ON d.MaDV = v.MaDV
   AND d.Thang = t.Thang
ORDER BY v.MaDV, t.Thang;
