import tkinter as tk
import random
import qrcode
from PIL import Image, ImageTk

# 設定畫布大小
WIDTH, HEIGHT = 300, 200
TICKET_COST = 50  # 每張刮刮樂價格
BRUSH_SIZE = 15  # 刮刮大小
LUCKY_MODE_THRESHOLD = 20  # 每 20 次保底 5000+

# **使用者財務數據**
total_money = 1000  # 初始金額
total_spent = 0  # 花費金額
total_earned = 0  # 總獎金
total_tickets = 0  # 總共刮了幾次
scratched_area = 0  # 刮開的區域大小
max_win = 0  # 最高中獎金額
win_history = []  # 中獎紀錄（最多 3 筆）
prize_text = "0"

# **獎品與機率**
prizes = (
    ["0"] * 55000 +
    ["100"] * 18000 +
    ["500"] * 12000 +
    ["1000"] * 8000 +
    ["5000"] * 5000 +
    ["10000"] * 1500 +
    ["50000"] * 400 +
    ["100000"] * 100 +
    ["500000"] * 20 +
    ["1000000"] * 1
)

weights = [55] * 55000 + [18] * 18000 + [12] * 12000 + [8] * 8000 + [5] * 5000 + [1.5] * 1500 + [0.4] * 400 + [0.1] * 100 + [0.02] * 20 + [0.0001] * 1


# 隨機選擇獎品，並觸發幸運模式
def generate_prize():
    global total_tickets
    if total_tickets > 0 and total_tickets % LUCKY_MODE_THRESHOLD == 0:
        return "5000"
    return random.choices(prizes, weights)[0]


# 產生 QR Code，避免提前知道獎金
def generate_qr_code(hidden=True):
    if hidden:
        qr_text = "請刮開查看結果"
    else:
        qr_text = f"恭喜中獎 {prize_text} 元！"
    
    qr = qrcode.make(qr_text)
    qr = qr.resize((100, 100))
    return ImageTk.PhotoImage(qr)


# 更新介面數據
def update_labels():
    global total_money, total_spent, total_earned, total_tickets, max_win, win_history
    roi = ((total_earned - total_spent) / total_spent * 100) if total_spent > 0 else 0
    money_label.config(text=f"💰 剩餘金額: ${total_money}")
    spent_label.config(text=f"🎟️ 投入金額: ${total_spent}")
    earned_label.config(text=f"🤑 總獎金: ${total_earned}")
    roi_label.config(text=f"📈 投資報酬率: {roi:.2f}%")
    profit_label.config(text=f"💹 總利潤: ${total_earned - total_spent}")
    ticket_label.config(text=f"🕹️ 刮了 {total_tickets} 次")
    max_win_label.config(text=f"🏆 最高中獎: ${max_win}")
    history_label.config(text=f"📜 歷史: {', '.join(win_history[-3:])}")


# 購買刮刮樂，隱藏獎金直到刮開
def buy_ticket(vip_mode=False):
    global total_money, total_spent, total_tickets, prize_text, mask_positions, total_earned, scratched_area, max_win
    ticket_count = 10 if vip_mode else 1
    total_cost = TICKET_COST * ticket_count

    if total_money < total_cost:
        result_label.config(text="❌ 錢不夠了！")
        return

    for _ in range(ticket_count):
        total_money -= TICKET_COST
        total_spent += TICKET_COST
        total_tickets += 1
        prize_text = generate_prize()
        scratched_area = 0  # 重設刮開區域
        mask_positions = []
        draw_scratch_card()
        update_labels()

    # 更新 QR Code，但先隱藏結果
    qr_code = generate_qr_code(hidden=True)
    qr_img_label.config(image=qr_code)
    qr_img_label.image = qr_code


# 重新繪製刮刮樂 UI，購買時完全覆蓋
def draw_scratch_card():
    canvas.delete("all")
    result_label.config(text="🎟️ 請刮開查看結果")
    canvas.create_text(WIDTH // 2, 120, text=prize_text, font=("Courier", 20, "bold"), fill="black", tags="prize")

    for x in range(0, WIDTH, 15):
        for y in range(0, HEIGHT, 15):
            mask = canvas.create_rectangle(x, y, x + 15, y + 15, fill="gray", outline="black", tags="mask")
            mask_positions.append(mask)


# 刮開指定區域，刮滿 80% 才顯示獎金
def scratch(event):
    global scratched_area, total_earned, prize_text, mask_positions, prize_shown
    if scratched_area == 0:
        prize_shown = False  # 重設獎品顯示標誌

    # 遍歷所有 mask 來刮開區域
    for mask in mask_positions[:]:
        coords = canvas.coords(mask)
        if coords is None:
            continue
        x1, y1, x2, y2 = coords
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            canvas.delete(mask)
            mask_positions.remove(mask)
            scratched_area += 1  # 更新刮開的區域數量

    # 刮開超過 10% 時顯示獎品
    if scratched_area >= len(mask_positions) * 0.1 and not prize_shown:
        canvas.delete("prize")
        canvas.create_text(WIDTH // 2, 120, text=prize_text, font=("Courier", 20, "bold"), fill="black", tags="prize")
        result_label.config(text=f"🎉 這次獲得: ${prize_text}")
        total_earned += int(prize_text)  # 更新總獎金
        prize_shown = True  # 確保獎品顯示一次
        update_labels()

        # 更新 QR Code
        qr_code = generate_qr_code(hidden=False)
        qr_img_label.config(image=qr_code)
        qr_img_label.image = qr_code


# 增加信用卡金額
def add_credit(amount):
    global total_money
    total_money += amount
    update_labels()


# 生成購買紀錄收據
def generate_receipt():
    receipt_text = (
        f"--- 刮刮樂購買紀錄 ---\n"
        f"總共刮了: {total_tickets} 次\n"
        f"投入金額: ${total_spent}\n"
        f"總獎金: ${total_earned}\n"
        f"最高中獎: ${max_win}\n"
        f"歷史紀錄: {', '.join(win_history[-3:])}\n"
        f"剩餘金額: ${total_money}\n"
        f"投資報酬率: {((total_earned - total_spent) / total_spent * 100) if total_spent > 0 else 0:.2f}%\n"
        f"總利潤: ${total_earned - total_spent}\n"
    )
    with open("receipt.txt", "w", encoding="utf-8") as file:
        file.write(receipt_text)
    result_label.config(text="🧾 收據已生成！")


# GUI 設計
root = tk.Tk()
root.title("刮刮樂 Plus")
root.geometry("400x700")
root.resizable(False, False)
root.configure(bg="lightgray")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white", relief="sunken", bd=3)
canvas.pack()
canvas.bind("<B1-Motion>", scratch)

# 介面標籤 & 按鈕
buy_button = tk.Button(root, text="🛒 單張 ($50)", command=buy_ticket, font=("Courier", 12), bg="lightgray", relief="ridge", bd=3)
buy_button.pack(pady=5)

credit_button = tk.Button(root, text="💳 加值 ($100)", command=lambda: add_credit(100), font=("Courier", 12), bg="lightgray", relief="ridge", bd=3)
credit_button.pack(pady=5)

receipt_button = tk.Button(root, text="🧾 生成收據", command=generate_receipt, font=("MS Sans Serif", 12), bg="#C0C0C0", relief="ridge", bd=3, width=20)
receipt_button.pack(pady=10)

# Other Labels
max_win_label = tk.Label(root, text="🏆 最高中獎: $0", font=("Courier", 12), bg="lightgray", relief="sunken", bd=2)
max_win_label.pack()

history_label = tk.Label(root, text="📜 歷史: ", font=("Courier", 12), bg="lightgray", relief="sunken", bd=2)
history_label.pack()

money_label = tk.Label(root, text="剩餘金額: $1000", font=("Courier", 12, "bold"), bg="lightgray", relief="sunken", bd=2)
money_label.pack()

result_label = tk.Label(root, text="請購買刮刮樂", font=("Courier", 12), fg="blue", bg="lightgray", relief="sunken", bd=2)
result_label.pack()

spent_label = tk.Label(root, text="投入金額: $0", font=("Courier", 12), bg="lightgray", relief="sunken", bd=2)
spent_label.pack()

earned_label = tk.Label(root, text="總獎金: $0", font=("Courier", 12), bg="lightgray", relief="sunken", bd=2)
earned_label.pack()

roi_label = tk.Label(root, text="投資報酬率: 0.00%", font=("Courier", 12), bg="lightgray", relief="sunken", bd=2)
roi_label.pack()

profit_label = tk.Label(root, text="總利潤: $0", font=("Courier", 12), bg="lightgray", relief="sunken", bd=2)
profit_label.pack()

ticket_label = tk.Label(root, text="刮了 0 次", font=("Courier", 12), bg="lightgray", relief="sunken", bd=2)
ticket_label.pack()

qr_img_label = tk.Label(root, bg="lightgray")
qr_img_label.pack()

mask_positions = []
draw_scratch_card()
update_labels()

root.mainloop()
