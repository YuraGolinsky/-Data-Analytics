import tkinter as tk
import webbrowser
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import csv
from collections import defaultdict
from datetime import datetime


# Функції для завантаження даних
def load_data():
    events, products, countries = [], [], []

    try:
        with open('C:/Users/werty/OneDrive/Рабочий стол/13. Final project/events.csv', mode='r') as file:
            reader = csv.DictReader(file)
            events.extend(row for row in reader)
    except FileNotFoundError:
        print("Файл events.csv не найден.")

    try:
        with open('C:/Users/werty/OneDrive/Рабочий стол/13. Final project/products.csv', mode='r') as file:
            reader = csv.DictReader(file)
            products.extend(row for row in reader)
    except FileNotFoundError:
        print("Файл products.csv не найден.")

    try:
        with open('C:/Users/werty/OneDrive/Рабочий стол/13. Final project/countries.csv', mode='r') as file:
            reader = csv.DictReader(file)
            countries.extend(row for row in reader)
    except FileNotFoundError:
        print("Файл countries.csv не найден.")

    return events, products, countries

# Функція для інспекції даних
def inspect_data(events, products):
    print("Events Data Sample:")
    for row in events[:5]:  # Show sample of first 5 rows
        print(row)

    print("\nProducts Data Sample:")
    for row in products[:5]:
        print(row)

# Підсумкові дані
def data_summary(events, products):
    print(f"Total Events: {len(events)}")
    print(f"Total Products: {len(products)}")
    print(f"Sample Event Keys: {list(events[0].keys()) if events else 'No data'}")
    print(f"Sample Product Keys: {list(products[0].keys()) if products else 'No data'}")


# Функція для очищення даних
def clean_data(events, products):
    for event in events:
        event['Units Sold'] = event['Units Sold'].replace(',', '')  # Remove commas
        try:
            float(event['Units Sold'])  # Ensure it's a valid number
        except ValueError:
            event['Units Sold'] = '0'  # Replace invalid values with '0'

    # Clean products (example: ensure all product IDs are valid)
    valid_product_ids = set(product['id'] for product in products)
    for event in events:
        if event['Product ID'] not in valid_product_ids:
            event['Product ID'] = 'Unknown'


# Функція для проведення EDA
def perform_eda(events, products):
    total_units_sold = sum(
        float(event['Units Sold']) for event in events if event['Units Sold'].replace('.', '', 1).isdigit())
    print(f"Total Units Sold: {total_units_sold}")

    product_sales = defaultdict(float)
    for event in events:
        product_sales[event['Product ID']] += float(event['Units Sold'])

    avg_units_per_product = sum(product_sales.values()) / len(product_sales) if product_sales else 0
    print(f"Average Units Sold per Product: {avg_units_per_product:.2f}")


# Функція для проведення ABC аналізу

# Функція для проведення ABC аналізу
def perform_abc_analysis(events, products):
    product_sales = defaultdict(lambda: {'units': 0, 'revenue': 0, 'profit': 0})

    for event in events:
        try:
            units_sold = float(event['Units Sold']) if event['Units Sold'] else 0.0
            unit_price = float(event['Unit Price']) if event['Unit Price'] else 0.0
            unit_cost = float(event['Unit Cost']) if event['Unit Cost'] else 0.0
        except ValueError as e:
            print(f"Error converting values: {e}")
            continue

        product_id = event['Product ID']
        product_sales[product_id]['units'] += units_sold
        product_sales[product_id]['revenue'] += units_sold * unit_price
        product_sales[product_id]['profit'] += units_sold * (unit_price - unit_cost)

    sorted_products = sorted(product_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)

    total_revenue = sum(p[1]['revenue'] for p in sorted_products)
    cumulative_revenue = 0
    abc_categories = {'A': [], 'B': [], 'C': []}

    for product_id, data in sorted_products:
        cumulative_revenue += data['revenue']
        percentage = cumulative_revenue / total_revenue * 100
        if percentage <= 80:
            abc_categories['A'].append(product_id)
        elif percentage <= 95:
            abc_categories['B'].append(product_id)
        else:
            abc_categories['C'].append(product_id)

    print("\nABC Analysis Results:")
    for category, products in abc_categories.items():
        print(f"Category {category}: {len(products)} products")

    return {category: len(products) for category, products in abc_categories.items()}


# Функція для відображення графіка ABC аналізу
def draw_bar_chart(canvas, abc_sales):
    categories = ['A', 'B', 'C']
    values = [abc_sales.get(cat, 0) for cat in categories]

    # Очищення канваса перед відображенням нового графіка
    canvas.delete("all")

    # Налаштування
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    bar_width = width // (len(categories) * 2)
    max_value = max(values) if values else 1

    for i, value in enumerate(values):
        x0 = (i * 2 + 1) * bar_width
        y0 = height - (value / max_value) * (height - 20)
        x1 = x0 + bar_width
        y1 = height - 20

        canvas.create_rectangle(x0, y0, x1, y1, fill='#66b3ff')
        canvas.create_text((x0 + x1) // 2, y0 - 10, text=str(value), fill='black')
        canvas.create_text((x0 + x1) // 2, height - 10, text=categories[i], fill='black')


# Функція для обробки натискання кнопки
def on_click_show_abc_chart():
    abc_sales = perform_abc_analysis(events, products)
    draw_bar_chart(graph_canvas, abc_sales)


# Функції для відображення/очищення зведеної інформації
def toggle_summary(events, countries):
    global summary_label
    if state["summary_displayed"]:
        summary_label.config(text="")
    else:
        total_orders = len(set(row['Order ID'] for row in events))
        total_profit = sum(
            float(row['Units Sold']) * (float(row['Unit Price']) - float(row['Unit Cost']))
            for row in events if row['Units Sold'].replace('.', '', 1).isdigit()
        )
        total_countries = len(set(row['name'] for row in countries))

        summary = (
            f"Загальна кількість замовлень: {total_orders}\n"
            f"Загальний прибуток: ${total_profit:.2f}\n"
            f"Загальна кількість охоплених країн: {total_countries}"
        )
        summary_label.config(text=summary)

    state["summary_displayed"] = not state["summary_displayed"]

# Продажі за категоріями
def toggle_sales_by_category(events, products):
    global sales_text_label
    if state["sales_displayed"]:
        sales_text_label.config(text="")
    else:
        category_sales = defaultdict(float)
        product_map = {product['id']: product['item_type'] for product in products}

        for event in events:
            try:
                product_id = event['Product ID']
                units_sold = float(event['Units Sold'])
                category = product_map.get(product_id, 'Unknown')
                category_sales[category] += units_sold
            except ValueError:
                pass

        sales_text = "Продажі по категоріях:\n"
        sales_text += '\n'.join(f"{category}: {sales} одиниць" for category, sales in category_sales.items())
        sales_text_label.config(text=sales_text)

    state["sales_displayed"] = not state["sales_displayed"]

# Сетка
def draw_grid(canvas, width, height):
    margin = 40
    step = 50

    for x in range(margin, width - margin, step):
        canvas.create_line(x, margin, x, height - margin, fill="lightgray", dash=(2, 4))

    for y in range(margin, height - margin, step):
        canvas.create_line(margin, y, width - margin, y, fill="lightgray", dash=(2, 4))

# Графік
def draw_bar_chart(canvas, data):
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    draw_grid(canvas, width, height)
    margin = 40
    bar_width = (width - 2 * margin) / len(data)

    max_value = max(data.values(), default=1)

    for i, (key, value) in enumerate(data.items()):
        x1 = margin + i * bar_width
        y1 = height - margin
        x2 = x1 + bar_width - 10
        y2 = height - margin - (value / max_value * (height - 2 * margin))
        canvas.create_rectangle(x1, y1, x2, y2, fill="skyblue", outline="blue")
        canvas.create_text((x1 + x2) / 2, y1 + 10, text=key, angle=45, font=("Helvetica", 10), fill="black")

# Лінійний графік
def draw_line_chart(canvas, data):
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    draw_grid(canvas, width, height)
    margin = 40

    max_value = max(data.values(), default=1)
    prev_x, prev_y = None, None

    for i, (key, value) in enumerate(sorted(data.items())):
        x = margin + i * (width - 2 * margin) / (len(data) - 1)
        y = height - margin - (value / max_value * (height - 2 * margin))
        if prev_x is not None:
            canvas.create_line(prev_x, prev_y, x, y, fill="red", width=2)
        prev_x, prev_y = x, y
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red", outline="black")

    if prev_x is not None:
        canvas.create_text(prev_x, prev_y - 10, text=f"{value:.2f}", font=("Helvetica", 8), fill="black")

# Перемикати графік
def toggle_graph(graph_type, events, products):
    if state["graph_displayed"]:
        graph_canvas.delete("all")
    else:
        product_sales = defaultdict(float)
        for event in events:
            try:
                product_id = event['Product ID']
                units_sold = float(event['Units Sold'])
                product_sales[product_id] += units_sold
            except ValueError:
                pass

        if graph_type == "bar":
            draw_bar_chart(graph_canvas, product_sales)
        elif graph_type == "line":
            draw_line_chart(graph_canvas, product_sales)

    state["graph_displayed"] = not state["graph_displayed"]


# Функція для відображення інформації про програму
def show_about():
    about_window = tk.Toplevel(root)
    about_window.title("About")
    about_window.geometry("300x200")
    # Додати вміст у вікно "Про програму"    about_text = (
    about_text = (
        "Data Analysis\n"
        "Data Science Project\n\n"
        "Yura Golinsky\n\n"
        "Links:\n"
        "Telegram: https://t.me/Yura_Golinsky\n"
        "GitHub: https://github.com/YuraGolinsky"
    )
    about_label = tk.Label(about_window, text=about_text, font=("Helvetica", 12), pady=10, padx=10, justify=tk.LEFT)
    about_label.pack(expand=True, fill=tk.BOTH)

    # Додати кнопку закриття    close_button = tk.Button(about_window, text="Close", command=about_window.destroy)

    close_button = tk.Button(about_window, text="Close", command=about_window.destroy)
    close_button.pack(pady=5)

    # Обробник для відкриття посилань у браузері
    def open_link(url):
        webbrowser.open(url)

    # Додати кнопки для відкриття посилань
    telegram_button = tk.Button(about_window, text="Open Telegram", command=lambda: open_link("https://t.me/Yura_Golinsky"))
    telegram_button.pack(pady=2)

    github_button = tk.Button(about_window, text="Open GitHub", command=lambda: open_link("https://github.com/YuraGolinsky"))
    github_button.pack(pady=2)

# Ініціалізація вікна Tkinter
root = tk.Tk()
root.title("Data Analysis Tool")
# Визначення шляхів та функцій для зміни розмірів зображень
image_paths = {
    "summary": "C:/Users/werty/OneDrive/Рабочий стол/13. Final project/pythonProject/imageslogo/information.png",
    "sales": "C:/Users/werty/OneDrive/Рабочий стол/13. Final project/pythonProject/imageslogo/sales.png",
    "bar": "C:/Users/werty/OneDrive/Рабочий стол/13. Final project/pythonProject/imageslogo/histogram.png",
    "line": "C:/Users/werty/OneDrive/Рабочий стол/13. Final project/pythonProject/imageslogo/line-graph.png",
    "about": "C:/Users/werty/OneDrive/Рабочий стол/13. Final project/pythonProject/imageslogo/developer.png",
    "day_of_week": "C:/Users/werty/OneDrive/Рабочий стол/13. Final project/pythonProject/imageslogo/Sales_by_Day.png",

    "time": "C:/Users/werty/OneDrive/Рабочий стол/13. Final project/pythonProject/imageslogo/time.png",
    "profit_vs_delay": "C:/Users/werty/OneDrive/Рабочий стол/13. Final project/pythonProject/imageslogo/profit_vs_delay.png",
    "week": "C:/Users/werty/OneDrive/Рабочий стол/13. Final project/pythonProject/imageslogo/week.png",

   "ABC_Chart":"C:/Users/werty/OneDrive/Рабочий стол/13. Final project/pythonProject/imageslogo/ABC_Chart.png"

}# Доданий шлях






# Зміна розміру зображень
def analyze_shipping_delay(events):
    shipping_delays = defaultdict(list)
    for event in events:
        try:
            order_date = datetime.strptime(event['Order Date'], '%m/%d/%Y')
            ship_date = datetime.strptime(event['Ship Date'], '%m/%d/%Y')
            delay = (ship_date - order_date).days
            category = event['Category']
            shipping_delays[category].append(delay)
        except (ValueError, KeyError):
            continue
    return shipping_delays
# Намалюйте діаграму затримки доставки
def draw_shipping_delay_chart(canvas, data):
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    if not data:
        canvas.create_text(width // 2, height // 2, text="No data available", font=("Helvetica", 12), fill="red")
        return

    draw_grid(canvas, width, height)
    margin = 40
    bar_width = (width - 2 * margin) / len(data)

    max_value = max(max(values) for values in data.values()) if data else 1

    for i, (category, delays) in enumerate(data.items()):
        average_delay = sum(delays) / len(delays)
        x1 = margin + i * bar_width
        y1 = height - margin
        x2 = x1 + bar_width - 10
        y2 = height - margin - (average_delay / max_value * (height - 2 * margin))
        canvas.create_rectangle(x1, y1, x2, y2, fill="skyblue", outline="blue")
        canvas.create_text((x1 + x2) / 2, y1 + 10, text=category, angle=45, font=("Helvetica", 10), fill="black")
# Перемкнути графік затримки доставки
def toggle_shipping_delay_graph(events):
    if state.get("shipping_delay_graph_displayed", False):
        graph_canvas.delete("all")
    else:
        delays = analyze_shipping_delay(events)
        draw_shipping_delay_chart(graph_canvas, delays)
    state["shipping_delay_graph_displayed"] = not state.get("shipping_delay_graph_displayed", False)


    #Проаналізуйте затримку доставки прибутку
def analyze_profit_vs_shipping_delay(events):
    delays_profit = defaultdict(lambda: {'delay': 0, 'profit': 0, 'count': 0})
    for event in events:
        try:
            order_date = datetime.strptime(event['Order Date'], '%m/%d/%Y')
            ship_date = datetime.strptime(event['Ship Date'], '%m/%d/%Y')
            delay = (ship_date - order_date).days
            profit = float(event['Units Sold']) * (float(event['Unit Price']) - float(event['Unit Cost']))
            delays_profit[delay]['delay'] += delay
            delays_profit[delay]['profit'] += profit
            delays_profit[delay]['count'] += 1
        except (ValueError, KeyError):
            continue

    profit_by_delay = {delay: data['profit'] / data['count'] if data['count'] else 0 for delay, data in delays_profit.items()}
    return profit_by_delay
# Графік затримки вилучення прибутку
def draw_profit_vs_delay_chart(canvas, data):
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    if not data:
        canvas.create_text(width // 2, height // 2, text="No data available", font=("Helvetica", 12), fill="red")
        return

    draw_grid(canvas, width, height)
    margin = 40

    max_value = max(data.values(), default=1)
    prev_x, prev_y = None, None

    for i, (delay, profit) in enumerate(sorted(data.items())):
        x = margin + i * (width - 2 * margin) / (len(data) - 1)
        y = height - margin - (profit / max_value * (height - 2 * margin))
        if prev_x is not None:
            canvas.create_line(prev_x, prev_y, x, y, fill="red", width=2)
        prev_x, prev_y = x, y
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red", outline="black")

    if prev_x is not None:
        canvas.create_text(prev_x, prev_y - 10, text=f"{profit:.2f}", font=("Helvetica", 8), fill="black")
#Перемикати графік затримки прибутку
def toggle_profit_vs_delay_graph(events):
    if state.get("profit_vs_delay_graph_displayed", False):
        graph_canvas.delete("all")
    else:
        profit_delay = analyze_profit_vs_shipping_delay(events)
        draw_profit_vs_delay_chart(graph_canvas, profit_delay)
    state["profit_vs_delay_graph_displayed"] = not state.get("profit_vs_delay_graph_displayed", False)

    #Aналіз продажів за час
def analyze_sales_over_time(events):
    sales_over_time = defaultdict(float)
    for event in events:
        try:
            order_date = datetime.strptime(event['Order Date'], '%m/%d/%Y')
            month = order_date.strftime('%Y-%m')  # Формат: '2024-08'
            sales = float(event['Units Sold']) * float(event['Unit Price'])
            sales_over_time[month] += sales
        except (ValueError, KeyError):
            continue
    return sales_over_time
# Намалював графік продажів понаднормово
def draw_sales_over_time_chart(canvas, data):
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    if not data:
        canvas.create_text(width // 2, height // 2, text="No data available", font=("Helvetica", 12), fill="red")
        return

    draw_grid(canvas, width, height)
    margin = 40

    max_value = max(data.values(), default=1)
    prev_x, prev_y = None, None

    for i, (month, sales) in enumerate(sorted(data.items())):
        x = margin + i * (width - 2 * margin) / (len(data) - 1)
        y = height - margin - (sales / max_value * (height - 2 * margin))
        if prev_x is not None:
            canvas.create_line(prev_x, prev_y, x, y, fill="blue", width=2)
        prev_x, prev_y = x, y
        canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue", outline="black")

    if prev_x is not None:
        canvas.create_text(prev_x, prev_y - 10, text=f"{sales:.2f}", font=("Helvetica", 8), fill="black")
# Переключить графiк сверхурочных продаж
def toggle_sales_over_time_graph(events):
    if state.get("sales_over_time_graph_displayed", False):
        graph_canvas.delete("all")
    else:
        sales_time = analyze_sales_over_time(events)
        draw_sales_over_time_chart(graph_canvas, sales_time)
    state["sales_over_time_graph_displayed"] = not state.get("sales_over_time_graph_displayed", False)


# Змінити розмір зображень
def resize_image(image_path, size=(48, 48)):
    with Image.open(image_path) as img:
        img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    #Aналізувати продажі за днями
def analyze_sales_by_day(events):
    sales_by_day = defaultdict(float)

    for event in events:
        try:
            units_sold = float(event['Units Sold'])
            date_str = event['Order Date']
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            day_of_week = date_obj.strftime('%A')
            sales_by_day[day_of_week] += units_sold
        except (ValueError, KeyError):
            continue

    return sales_by_day

# Малювати діаграму  за  тиждень
def draw_day_of_week_chart(canvas, data):
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    if not data:
        canvas.create_text(width // 2, height // 2, text="No data available", font=("Helvetica", 12), fill="red")
        return

    draw_grid(canvas, width, height)
    margin = 40
    bar_width = (width - 2 * margin) / len(data)

    max_value = max(data.values(), default=1)

    for i, (day, sales) in enumerate(data.items()):
        x1 = margin + i * bar_width
        y1 = height - margin
        x2 = x1 + bar_width - 10
        y2 = height - margin - (sales / max_value * (height - 2 * margin))
        canvas.create_rectangle(x1, y1, x2, y2, fill="skyblue", outline="blue")
        canvas.create_text((x1 + x2) / 2, y1 + 10, text=day, angle=45, font=("Helvetica", 10), fill="black")
        # Перемикати графік дня тижня
def toggle_day_of_week_graph(events):
    if state.get("day_of_week_graph_displayed", False):
        graph_canvas.delete("all")
    else:
        sales_by_day = analyze_sales_by_day(events)
        print("Sales by Day Data:", sales_by_day)  # Debug print
        draw_day_of_week_chart(graph_canvas, sales_by_day)
    state["day_of_week_graph_displayed"] = not state.get("day_of_week_graph_displayed", False)


images = {name: resize_image(path) for name, path in image_paths.items()}

# Створення кадрів та кнопок
control_frame = tk.Frame(root)
control_frame.pack(side=tk.TOP, fill=tk.X)

state = {
    "summary_displayed": False,
    "sales_displayed": False,
    "graph_displayed": False
}
images = {name: resize_image(path) for name, path in image_paths.items()}

# Create and configure the 'Sales by Day' button with an image
day_of_week_button = tk.Button(control_frame, image=images["day_of_week"], command=lambda: toggle_day_of_week_graph(events),
                               borderwidth=0, background=root.cget('bg'))
day_of_week_button.grid(row=0, column=6, padx=8, pady=8)
summary_button = tk.Button(control_frame, image=images["summary"], command=lambda: toggle_summary(events, countries),
                           borderwidth=0, background=root.cget('bg'))
summary_button.grid(row=0, column=0, padx=8, pady=8)

sales_button = tk.Button(control_frame, image=images["sales"],
                         command=lambda: toggle_sales_by_category(events, products), borderwidth=0,
                         background=root.cget('bg'))
sales_button.grid(row=0, column=1, padx=8, pady=8)

bar_button = tk.Button(control_frame, image=images["bar"], command=lambda: toggle_graph("bar", events, products),
                       borderwidth=0, background=root.cget('bg'))
bar_button.grid(row=0, column=3, padx=8, pady=8)

line_button = tk.Button(control_frame, image=images["line"], command=lambda: toggle_graph("line", events, products),
                        borderwidth=0, background=root.cget('bg'))
line_button.grid(row=0, column=4, padx=8, pady=8)

# Кнопка "Про програму" із зображенням
about_button = tk.Button(control_frame, image=images["about"], command=show_about, borderwidth=0,
                         background=root.cget('bg'))
about_button.grid(row=0, column=10, padx=8, pady=8)

day_of_week_button = tk.Button(control_frame,image=images["week"], borderwidth=0,command=lambda: toggle_day_of_week_graph(events))
day_of_week_button.grid(row=0, column=6, padx=8, pady=8)

show_chart_button  = tk.Button(control_frame, image=images["ABC_Chart"], command=on_click_show_abc_chart,
                                   borderwidth=0, background=root.cget('bg'))
show_chart_button .grid(row=0, column=11, padx=8, pady=8)
# Кнопки для  графіків


profit_vs_delay_button = tk.Button(control_frame, image=images["profit_vs_delay"], command=lambda: toggle_profit_vs_delay_graph(events),
                                   borderwidth=0, background=root.cget('bg'))
profit_vs_delay_button.grid(row=0, column=8, padx=8, pady=8)

sales_over_time_button = tk.Button(control_frame, image=images["time"], command=lambda: toggle_sales_over_time_graph(events),
                                   borderwidth=0, background=root.cget('bg'))
sales_over_time_button.grid(row=0, column=9, padx=8, pady=8)

# Мітки та полотно
summary_label = tk.Label(root, text="", font=("Helvetica", 12))
summary_label.pack(pady=10)

sales_text_label = tk.Label(root, text="", font=("Helvetica", 12))
sales_text_label.pack(pady=10)

graph_canvas = tk.Canvas(root, width=600, height=400, bg="white")
graph_canvas.pack(pady=20)

# Завантаження та очищення даних
events, products, countries = load_data()
clean_data(events, products)
inspect_data(events, products)
data_summary(events, products)

root.mainloop()

if __name__ == "__main__":
    ()
