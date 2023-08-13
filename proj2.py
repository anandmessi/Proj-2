import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from tkinter import ttk
import mysql.connector
from PIL import Image, ImageTk
import io
import urllib.request
# Connect to the MySQL database server
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2006"
)

# Create a cursor
cursor = db.cursor()

# Create the database if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS car_database")
cursor.execute("USE car_database")

# Create a table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS cars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company VARCHAR(255),
    car_name VARCHAR(255),
    year INT,
    image_url VARCHAR(1000)  -- Increase the length of image_url column
)
""")
db.commit()

def add_details():
    company = simpledialog.askstring("Add Details", "Enter Company Name:")
    
    if company:
        car_name = simpledialog.askstring("Add Details", "Enter Car Name:")
        
        if car_name:
            year = simpledialog.askinteger("Add Details", "Enter Year:")
            
            image_url = simpledialog.askstring("Add Details", "Enter Image URL (optional):")

            cursor.execute("INSERT INTO cars (company, car_name, year, image_url) VALUES (%s, %s, %s, %s)",
                           (company, car_name, year, image_url))
            db.commit()
            messagebox.showinfo("Success", "Details added successfully!")
        else:
            messagebox.showerror("Error", "Car Name is required.")
    else:
        messagebox.showerror("Error", "Company Name is required.")

def show_details():
    cursor.execute("SELECT DISTINCT company FROM cars")
    companies = cursor.fetchall()

    if not companies:
        messagebox.showinfo("No Data", "No details found. Please add data first.")
        return
    
    company_names = [company[0] for company in companies]

    def show_selected_company_details(selected_company):
        cursor.execute("SELECT car_name, year, image_url FROM cars WHERE company = %s", (selected_company,))
        car_details = cursor.fetchall()

        details_window = tk.Toplevel(root)
        details_window.title(f"{selected_company} Car Details")

        for car in car_details:
            car_frame = ttk.Frame(details_window)
            car_frame.pack(padx=10, pady=10, fill="both", expand=True)

            car_label = tk.Label(car_frame, text=f"Car Name: {car[0]}, Year: {car[1]}")
            car_label.pack()

            if car[2]:  # If there's an image URL
                print("Image URL:", car[2])
                
                try:
                    response = urllib.request.urlopen(car[2])  # Fetch the image from the URL
                    img_data = response.read()
                    img = Image.open(io.BytesIO(img_data))
                    img = img.resize((200, 150), Image.BILINEAR)  # Use Image.BILINEAR for resizing
                    img = ImageTk.PhotoImage(img)

                    image_label = tk.Label(car_frame, image=img)
                    image_label.image = img
                    image_label.pack(padx=5, pady=5)
                except Exception as e:
                    print("Error loading image:", e)

    top = tk.Toplevel(root)
    top.title("Select Company")

    for company in company_names:
        company_button = tk.Button(top, text=company,
                                   command=lambda comp=company: show_selected_company_details(comp))
        company_button.pack(pady=5)


# Create the main window
root = tk.Tk()
root.title("Car Database")

add_button = tk.Button(root, text="Add Details", command=add_details)
add_button.pack(pady=10)

show_button = tk.Button(root, text="Show Details", command=show_details)
show_button.pack(pady=10)

root.mainloop()

# Close the database connection when the GUI is closed
db.close()
