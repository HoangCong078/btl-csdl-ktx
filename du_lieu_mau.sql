USE KTX;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE CHITIET_HOADON; TRUNCATE TABLE HOADON; TRUNCATE TABLE LUOT_RA_VAO_XE;
TRUNCATE TABLE DANGKY_XE_THANG; TRUNCATE TABLE XE; TRUNCATE TABLE SUDUNG_DV; TRUNCATE TABLE DICHVU;
TRUNCATE TABLE LUOT_THAM; TRUNCATE TABLE KHACH; TRUNCATE TABLE DANGKY_O;
TRUNCATE TABLE SINHVIEN; TRUNCATE TABLE PHONG;
SET FOREIGN_KEY_CHECKS = 1;

SET @hn = CURDATE();
SET @hq = DATE_SUB(CURDATE(), INTERVAL 1 DAY);

INSERT INTO PHONG VALUES
 ('P101', 'Thường', 500000, 4), ('P102', 'Thường', 500000, 2), ('P201', 'Chất lượng cao', 900000, 2),('V101','Hoàng Gia',5000000,1);

INSERT INTO SINHVIEN (MaSV, HoTen, GioiTinh, SDT, SoCMT, NgaySinh, Lop, QueQuan) VALUES
 ('B24DCCN001', 'Nguyễn Văn An',  'Nam', '0901234567', '001206000001', '2006-03-21', 'B24CQCN01-B', 'Hà Nam'),
 ('B24DCCN002', 'Trần Thị Bình',  'Nữ',  '0912345678', '001206000002', '2006-07-09', 'B24CQCN02-B', 'Nam Định'),
 ('B24DCCN003', 'Lê Văn Cường',   'Nam', '0987654321', '001205000003', '2005-11-30', 'B24CQCN03-B', 'Thanh Hóa'),
 ('B24DCCN004', 'Phạm Thị Dung',  'Nữ',  '0933111222', '001206000004', '2006-01-15', 'B24CQCN01-B', 'Hải Dương'),
 ('B24DCCN005', 'Hoàng Minh Đức', 'Nam', '0944555666', '001206000005', '2006-09-02', 'B24CQCN02-B', 'Nghệ An'),
 ('B24DCCN006', 'Vũ Thị Hà',      'Nữ',  NULL,         '001206000006', '2006-05-27', 'B24CQCN03-B', 'Bắc Ninh'),
 ('B24DCCN007', 'Nguyễn Văn A',   'Nam', NULL,         '000000000001', '2006-01-01', 'B24CQCN03-B', 'Hà Nội'),
 ('B24DCCN008', 'Nguyễn Văn B',   'Nam', NULL,         '000000000002', '2006-01-01', 'B24CQCN03-B', 'Hà Nội'),
 ('B24DCCN009', 'Nguyễn Văn C',   'Nam', NULL,         '000000000003', '2006-01-01', 'B24CQCN03-B', 'Hà Lội');

INSERT INTO DANGKY_O (MaSV, SoPhong, NgayBatDau, NgayKetThuc, DonGiaThangApDung) VALUES
 ('B24DCCN001', 'P101', DATE_SUB(@hn, INTERVAL 60 DAY), NULL, 500000),
 ('B24DCCN003', 'P101', DATE_SUB(@hn, INTERVAL 60 DAY), NULL, 500000),
 ('B24DCCN005', 'P101', DATE_SUB(@hn, INTERVAL 50 DAY), NULL, 500000),
 ('B24DCCN002', 'P102', DATE_SUB(@hn, INTERVAL 60 DAY), NULL, 500000),
 ('B24DCCN004', 'P102', DATE_SUB(@hn, INTERVAL 45 DAY), NULL, 500000),
 ('B24DCCN008', 'V101', DATE_SUB(@hn, INTERVAL 60 DAY), NULL, 5000000);

INSERT INTO KHACH (CMTKhach, HoTen, NgaySinh, SDT) VALUES
 ('038200000001', 'Nguyễn Thị Lan', '1978-05-12', '0903111222'),
 ('038200000002', 'Trần Văn Hùng',  '1980-09-03', '0903333444'),
 ('038200000003', 'Lê Thu Hà',      '2005-02-20', NULL);

INSERT INTO LUOT_THAM (CMTKhach, MaSV, ThoiDiemDen) VALUES
 ('038200000001', 'B24DCCN001', TIMESTAMP(@hn, '09:30:00')),
 ('038200000001', 'B24DCCN001', TIMESTAMP(@hq, '08:15:00')),
 ('038200000002', 'B24DCCN002', TIMESTAMP(DATE_SUB(@hn, INTERVAL 2 DAY), '15:00:00')),
 ('038200000003', 'B24DCCN001', TIMESTAMP(DATE_SUB(@hn, INTERVAL 9 DAY), '18:20:00')),
 ('038200000002', 'B24DCCN002', TIMESTAMP(DATE_SUB(@hn, INTERVAL 40 DAY), '10:00:00')),
 ('038200000001', 'B24DCCN003', TIMESTAMP(@hn, '14:45:00'));

INSERT INTO DICHVU (MaDV, TenDV, LoaiDV, DonGia, DonViTinh) VALUES
 ('DV01', 'Giặt là', 'Giặt là', 15000, 'kg'), ('DV02', 'Ăn uống', 'Ăn uống', 30000, 'suất'),
 ('DV03', 'Trông xe vãng lai', 'Trông xe', 3000, 'lượt'), ('DV04', 'Cho thuê xe', 'Cho thuê xe', 50000, 'lần');

-- DonGiaApDung để trống: trigger trg_sudung_dv_bi tự lấy từ DICHVU
INSERT INTO SUDUNG_DV (MaSV, MaDV, ThoiDiemSuDung, SoLuong) VALUES
 ('B24DCCN001', 'DV01', TIMESTAMP(DATE_SUB(@hn, INTERVAL 20 DAY), '18:00:00'), 3),
 ('B24DCCN001', 'DV02', TIMESTAMP(DATE_SUB(@hn, INTERVAL 18 DAY), '12:00:00'), 4),
 ('B24DCCN001', 'DV02', TIMESTAMP(DATE_SUB(@hn, INTERVAL 10 DAY), '12:10:00'), 2),
 ('B24DCCN002', 'DV01', TIMESTAMP(DATE_SUB(@hn, INTERVAL 15 DAY), '19:00:00'), 2),
 ('B24DCCN002', 'DV04', TIMESTAMP(DATE_SUB(@hn, INTERVAL 12 DAY), '09:00:00'), 1),
 ('B24DCCN002', 'DV02', TIMESTAMP(DATE_SUB(@hn, INTERVAL 5 DAY),  '18:30:00'), 3),
 ('B24DCCN003', 'DV02', TIMESTAMP(DATE_SUB(@hn, INTERVAL 22 DAY), '12:00:00'), 5),
 ('B24DCCN003', 'DV03', TIMESTAMP(DATE_SUB(@hn, INTERVAL 3 DAY),  '07:30:00'), 2),
 ('B24DCCN003', 'DV01', TIMESTAMP(DATE_SUB(@hn, INTERVAL 45 DAY), '20:00:00'), 4),
 ('B24DCCN001', 'DV04', TIMESTAMP(@hq, '15:00:00'), 2),
 ('B24DCCN004', 'DV02', TIMESTAMP(@hn, '12:00:00'), 1),
 ('B24DCCN005', 'DV01', TIMESTAMP(DATE_SUB(@hn, INTERVAL 2 DAY), '19:30:00'), 2);

INSERT INTO XE (BienSo, LoaiXe) VALUES
 ('29A1-12345', 'Xe máy'), ('29B2-67890', 'Xe máy'), ('XD-B24DCCN001', 'Xe đạp'), ('29MD-11111', 'Xe điện');

-- NgayKetThuc NULL = vé còn hiệu lực. B24DCCN001 đủ 2 xe; vé 29MD-11111 của B24DCCN003 đã hủy.
INSERT INTO DANGKY_XE_THANG (MaSV, BienSo, NgayBatDau, NgayKetThuc, DonGiaThangApDung) VALUES
 ('B24DCCN001', '29A1-12345',    DATE_SUB(@hn, INTERVAL 40 DAY), NULL, 100000),
 ('B24DCCN001', 'XD-B24DCCN001', DATE_SUB(@hn, INTERVAL 40 DAY), NULL, 100000),
 ('B24DCCN002', '29B2-67890',    DATE_SUB(@hn, INTERVAL 30 DAY), NULL, 100000),
 ('B24DCCN003', '29MD-11111',    DATE_SUB(@hn, INTERVAL 45 DAY), DATE_SUB(@hn, INTERVAL 30 DAY), 100000);

-- PhiPhatSinh do trigger tự tính: hôm qua xe 29A1-12345 có lượt 3 và 4 mất 3.000đ; hôm nay đã 2 lượt
INSERT INTO LUOT_RA_VAO_XE (MaDKXe, ThoiDiem, LoaiHanhDong) VALUES
 (1, TIMESTAMP(@hq, '06:50:00'), 'Gui'), (1, TIMESTAMP(@hq, '07:30:00'), 'Lay'),
 (1, TIMESTAMP(@hq, '12:00:00'), 'Gui'), (1, TIMESTAMP(@hq, '12:30:00'), 'Lay'),
 (2, TIMESTAMP(@hq, '07:05:00'), 'Gui'), (2, TIMESTAMP(@hq, '17:20:00'), 'Lay'),
 (3, TIMESTAMP(@hq, '07:10:00'), 'Gui'), (3, TIMESTAMP(@hq, '17:25:00'), 'Lay'),
 (1, TIMESTAMP(@hn, '06:50:00'), 'Gui'), (1, TIMESTAMP(@hn, '07:30:00'), 'Lay');

-- Ba hóa đơn mẫu của tháng chạy file: An, Bình đã thanh toán; Cường chưa thanh toán.
-- Chỉ lấy các khoản thu thuộc kỳ hóa đơn, kể cả khi chạy vào đầu tháng/đầu năm.
SET @dau_ky_hd = CAST(DATE_FORMAT(@hn, '%Y-%m-01') AS DATE);
SET @cuoi_ky_hd = LAST_DAY(@hn);

START TRANSACTION;

INSERT INTO HOADON (MaSV, Thang, Nam, TrangThai) VALUES
 ('B24DCCN001', MONTH(@hn), YEAR(@hn), 'DaThanhToan'),
 ('B24DCCN002', MONTH(@hn), YEAR(@hn), 'DaThanhToan'),
 ('B24DCCN003', MONTH(@hn), YEAR(@hn), 'ChuaThanhToan');

DROP TEMPORARY TABLE IF EXISTS tmp_hoadon_mau;

CREATE TEMPORARY TABLE tmp_hoadon_mau AS
SELECT MaHD, MaSV, Thang, Nam
FROM HOADON
WHERE Thang = MONTH(@hn) AND Nam = YEAR(@hn);

-- DonGiaApDung truyền 0 làm giá trị ban đầu; trigger trg_cthd_bi lấy lại giá
-- và số lượng từ nguồn, tính ThanhTien; trigger trg_cthd_ai cộng vào TongTien.
-- Tiền phòng: tính đủ một tháng cho mỗi đăng ký ở giao với kỳ hóa đơn.
INSERT INTO CHITIET_HOADON (MaHD, LoaiPhi, DienGiai, SoLuong, DonGiaApDung, MaDKO)
SELECT h.MaHD, 'Phong', CONCAT('Tiền phòng ', d.SoPhong, ' (tính chẵn tháng)'),
       1, 0, d.MaDKO
FROM tmp_hoadon_mau h
JOIN DANGKY_O d ON d.MaSV = h.MaSV
WHERE h.Thang = MONTH(@hn) AND h.Nam = YEAR(@hn)
  AND d.NgayBatDau <= @cuoi_ky_hd
  AND COALESCE(d.NgayKetThuc, '9999-12-31') >= @dau_ky_hd;

-- Dịch vụ: mỗi lượt sử dụng trong tháng là một dòng chi tiết có MaSuDung.
INSERT INTO CHITIET_HOADON (MaHD, LoaiPhi, DienGiai, SoLuong, DonGiaApDung, MaSuDung)
SELECT h.MaHD, 'DichVu', CONCAT('Dịch vụ ', v.TenDV), 1, 0, u.MaSuDung
FROM tmp_hoadon_mau h
JOIN SUDUNG_DV u ON u.MaSV = h.MaSV
JOIN DICHVU v ON v.MaDV = u.MaDV
WHERE h.Thang = MONTH(@hn) AND h.Nam = YEAR(@hn)
  AND u.ThoiDiemSuDung >= @dau_ky_hd
  AND u.ThoiDiemSuDung < @cuoi_ky_hd + INTERVAL 1 DAY;

-- Vé tháng: đúng một dòng/hóa đơn; trigger tự cộng giá của tất cả vé trong kỳ.
INSERT INTO CHITIET_HOADON (MaHD, LoaiPhi, DienGiai, SoLuong, DonGiaApDung)
SELECT h.MaHD, 'XeThang', 'Phí vé tháng xe (gộp tất cả xe)', 1, 0
FROM tmp_hoadon_mau h
WHERE h.Thang = MONTH(@hn) AND h.Nam = YEAR(@hn)
  AND EXISTS (
      SELECT 1 FROM DANGKY_XE_THANG d
      WHERE d.MaSV = h.MaSV
        AND d.NgayBatDau <= @cuoi_ky_hd
        AND COALESCE(d.NgayKetThuc, '9999-12-31') >= @dau_ky_hd
  );

-- Phí xe phát sinh: chỉ lấy lượt có phí 3.000đ và thuộc tháng hóa đơn.
INSERT INTO CHITIET_HOADON (MaHD, LoaiPhi, DienGiai, SoLuong, DonGiaApDung, MaLuot)
SELECT h.MaHD, 'XePhatSinh', 'Phí gửi/lấy xe phát sinh', 1, 0, l.MaLuot
FROM tmp_hoadon_mau h
JOIN DANGKY_XE_THANG d ON d.MaSV = h.MaSV
JOIN LUOT_RA_VAO_XE l ON l.MaDKXe = d.MaDKXe
WHERE h.Thang = MONTH(@hn) AND h.Nam = YEAR(@hn)
  AND l.PhiPhatSinh = 3000
  AND l.ThoiDiem >= @dau_ky_hd
  AND l.ThoiDiem < @cuoi_ky_hd + INTERVAL 1 DAY;

COMMIT;
