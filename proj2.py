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
    engine_type VARCHAR(20),
    image_url VARCHAR(1000)
)
""")
db.commit()

def add_details():
    company = simpledialog.askstring("Add Details", "Enter Company Name:")
    
    if company:
        car_name = simpledialog.askstring("Add Details", "Enter Car Name:")
        
        if car_name:
            year = simpledialog.askinteger("Add Details", "Enter Year:")
            
            engine_type_menu = tk.Toplevel(root)
            engine_type_menu.title("Select Engine Type")
            
            def set_engine_type(selected_engine_type):
                engine_type_menu.destroy()
                add_car_with_engine_type(company, car_name, year, selected_engine_type)

            petrol_button = tk.Button(engine_type_menu, text="Petrol", command=lambda: set_engine_type("Petrol"))
            diesel_button = tk.Button(engine_type_menu, text="Diesel", command=lambda: set_engine_type("Diesel"))
            electric_button = tk.Button(engine_type_menu, text="Electric", command=lambda: set_engine_type("Electric"))

            petrol_button.pack(pady=5)
            diesel_button.pack(pady=5)
            electric_button.pack(pady=5)

def add_car_with_engine_type(company, car_name, year, engine_type):
    image_url = simpledialog.askstring("Add Details", "Enter Image URL:")
    
    cursor.execute("INSERT INTO cars (company, car_name, year, engine_type, image_url) VALUES (%s, %s, %s, %s, %s)",
                   (company, car_name, year, engine_type, image_url))
    db.commit()
    messagebox.showinfo("Success", "Details added successfully!")

def show_details(cursor):
    clear_widgets(root)
    
    cursor.execute("SELECT DISTINCT company FROM cars")
    companies = cursor.fetchall()

    if not companies:
        messagebox.showinfo("No Data", "No details found. Please add data first.")
        return
    
    company_names = [company[0] for company in companies]

    for company in company_names:
        company_button = tk.Button(root, text=company,
                                   command=lambda comp=company: show_company_models(comp, cursor))
        company_button.pack(pady=5)

def show_company_models(selected_company, cursor):
    clear_widgets(root)
    
    cursor.execute("SELECT DISTINCT car_name FROM cars WHERE company = %s", (selected_company,))
    car_names = cursor.fetchall()

    for car in car_names:
        car_button = tk.Button(root, text=car[0],
                               command=lambda car_name=car[0]: show_car_details(selected_company, car_name, cursor))
        car_button.pack(pady=5)

def show_car_details(company, car_name, cursor):
    clear_widgets(root)
    
    cursor.execute("SELECT car_name, year, engine_type, image_url FROM cars WHERE company = %s AND car_name = %s",
                   (company, car_name))
    car_details = cursor.fetchall()

    for car in car_details:
        car_frame = tk.Frame(root, bg="white")
        car_frame.pack(padx=20, pady=20)

        car_label = tk.Label(car_frame, text=f"Car Name: {car[0]}, Year: {car[1]}, Engine Type: {car[2]}", bg="white")
        car_label.pack()

        if car[3]:  # If there's an image URL
            try:
                response = urllib.request.urlopen(car[3])  # Fetch the image from the URL
                img_data = response.read()
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((200, 150), Image.BILINEAR)  # Use Image.BILINEAR for resizing
                img = ImageTk.PhotoImage(img)

                image_label = tk.Label(car_frame, image=img, bg="white")
                image_label.image = img
                image_label.pack(padx=5, pady=5)
            except Exception as e:
                print("Error loading image:", e)
def clear_widgets(parent):
    for widget in parent.winfo_children():
        widget.destroy()
# Create the main window
root = tk.Tk()
root.title("Car Database")
# Load the background image
bg_image = Image.open("background.jpg")  # Replace with your image path
bg_photo = ImageTk.PhotoImage(bg_image)
# Get the dimensions of the background image
bg_width = bg_photo.width()
bg_height = bg_photo.height()
# Set the geometry to match the dimensions of the background image
root.geometry(f"{bg_width}x{bg_height}")
# Create a label to display the background image
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
# Function to create smaller buttons
def create_button(parent, text, command):
    button = tk.Button(parent, text=text, command=command, width=int(bg_width * 0.01), height=int(bg_height * 0.005))
    return button
# Create buttons
add_button = create_button(root, "Add", add_details)
add_button.pack(pady=int(bg_height * 0.003))
show_button = create_button(root, "Show", lambda: show_details(cursor))
show_button.pack(pady=int(bg_height * 0.003))
root.mainloop()
# Close the database connection when the GUI is closed
db.close()
