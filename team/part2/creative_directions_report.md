# Phần 2 (Nâng Cao) — Phân Tích Vận Hành & Chiến Lược Cạnh Tranh (Top-Tier Insights)

Để tạo ra sự khác biệt hoàn toàn so với các đội thi khác (những đội thường chỉ tập trung vào phân tích doanh thu theo mùa vụ hoặc nhân khẩu học cơ bản), chúng ta đã khai thác sâu vào **dữ liệu Vận hành (Operations)** và **cấu trúc Sản phẩm (Product Hierarchy)**. 

Bằng cách sử dụng kỹ thuật Regular Expressions (Regex) để bóc tách chuỗi mã sản phẩm và liên kết chéo (cross-join) giữa các bảng `orders`, `shipments`, `products` và `order_items`, chúng ta đã tìm ra **3 Insight ngược đời (Counter-intuitive) nhưng mang lại giá trị chiến lược khổng lồ**.

---

## Direction 1: The "Loss Leader" Trap — Cạm Bẫy Sản Phẩm Phễu
**Thư mục:** `direction1_loss_leaders`

* **Khái niệm:** Doanh nghiệp có một lượng lớn sản phẩm (461 SKUs) được định giá với biên lợi nhuận cực thấp (Margin $\le$ 5.5%). Đây thường là chiến lược "Mồi nhử" (Loss Leader / Bait & Hook) nhằm thu hút khách hàng mua thêm các sản phẩm khác có lời hơn trong cùng một giỏ hàng.
* **Phân tích (Analysis):** 
  * Biểu đồ so sánh giữa *Đơn hàng tiêu chuẩn* và *Đơn hàng chứa sản phẩm phễu*.
  * Đúng như kỳ vọng của chiến lược, đơn hàng có mồi nhử giúp tăng số lượng sản phẩm/giỏ (từ 4.9 lên 5.1 items).
  * **TUY NHIÊN (Key Finding):** Số lượng mua thêm này **KHÔNG ĐỦ** để bù đắp lại khoản lỗ từ sản phẩm mồi nhử. Kết quả là lợi nhuận ròng của toàn bộ giỏ hàng (Basket Profit) bị âm (-1,472 VND/đơn), trong khi đơn tiêu chuẩn lãi gần 4,000 VND/đơn.
* **Ý nghĩa kinh doanh (Prescriptive):** Chiến lược mồi nhử đang thất bại thảm hại và gây "chảy máu" dòng tiền (Operational Bleeding). Cần ngay lập tức:
  1. Loại bỏ các mã sản phẩm có margin $\le$ 5.5%.
  2. Bắt buộc áp dụng `min_order_value` khắt khe hơn khi khách hàng mua các sản phẩm phễu này để ép họ phải mua bù các sản phẩm giá trị cao.

---

## Direction 2: The "Inelastic" Logistics Paradox — Nghịch Lý Giao Hàng
**Thư mục:** `direction2_logistics_churn`

* **Khái niệm:** Trong TMĐT, tốc độ giao hàng (Logistics) thường là yếu tố sống còn quyết định tỷ lệ quay lại (Repurchase Rate). Giao hàng chậm = Mất khách.
* **Phân tích (Analysis):** 
  * Chúng ta tính toán độ trễ giao hàng thực tế (`delivery_date` - `order_date`) của **đơn hàng đầu tiên** của mỗi khách hàng, sau đó tracking xem họ có quay lại mua đơn thứ 2 hay không.
  * **Key Finding (Cực kỳ dị biệt):** Đường xu hướng (Trendline) nằm ngang một cách hoàn hảo ở mức ~74% Repurchase Rate. Khách hàng nhận được đồ sau **2 ngày** hay sau **14 ngày** đều có tỷ lệ quay lại mua hàng giống hệt nhau! Khách hàng của VinUni thể hiện sự trung thành và bao dung (inelastic) cực kỳ lớn đối với thời gian chờ đợi.
* **Ý nghĩa kinh doanh (Prescriptive):** Doanh nghiệp có thể đang **ném tiền qua cửa sổ** nếu đang trả phí cao cho các đối tác vận chuyển (3PL) để ép SLA giao hàng nhanh. 
  * Đề xuất: Chuyển toàn bộ các đơn hàng không khẩn cấp sang các gói vận chuyển giá rẻ nhất (Economy Shipping) chấp nhận giao chậm 7-10 ngày để cắt giảm khổng lồ chi phí vận hành (Shipping Fee) mà không sợ mất khách.

---

## Direction 3: The Power of Iteration — Sức Mạnh Của Việc Lặp Lại R&D
**Thư mục:** `direction3_product_lifecycle`

* **Khái niệm:** Mã sản phẩm của VinUni tuân theo quy tắc `[Brand] [LineCode]-[Suffix]`. Hậu tố Suffix chạy từ `00` đến `99`, thể hiện cho các "Thế hệ" (Generation) hoặc phiên bản lặp lại của sản phẩm (giống như iPhone 11, 12, 13...).
* **Phân tích (Analysis):**
  * Chúng ta phân rã 100 suffix numbers thành 5 thế hệ: Classics (00-10), Early-Mid (11-30), Mid-Gen (31-50), Late-Gen (51-70), và Newest Iterations (71-99).
  * **Key Finding:** Thay vì rơi vào trạng thái "Innovation Fatigue" (Sản phẩm cũ bán chạy, sản phẩm mới ra mắt bị ế), biểu đồ cho thấy một sự tăng trưởng bậc thang hoàn hảo. Các thế hệ sản phẩm mới nhất (71-99) tạo ra **doanh thu trung bình trên mỗi SKU cao hơn 64%** (10 Tỷ VND) so với các mẫu mã nguyên bản (6 Tỷ VND).
* **Ý nghĩa kinh doanh (Prescriptive):** Đây là lời khẳng định đanh thép cho bộ phận R&D và Thiết kế (Design Team). Họ đang đọc vị thị trường cực kỳ xuất sắc. 
  * Đề xuất: Thay vì tiếp tục restock (nhập thêm) các dòng sản phẩm Classic, hãy mạnh dạn clear kho (xả hàng) các mẫu cũ (Suffix < 30) và dồn toàn bộ nguồn vốn (Working Capital) để sản xuất các mẫu mới (Suffix > 70).

---

> **Lưu ý dành cho team:** 3 insight trên là những insight "ăn tiền" nhất vì nó đòi hỏi kỹ năng **Feature Engineering** (Regex Suffix, Tính Basket Profit, Tính Churn Rate theo Order Rank) thay vì chỉ vẽ chart cơ bản bằng hàm `groupby` có sẵn. Hãy ưu tiên thuyết trình 3 chart này để show-off kỹ năng Data Science ứng dụng thực tế.
