import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import mysql.connector
from PIL import Image, ImageTk

# Connect to the MySQL database server
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2006",
    database="car_database"  # Add this line to specify the database
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

# Function to clear widgets from the window
def clear_widgets(parent):
    for widget in parent.winfo_children():
        widget.destroy()

# Function to add details
def add_details():
    company = simpledialog.askstring("Add Details", "Enter Company Name:")
    
    if company:
        car_name = simpledialog.askstring("Add Details", "Enter Car Name:")
        
        if car_name:
            year = simpledialog.askinteger("Add Details", "Enter Year:")
            engine_type_menu = tk.Toplevel(root)
            engine_type_menu.title("Select Engine Type")
            
            # Function to handle file selection
            def choose_image():
                file_path = filedialog.askopenfilename(title="Select Image File", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
                if file_path:
                    cursor.execute("INSERT INTO cars (company, car_name, year, engine_type, image_url) VALUES (%s, %s, %s, %s, %s)",
                                   (company, car_name, year, selected_engine_type, file_path))
                    db.commit()
                    messagebox.showinfo("Success", "Details added successfully!")
                
            # Button to choose image file
            tk.Button(engine_type_menu, text="Choose Image", command=choose_image).pack()

            # Create buttons for engine types
            engine_types = ["Petrol", "Diesel", "Electric", "Hybrid"]
            for engine_type in engine_types:
                tk.Button(engine_type_menu, text=engine_type, command=lambda et=engine_type: set_engine_type(et)).pack()

# Function to show details
def show_details(cursor):
    clear_widgets(root)
    
    cursor.execute("SELECT DISTINCT company FROM cars")
    companies = cursor.fetchall()

    if not companies:
        messagebox.showinfo("No Data", "No details found. Please add data first.")
        return
    
    for company in companies:
        tk.Button(root, text=company[0], command=lambda comp=company[0]: show_company_models(comp, cursor)).pack(pady=5)

# Function to show models of a selected company
def show_company_models(selected_company, cursor):
    clear_widgets(root)
    
    cursor.execute("SELECT DISTINCT car_name FROM cars WHERE company = %s", (selected_company,))
    car_names = cursor.fetchall()

    for car in car_names:
        tk.Button(root, text=car[0], command=lambda car_name=car[0]: show_car_details(selected_company, car_name, cursor)).pack(pady=5)

# Function to show details of a selected car
def show_car_details(company, car_name, cursor):
    clear_widgets(root)
    
    cursor.execute("SELECT car_name, year, engine_type, image_url FROM cars WHERE company = %s AND car_name = %s",
                   (company, car_name))
    car_details = cursor.fetchall()

    for car in car_details:
        car_frame = tk.Frame(root, bg="white")
        car_frame.pack(padx=20, pady=20)

        tk.Label(car_frame, text=f"Car Name: {car[0]}, Year: {car[1]}, Engine Type: {car[2]}", bg="white").pack()

        if car[3]:
            try:
                img = Image.open(car[3])
                img = img.resize((200, 150), Image.BILINEAR)
                img = ImageTk.PhotoImage(img)
                tk.Label(car_frame, image=img, bg="white").image = img
                tk.Label(car_frame, image=img, bg="white").pack(padx=5, pady=5)
            except Exception as e:
                print("Error loading image:", e)
# Function to edit details
def edit_details():
    selected_company = simpledialog.askstring("Edit Details", "Enter Company Name:")
    
    if selected_company:
        selected_car = simpledialog.askstring("Edit Details", "Enter Car Name:")
        
        if selected_car:
            edit_window = tk.Toplevel(root)
            edit_window.title("Edit Car Details")

            # Fetch current details for the selected car
            cursor.execute("SELECT year, engine_type, image_url FROM cars WHERE company = %s AND car_name = %s",
                           (selected_company, selected_car))
            current_details = cursor.fetchone()

            if current_details:
                current_year, current_engine_type, current_image_url = current_details

                # Create entry fields with current values
                year_var = tk.StringVar(value=current_year)
                engine_type_var = tk.StringVar(value=current_engine_type)
                image_url_var = tk.StringVar(value=current_image_url)

                # Create labels and entry widgets for each field
                tk.Label(edit_window, text="Year:").pack()
                year_entry = tk.Entry(edit_window, textvariable=year_var)
                year_entry.pack()

                tk.Label(edit_window, text="Engine Type:").pack()
                engine_type_entry = tk.Entry(edit_window, textvariable=engine_type_var)
                engine_type_entry.pack()

                tk.Label(edit_window, text="Image URL:").pack()

                # Function to handle file selection
                def choose_image():
                    file_path = filedialog.askopenfilename(title="Select Image File", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
                    if file_path:
                        image_url_var.set(file_path)

                # Button to choose image file
                tk.Button(edit_window, text="Choose Image", command=choose_image).pack()

                # Function to handle save button click
                def save_button_click():
                    save_changes(selected_company, selected_car, year_var.get(), engine_type_var.get(), image_url_var.get())
                    # Close the edit window
                    edit_window.destroy()

                # Save button
                tk.Button(edit_window, text="Save Changes", command=save_button_click).pack()

# Function to save changes
def save_changes(company, car_name, new_year, new_engine_type, new_image_url):
    cursor.execute("""
    UPDATE cars
    SET year = %s, engine_type = %s, image_url = %s
    WHERE company = %s AND car_name = %s
    """, (new_year, new_engine_type, new_image_url, company, car_name))
    db.commit()
    messagebox.showinfo("Success", "Changes saved successfully!")
    # Show updated details
    show_details(cursor)

# Function to handle delete button click
def delete_button_click():
    selected_company = simpledialog.askstring("Delete Company", "Enter Company Name:")

    if selected_company:
        delete_company(selected_company)

# Function to delete a company and its cars
def delete_company(selected_company):
    # Delete the company and its cars from the database
    cursor.execute("""
    DELETE FROM cars 
    WHERE company = %s
    """, (selected_company,))
    db.commit()
    messagebox.showinfo("Success", f"{selected_company} and its cars deleted successfully!")
    # Show updated details
    show_details(cursor)

# Function to handle delete car button click
def delete_car_button_click():
    selected_company = simpledialog.askstring("Delete Car", "Enter Company Name:")

    if selected_company:
        selected_car = simpledialog.askstring("Delete Car", "Enter Car Name:")

        if selected_car:
            delete_car(selected_company, selected_car)

# Function to delete a car
def delete_car(selected_company, selected_car):
    # Delete the car from the database
    cursor.execute("""
    DELETE FROM cars 
    WHERE company = %s AND car_name = %s
    """, (selected_company, selected_car))
    db.commit()
    messagebox.showinfo("Success", f"{selected_car} deleted successfully!")
    # Show updated details
    show_details(cursor)

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

edit_button= create_button(root, "Edit", edit_details)
edit_button.pack(pady=int(bg_height * 0.003))

delete_button = create_button(root, "Delete", delete_button_click)
delete_button.pack(pady=int(bg_height * 0.003))

delete_car_button = create_button(root, "Delete Car", delete_car_button_click)
delete_car_button.pack(pady=int(bg_height * 0.003))

# Main loop
root.mainloop()

# Close the database connection when the GUI is closed
db.close()