/* Sắp xếp cột bảng (9) và chế độ sáng/tối (10).
   Áp dụng tự động cho mọi bảng có class "bang". Tắt cho một bảng: data-khong="1". */
(function () {
    "use strict";

    // Đổi chữ trong ô bảng thành giá trị để so sánh (ngày, tiền, số, chữ)
    function giaTri(chu) {
        var s = chu.replace(/\s+/g, " ").trim();
        var m = s.match(/^(?:(\d{2}):(\d{2})(?::(\d{2}))?\s+)?(\d{2})\/(\d{2})\/(\d{4})$/);   // 09:30 21/10/2026
        if (m) { return Number(m[6] + m[5] + m[4] + (m[1] || "00") + (m[2] || "00") + (m[3] || "00")); }
        m = s.match(/^(\d[\d.]*)\s*(?:đ|lần|lượt|kg|suất)?$/);                                 // 500.000đ, 12, 2 lần
        if (m) { return parseInt(m[1].replace(/\./g, ""), 10); }
        return s.toLowerCase();
    }

    function soSanh(a, b) {
        var soA = typeof a === "number", soB = typeof b === "number";
        if (soA && soB) { return a - b; }
        if (soA) { return -1; }
        if (soB) { return 1; }
        return a.localeCompare(b, "vi");
    }

    function sapXepBang(bang) {
        var tbody = bang.tBodies[0];
        if (!tbody || !bang.tHead || bang.dataset.khong === "1") { return; }
        var soHang = Array.from(tbody.rows).filter(function (r) { return !r.querySelector("td.trong"); }).length;
        if (soHang < 2) { return; }
        var tieuDe = Array.from(bang.tHead.rows[0].cells);
        var cot = -1, huong = 1;
        tieuDe.forEach(function (th) {
            if (!th.textContent.trim()) { return; }
            th.classList.add("sx");
            th.addEventListener("click", function () {
                huong = cot === th.cellIndex ? -huong : 1;
                cot = th.cellIndex;
                tieuDe.forEach(function (o) { o.classList.remove("sx-tang", "sx-giam"); });
                th.classList.add(huong === 1 ? "sx-tang" : "sx-giam");
                var hang = Array.from(tbody.rows).filter(function (r) { return !r.querySelector("td.trong"); });
                function khoa(r) { 
                    var c = r.cells[cot];
                    if (!c) return giaTri("");
                    
                    // 1. Chỉ lấy chữ trong thẻ chứa tên chính (bỏ qua các mã SV, lớp ở thẻ span phụ bên dưới)
                    var theTen = c.querySelector(".fw-semibold");
                    var chu = theTen ? theTen.textContent.trim() : c.textContent;
                    
                    // 2. Đảo chữ cuối (Tên) lên đầu để so sánh (VD: "Trần Thị Bình" -> "Bình Trần Thị")
                    if (theTen) {
                        var mang = chu.split(/\s+/);
                        if (mang.length > 1) {
                            chu = mang.pop() + " " + mang.join(" ");
                        }
                    }
                    
                    return giaTri(chu);
                }
                hang.sort(function (a, b) { return huong * soSanh(khoa(a), khoa(b)); });
                hang.forEach(function (r) { tbody.appendChild(r); });
            });
        });
    }

    function khoiTao() {
        document.querySelectorAll("table.bang").forEach(sapXepBang);

        var nut = document.querySelectorAll("[data-chuyen-giao-dien]");
        function capNhatNut() {
            var toi = document.documentElement.getAttribute("data-bs-theme") === "dark";
            nut.forEach(function (n) {
                n.querySelector("i").className = toi ? "bi bi-sun" : "bi bi-moon-stars";
                n.querySelector("span").textContent = toi ? "Chế độ sáng" : "Chế độ tối";
            });
        }
        nut.forEach(function (n) {
            n.addEventListener("click", function () {
                var moi = document.documentElement.getAttribute("data-bs-theme") === "dark" ? "light" : "dark";
                document.documentElement.setAttribute("data-bs-theme", moi);
                try { localStorage.setItem("ktx-giao-dien", moi); } catch (e) { /* trình duyệt chặn lưu trữ */ }
                capNhatNut();
            });
        });
        capNhatNut();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", khoiTao);
    } else {
        khoiTao();
    }
})();