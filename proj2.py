import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import mysql.connector
from PIL import Image, ImageTk

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="car_database" 
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

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title, options):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")

        self.result = None

        label = tk.Label(self, text=f"Select {title}:")
        label.pack(pady=10)

        combo_var = tk.StringVar()
        combo = ttk.Combobox(self, textvariable=combo_var, values=options)
        combo.pack(pady=10)

        btn_ok = tk.Button(self, text="OK", command=lambda: self.ok_button(combo_var.get()))
        btn_ok.pack(pady=10)

    def ok_button(self, value):
        self.result = value
        self.destroy()

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
            def choose_image(selected_engine_type):
                file_path = filedialog.askopenfilename(title="Select Image File", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif")])
                if file_path:
                    cursor.execute("INSERT INTO cars (company, car_name, year, engine_type, image_url) VALUES (%s, %s, %s, %s, %s)",
                                   (company, car_name, year, selected_engine_type, file_path))
                    db.commit()
                    messagebox.showinfo("Success", "Details added successfully!")

            # Create buttons for engine types
            engine_types = ["Petrol", "Diesel", "Electric", "Hybrid"]
            for engine_type in engine_types:
                tk.Button(engine_type_menu, text=engine_type, command=lambda et=engine_type: choose_image(et)).pack()

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
        car_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left side: Car details
        details_frame = tk.Frame(car_frame, bg="white")
        details_frame.pack(side=tk.LEFT, padx=20)

        tk.Label(details_frame, text=f"Car Name: {car[0]}", bg="white").pack(anchor='w')
        tk.Label(details_frame, text=f"Year: {car[1]}", bg="white").pack(anchor='w')
        tk.Label(details_frame, text=f"Engine Type: {car[2]}", bg="white").pack(anchor='w')

        # Right side: Image
        image_frame = tk.Frame(car_frame, bg="white")
        image_frame.pack(side=tk.RIGHT)

        if car[3]:
            try:
                img = Image.open(car[3])
                img = img.resize((root.winfo_screenwidth() // 3, root.winfo_screenheight() // 3), Image.LANCZOS)
                img = ImageTk.PhotoImage(img)
                img_label = tk.Label(image_frame, image=img, bg="white")
                img_label.image = img
                img_label.pack(padx=20, pady=20, anchor='e')
            except Exception as e:
                print("Error loading image:", e)

        # Back button
        back_button = tk.Button(car_frame, text="Back", command=lambda: show_company_models(company, cursor))
        back_button.pack(side=tk.BOTTOM, pady=20)

# Function to show edit options for the selected company and car
def show_edit_options(selected_company, selected_car):
    edit_options_window = tk.Toplevel(root)
    edit_options_window.title("Edit Options")

    # Function to handle edit button click
    def edit_button_click():
        edit_car_details(selected_company, selected_car)

    # Edit button
    tk.Button(edit_options_window, text="Edit Car Details", command=edit_button_click).pack()

    # Function to handle delete button click
    def delete_button_click():
        delete_car(selected_company, selected_car)

    # Delete button
    tk.Button(edit_options_window, text="Delete Car", command=delete_button_click).pack()

def edit_car_details(selected_company, selected_car):
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Car Details")

    # Fetch current details for the selected car
    cursor.execute("SELECT car_name, year, engine_type, image_url FROM cars WHERE company = %s AND car_name = %s",
                   (selected_company, selected_car))
    current_details = cursor.fetchone()

    if current_details:
        current_car_name, current_year, current_engine_type, current_image_url = current_details

        # Create entry fields with current values
        car_name_var = tk.StringVar(value=current_car_name)
        year_var = tk.StringVar(value=current_year)
        engine_type_var = tk.StringVar(value=current_engine_type)
        image_url_var = tk.StringVar(value=current_image_url)

        # Create labels and entry widgets for each field
        tk.Label(edit_window, text="Car Name:").pack()
        car_name_entry = tk.Entry(edit_window, textvariable=car_name_var)
        car_name_entry.pack()

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
            new_car_name = car_name_var.get()
            new_year = year_var.get()
            new_engine_type = engine_type_var.get()
            new_image_url = image_url_var.get()

            # Validate that the new car name is not empty
            if not new_car_name:
                messagebox.showerror("Error", "Car Name cannot be empty.")
                return

            # Update the car details
            cursor.execute("""
            UPDATE cars
            SET car_name = %s, year = %s, engine_type = %s, image_url = %s
            WHERE company = %s AND car_name = %s
            """, (new_car_name, new_year, new_engine_type, new_image_url, selected_company, selected_car))
            db.commit()

            # Show success message
            messagebox.showinfo("Success", "Changes saved successfully!")

            # Close the edit window
            edit_window.destroy()

            # Show updated details
            show_details(cursor)

        # Save button
        tk.Button(edit_window, text="Save Changes", command=save_button_click).pack()

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
    # Fetch distinct companies
    cursor.execute("SELECT DISTINCT company FROM cars")
    companies = cursor.fetchall()

    if not companies:
        messagebox.showinfo("No Data", "No companies found. Please add data first.")
        return

    # Create a list of company names
    company_name_list = [company[0] for company in companies]

    # Create a custom dialog for selecting the company
    company_dialog = CustomDialog(root, "Company", company_name_list)
    root.wait_window(company_dialog)

    selected_company = company_dialog.result

    if selected_company:
        # Fetch distinct car names for the selected company
        cursor.execute("SELECT DISTINCT car_name FROM cars WHERE company = %s", (selected_company,))
        car_names = cursor.fetchall()

        if car_names:
            # Create a list of car names
            car_name_list = [car[0] for car in car_names]

            # Create a custom dialog for selecting the car
            car_dialog = CustomDialog(root, "Car", car_name_list)
            root.wait_window(car_dialog)

            selected_car = car_dialog.result

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

# Function to edit car details
def edit_details():
    # Fetch distinct companies
    cursor.execute("SELECT DISTINCT company FROM cars")
    companies = cursor.fetchall()

    if not companies:
        messagebox.showinfo("No Data", "No companies found. Please add data first.")
        return

    # Create a list of company names
    company_name_list = [company[0] for company in companies]

    # Create a custom dialog for selecting the company
    company_dialog = CustomDialog(root, "Company", company_name_list)
    root.wait_window(company_dialog)

    selected_company = company_dialog.result

    if selected_company:
        # Fetch distinct car names for the selected company
        cursor.execute("SELECT DISTINCT car_name FROM cars WHERE company = %s", (selected_company,))
        car_names = cursor.fetchall()

        if car_names:
            # Create a list of car names
            car_name_list = [car[0] for car in car_names]

            # Create a custom dialog for selecting the car
            car_dialog = CustomDialog(root, "Car", car_name_list)
            root.wait_window(car_dialog)

            selected_car = car_dialog.result

            if selected_car:
                show_edit_options(selected_company, selected_car)

# Create the main window
root = tk.Tk()
root.title("Car Database")

# Load the background image
bg_image = Image.open("background.jpg")  # Replace with your image path
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
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
    button = tk.Button(parent, text=text, command=command, width=int(bg_width * 0.01), height=int(bg_height * 0.005), font=("Helvetica", 12))
    return button

# Create buttons
add_button = create_button(root, "Add", add_details)
add_button.pack(pady=int(bg_height * 0.003))

show_button = create_button(root, "Show", lambda: show_details(cursor))
show_button.pack(pady=int(bg_height * 0.003))

edit_button = create_button(root, "Edit", lambda: edit_details())
edit_button.pack(pady=int(bg_height * 0.003))

delete_car_button = create_button(root, "Delete Car", delete_car_button_click)
delete_car_button.pack(pady=int(bg_height * 0.003))

# Main loop
root.mainloop()


db.close()