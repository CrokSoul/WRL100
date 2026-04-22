import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import csv
import os
from datetime import datetime


STOCK_CSV = "stock.csv"
RECORDS_CSV = "transactions.csv"


def read_stock():
    products = {}
    try:
        with open(STOCK_CSV, mode = 'r') as stock:
            reader = csv.DictReader(stock)
            for row in reader:
                product_id = row['ID']
                product_name = row['Name of product']
                product_price = int(row['Price'])
                product_quantity = int(row['Quantity'])
                products[product_id] = (product_name, product_price, product_quantity)

    except FileNotFoundError:
        messagebox.showerror("Error", f"File {STOCK_CSV} not found, please close the program!")
    return products


def update_stock(quantity):
    with open(STOCK_CSV, mode = 'w', newline = '') as stock:
        writer = csv.DictWriter(stock, fieldnames = ['ID', 'Name of product', 'Price', 'Quantity'])
        writer.writeheader()
        for product_id, (product_name, product_price, product_quantity) in quantity.items():
            writer.writerow({'ID': product_id, 'Name of product': product_name, 'Price': product_price, 'Quantity': product_quantity})

#WORKER WINDOW
def open_worker_window():
    app.withdraw()
    products = read_stock()
    if not products:
        return

    worker_window = tk.Toplevel(app)
    worker_window.title("OneStop IT (Worker)")
    worker_window.geometry("400x475")

    order = []

    def save_transactions():
        with open(RECORDS_CSV, mode = 'a', newline = '') as file:
            csv_rows = ['Date', 'ID', 'Name', 'Price', 'Quantity']
            writer = csv.DictWriter(file, fieldnames = csv_rows)
            
            date = datetime.now().strftime('%Y-%m-%d')
            for product_id, product_name, product_price, in order:
                writer.writerow({
                    'Date': date,
                    "ID": product_id,
                    'Name': product_name,
                    'Price': product_price,
                    'Quantity': 1
                })



    def add_to_cart():
        selected = choose_product.get()
        if selected:
            selected_id = selected.split(' - ')[0]
            product_name, product_price, product_quantity = products[selected_id]
            if product_quantity > 0:
                order.append((selected_id, product_name, product_price))
                update_order()
                products[selected_id] = (product_name, product_price, product_quantity - 1)
            else:
                messagebox.showwarning("Error", f"The product: '{product_name}' is out of stock!")
        else:
            messagebox.showwarning("Error", "Choose the product!")

            
    def update_order():
        total_price = 0
        order_listbox.delete(0, tk.END)
        for _, product_name, product_price in order:
            order_listbox.insert(tk.END, f"{product_name} - {product_price} GBP")
            total_price += product_price
        total_price_label.config(text = f"Total price is: {total_price} GBP")
        

    def cash_payment():
        try:
            cash = float(cash_entry.get())
            total = sum(product_price for _, _, product_price in order)
            if cash >= total:
                change = cash - total
                messagebox.showinfo("Cash Payment", f"Payment was successful! Change: {change} GBP")
                save_transactions()
                update_stock(products)
                order.clear()
                update_order()
                cash_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Insufficient funds!", f"Not enough money to pay!")
        except ValueError:
            messagebox.showerror("Error", f"Please enter the correct amount!")


    def card_payment():
        messagebox.showinfo("Card Payment", f"Card payment was successful!")
        save_transactions()
        update_stock(products)
        order.clear()
        update_order()


    tk.Label(worker_window, text = "Choose a product:").pack(pady = 5)
    choose_product = ttk.Combobox(worker_window, values = [f"{pid} - {name}" for pid, (name, _, _) in products.items()])
    choose_product.pack(pady = 5)

    add_to_order = tk.Button(worker_window, text = "Add to order", command = add_to_cart)
    add_to_order.pack(pady = 5)

    tk.Label(worker_window, text = "Order:").pack(pady = 5)
    order_listbox = tk.Listbox(worker_window, width = 50, height = 10)
    order_listbox.pack(pady = 5)

    total_price_label = tk.Label(worker_window, text = "Total price: 0 GBP", font = ("Arial", 12, "bold"))
    total_price_label.pack(pady = 5)

    tk.Label(worker_window, text = "Enter the cash amount and press PAY or pay by CARD:").pack(pady = 5)
    cash_entry = tk.Entry(worker_window)
    cash_entry.pack(pady = 5)

    pay_button = tk.Button(worker_window, text = "PAY", command = cash_payment)
    pay_button.pack(pady = 5)

    pay_card = tk.Button(worker_window, text = "CARD", command = card_payment)
    pay_card.pack(pady = 5)



def open_admin_window():
    app.withdraw()
    admin_window = tk.Toplevel(app)
    admin_window.title("OneStop IT (Admin)")
    admin_window.geometry("400x475")


    def generate_new_id(file):
        with open(file, mode = 'r', newline = '') as file_id:
            reader = list(csv.reader(file_id))
            return len(reader)


    def view_stock():
        try:
            with open(STOCK_CSV, mode = 'r', newline = '') as stock:
                reader = csv.DictReader(stock)
                result = "Stock:\n"
                for row in reader:
                    result += f"ID: {row['ID']}, Product Name: {row['Name of product']}, Price: {row['Price']}, Quantity: {row['Quantity']}\n"
                messagebox.showinfo("Stock", result)
        except FileNotFoundError:
            messagebox.showerror("Error", f"File {STOCK_CSV} not fount!")


    def add_new_product():
        name = simpledialog.askstring("Name", f"Enter the name of new product: ")
        price = simpledialog.askstring("Price", f"Enter the price of new product: ")
        quantity = simpledialog.askstring("Quantity", f"Enter the quantity of new product: ")

        if name and price and quantity:
            try:
                price = int(price.strip())
                quantity = int(quantity.strip())
                product_id = generate_new_id(STOCK_CSV)

                with open(STOCK_CSV, mode = 'a', newline = '') as file:
                    writer = csv.writer(file)
                    writer.writerow([product_id, name, price, quantity])
                    messagebox.showinfo("Success", "Product added successfully!")
            except ValueError:
                messagebox.showerror("Error", "The price should be as a number, and price as integer!")
        else:
            messagebox.showwarning("Input error", "All fields are required!")


    def edit_product():
        product_id = simpledialog.askstring("Edit product", "Enter the product ID you want to edit: ")
        new_name = simpledialog.askstring("New name", "Enter new name for the product: ")
        new_price = simpledialog.askstring("New price", "Enter new price for the product(GBP): ")
        new_quantity = simpledialog.askstring("New quantity", "Enter new quantity for the product: ")
    
        updated = False
        products = []

        try:
            with open(STOCK_CSV, mode = 'r', newline = '') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['ID'] == product_id:
                        if new_name: row['Name of product'] = new_name.strip()
                        if new_price: row['Price'] = new_price.strip()
                        if new_quantity: row['Quantity'] = new_quantity.strip()
                        updated = True
                    products.append(row)

            with open(STOCK_CSV, mode = 'w', newline = '') as file:
                csv_rows = ['ID', 'Name of product', 'Price', 'Quantity']
                writer = csv.DictWriter(file, fieldnames = csv_rows)
                writer.writeheader()
                writer.writerows(products)

            if updated:
                messagebox.showinfo("Success", "Product updated successfully!")
            else:
                messagebox.showerror("Error", "No product with such ID found.")
    
        except FileNotFoundError:
            messagebox.showerror("Error", f"File {STOCK_CSV} not found!")


    def remove_product():
        product_id = simpledialog.askstring("Product removal", "Enter the product ID to delete:")
        products = []
        deleted = False

        try:
            with open(STOCK_CSV, mode = 'r', newline = '') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['ID'] != product_id:
                        products.append(row)
                    else:
                        deleted = True

            with open(STOCK_CSV, mode = 'w', newline = '') as file:
                csv_rows = ['ID', 'Name of product', 'Price', 'Quantity']
                writer = csv.DictWriter(file, fieldnames=csv_rows)
                writer.writeheader()
                writer.writerows(products)

            if deleted:
                messagebox.showinfo("Success", "Product successfully removed!")
            else:
                messagebox.showerror("Error", "No product with this ID was found!")
        
        except FileNotFoundError:
            messagebox.showerror("Error", f"File {STOCK_CSV} not found!")



    def edit_price():
        product_id = simpledialog.askstring("Price update", "Enter product ID to update price: ")
        new_price = simpledialog.askstring("New price", "Enter new price(GBP): ")

        if not product_id or not new_price:
            messagebox.showwarning("Error", "ID and New price are required!")
            return

        updated = False
        products = []

        try:
            with open(STOCK_CSV, mode = 'r', newline = '') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['ID'] == product_id:
                        row['Price'] = new_price
                        updated = True
                    products.append(row)

            with open(STOCK_CSV, mode = 'w', newline = '') as file:
                csv_rows = ['ID', 'Name of product', 'Price', 'Quantity']
                writer = csv.DictWriter(file, fieldnames = csv_rows)
                writer.writeheader()
                writer.writerows(products)

            if updated:
                messagebox.showinfo("Success", "Product price has been successfully changed!")
            else:
                messagebox.showerror("Error", "No product with such ID found.")

        except FileNotFoundError:
            messagebox.showerror("Error", f"File {STOCK_CSV} not found!")


    def view_sales():
        try:
            with open(RECORDS_CSV, mode='r', newline='') as sales:
                reader = csv.DictReader(sales)
                result = "Sales Transactions:\n"
                for row in reader:
                    result += f"ID: {row['ID']}, Product Name: {row['Name']}, Price: {row['Price']}, Quantity Sold: {row['Quantity']}, Date: {row['Date']}\n"
                messagebox.showinfo("Sales Transactions", result)
        except FileNotFoundError:
            messagebox.showerror("Error", f"File {RECORDS_CSV} not found!")


    def view_by_date():
        date = simpledialog.askstring("View Records by date", f"Enter the date in YYYY-MM-DD format:")
        if not date:
            return
        
        try:
            with open(RECORDS_CSV, mode = 'r', newline = '') as by_date:
                reader = csv.DictReader(by_date)
                result = f"Sales for {date}:\n"
                found = False
                total_amount = 0

                for row in reader:
                    if row['Date'].strip() == date:
                        found = True
                        price = float(row['Price'].strip())
                        quantity = int(row['Quantity'].strip())
                        subtotal = price * quantity
                        total_amount += subtotal
                        result += (f"ID: {row['ID']}, Name: {row['Name']}, Price: {price} GBP , Quantity: {quantity}, Sum: {subtotal} GBP\n")

                if found:
                    result += f"\nTotal amount of sales: {total_amount: } GBP"
                    messagebox.showinfo("Result", result)
                else:
                    messagebox.showinfo("Result", f"No records found for {date}")

        except FileNotFoundError:
            messagebox.showerror("Error", f"File {RECORDS_CSV} not found!")


    tk.Label(admin_window, text = "Welcome Admin!", font = ("Arial", 12, "bold")).pack(pady = 5)
    tk.Label(admin_window, text = "Select an option:").pack(pady = 5)

    View_stock = tk.Button(admin_window, text = "View stock", height = 2, width = 25, command = view_stock)
    View_stock.pack(pady = 5)

    Add_new_product = tk.Button(admin_window, text = "Add new product", height = 2, width = 25, command = add_new_product)
    Add_new_product.pack(pady = 5)

    Edit_product = tk.Button(admin_window, text = "Edit product", height = 2, width = 25, command = edit_product)
    Edit_product.pack(pady = 5)

    Remove_product = tk.Button(admin_window, text = "Remove product", height = 2, width = 25, command = remove_product)
    Remove_product.pack(pady = 5)

    Edit_price_of_the_product = tk.Button(admin_window, text = "Edit price of the product", height = 2, width = 25, command = edit_price)
    Edit_price_of_the_product.pack(pady = 5)

    View_all_records = tk.Button(admin_window, text = "View all records", height = 2, width = 25, command = view_sales)
    View_all_records.pack(pady = 5)

    View_by_date = tk.Button(admin_window, text = "View records by date", height = 2, width = 25, command = view_by_date)
    View_by_date.pack(pady = 5)


def open_password_window():
    password_window = tk.Toplevel()
    password_window.title("OneStop IT (Password)")
    password_window.geometry("200x150")


    def password_system():
            Password = "1234"
            Entered = Number1_password.get()
            if Entered == Password:
                password_window.destroy()
                open_admin_window()
            else:
                messagebox.showwarning("Error", f"Password incorrect, please try again!")
                password_window.destroy()

    
    Number1_password = tk.StringVar()

    tk.Label(password_window, text = "Enter the password: ").pack(pady = 5)
    Pass = ttk.Entry(password_window, show = "*", width = 20, textvariable = Number1_password)
    Pass.pack(pady = 5)

    enter_pass = ttk.Button(password_window, text = "LOG IN", command = password_system)
    enter_pass.pack(pady = 5)



app = tk.Tk()
app.title("OneStop IT (Login Page)")
app.geometry("350x200")


tk.Label(app, text = "Log in as:", font = ("Arial",12)).pack(pady = 20)

worker_button = tk.Button(app, text = "Worker", width = 30, command = open_worker_window)
worker_button.pack(pady = 5)

admin_button = tk.Button(app, text = "Admin", width = 30, command = open_password_window)
admin_button.pack(pady = 5)

app.mainloop()