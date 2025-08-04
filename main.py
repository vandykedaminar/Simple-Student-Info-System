import csv
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import re

# Load college programs from CSV
def load_college_programs():
    programs = {}
    try:
        with open(r'./college_programs.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                college_code = row[0]
                program_list = row[1:]
                programs[college_code] = program_list
    except FileNotFoundError:
        messagebox.showerror("File Error", "college_programs.csv not found!")
    return programs


def load_college_mapping():
    mapping = {}
    try:
        with open(r'./college_mapping.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                college_name = row[0]
                college_code = row[1]
                mapping[college_name] = college_code
    except FileNotFoundError:
        messagebox.showerror("File Error", "college_mapping.csv not found!")
    return mapping

# Load data from CSV files
college_programs = load_college_programs()
college_mapping = load_college_mapping()

def autofill_code(event):
    selected_college = CollName_entry.get()
    if selected_college in college_mapping:
        CollCode_entry.delete(0, END)
        CollCode_entry.insert(0, college_mapping[selected_college])
        program_combobox['values'] = college_programs.get(college_mapping[selected_college], [])

def open_edit_student_window():
    selected_item = student_info.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "No student selected!")
        return

    student_data = student_info.item(selected_item[0], 'values')

    edit_window = Toplevel(root)
    edit_window.title("Edit Student")
    edit_window.geometry("400x600")

    edit_idnum_var = StringVar(value=student_data[0])
    edit_fname_var = StringVar(value=student_data[1])
    edit_lname_var = StringVar(value=student_data[2])
    edit_sex_var = StringVar(value=student_data[3])
    edit_progcode_var = StringVar(value=student_data[4])
    edit_year_var = IntVar(value=student_data[5])
    edit_collname_var = StringVar(value=student_data[6])
    edit_collcode_var = StringVar(value=student_data[7])

    Label(edit_window, text="ID Number:").pack(pady=5)
    Entry(edit_window, textvariable=edit_idnum_var, state="readonly").pack(pady=5)

    Label(edit_window, text="First Name:").pack(pady=5)
    Entry(edit_window, textvariable=edit_fname_var).pack(pady=5)

    Label(edit_window, text="Last Name:").pack(pady=5)
    Entry(edit_window, textvariable=edit_lname_var).pack(pady=5)

    Label(edit_window, text="Sex:").pack(pady=5)
    ttk.Combobox(edit_window, values=["F", "M"], textvariable=edit_sex_var, state="readonly").pack(pady=5)

    Label(edit_window, text="Year Level:").pack(pady=5)
    ttk.Combobox(edit_window, values=["1", "2", "3", "4"], textvariable=edit_year_var, state="readonly").pack(pady=5)

    Label(edit_window, text="College Name:").pack(pady=5)
    college_combobox = ttk.Combobox(edit_window, values=list(college_mapping.keys()), textvariable=edit_collname_var, state="readonly")
    college_combobox.pack(pady=5)

    Label(edit_window, text="College Code:").pack(pady=5)
    coll_code_entry = Entry(edit_window, textvariable=edit_collcode_var, state="readonly")
    coll_code_entry.pack(pady=5)

    # --- MODIFICATION START ---
    Label(edit_window, text="Program Name:").pack(pady=5)
    
    # Get initial programs for the student's current college
    initial_programs = college_programs.get(student_data[7], []) # Use college code (index 7)
    
    # Create the program Combobox
    program_combobox_edit = ttk.Combobox(edit_window, textvariable=edit_progcode_var, values=initial_programs, state="readonly")
    program_combobox_edit.pack(pady=5)

    def autofill_edit_college_code_and_programs(event):
        selected_college = edit_collname_var.get()
        if selected_college in college_mapping:
            new_college_code = college_mapping[selected_college]
            edit_collcode_var.set(new_college_code)
            
            # Update the program combobox with programs from the new college
            programs_for_new_college = college_programs.get(new_college_code, [])
            program_combobox_edit['values'] = programs_for_new_college
            
            # Clear current program selection to force user to choose a new, valid one
            edit_progcode_var.set("")
        else:
            # Clear everything if college is not found
            edit_collcode_var.set("")
            program_combobox_edit['values'] = []
            edit_progcode_var.set("")


    college_combobox.bind("<<ComboboxSelected>>", autofill_edit_college_code_and_programs)
    # --- MODIFICATION END ---
    
    def save_changes():
        # Get all current values from the form variables
        updated_values = (
            edit_idnum_var.get(),
            edit_fname_var.get(),
            edit_lname_var.get(),
            edit_sex_var.get(),
            edit_progcode_var.get(),
            edit_year_var.get(),
            edit_collname_var.get(),
            edit_collcode_var.get()
        )

        # Check if a program was selected
        if not updated_values[4]:
            messagebox.showerror("Input Error", "Please select a program for the student.")
            return

        # Update the Treeview
        student_info.item(selected_item[0], values=updated_values)

        # Update the CSV file
        try:
            with open(r'students.csv', mode='r', newline='') as file:
                rows = list(csv.reader(file))
        except FileNotFoundError:
            messagebox.showerror("File Error", "students.csv not found!")
            return

        with open(r'students.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in rows:
                # Find the row by ID number (which is read-only and unique)
                if row and row[0] == student_data[0]:
                    writer.writerow(list(updated_values))
                else:
                    writer.writerow(row)
        
        messagebox.showinfo("Success", "Student information updated successfully!")
        edit_window.destroy()

    Button(edit_window, text="Save Changes", command=save_changes).pack(pady=20)
def save_to_csv():
    idnum = idnum_var.get()
    fname = fname_var.get()
    lname = lname_var.get()
    sex = sex_var.get()
    progcode = progcode_var.get()
    year = year_var.get()
    collname = collname_var.get()
    collcode = collcode_var.get()

    if not (idnum and fname and lname and sex and progcode and year and collname and collcode):
        messagebox.showwarning("Input Error", "All fields must be filled out")
        return

    with open(r'students.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([idnum, fname, lname, sex, progcode, year, collname, collcode])

    student_info.insert('', 'end', values=(idnum, fname, lname, sex, progcode, year, collname, collcode))

    idnum_var.set("")
    fname_var.set("")
    lname_var.set("")
    sex_var.set("")
    progcode_var.set("")
    year_var.set("")
    collname_var.set("")
    collcode_var.set("")

def open_delete_college_window():
    delete_college_window = Toplevel(root)
    delete_college_window.title("Delete College")
    delete_college_window.geometry("400x300")

    Label(delete_college_window, text="Select College to Delete:", font=("Arial", 12)).pack(pady=10)
    college_combobox = ttk.Combobox(delete_college_window, values=list(college_mapping.keys()), state="readonly", font=("Arial", 10))
    college_combobox.pack(pady=10)

    def delete_college():
        selected_college = college_combobox.get()
        if not selected_college:
            messagebox.showwarning("Selection Error", "No college selected!")
            return

        college_code = college_mapping.get(selected_college)

        if not college_code:
            messagebox.showerror("Error", "Selected college does not exist!")
            return

        # Remove from in-memory mappings
        del college_mapping[selected_college]
        if college_code in college_programs:
            del college_programs[college_code]

        # Remove from college_mapping.csv
        try:
            with open(r'./college_mapping.csv', 'r', newline='') as file:
                rows = list(csv.reader(file))
            with open(r'./college_mapping.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                for row in rows:
                    if len(row) >= 2 and not (row[0] == selected_college and row[1] == college_code):
                        writer.writerow(row)
        except Exception as e:
            messagebox.showerror("File Error", f"Error updating college_mapping.csv: {e}")
            return

        # Remove from college_programs.csv
        try:
            with open(r'./college_programs.csv', 'r', newline='') as file:
                rows = list(csv.reader(file))
            with open(r'./college_programs.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                for row in rows:
                    if len(row) >= 1 and row[0] != college_code:
                        writer.writerow(row)
        except Exception as e:
            messagebox.showerror("File Error", f"Error updating college_programs.csv: {e}")
            return

        # Update students associated with the deleted college to have null/blank college info
        try:
            with open(r'students.csv', 'r', newline='') as file:
                rows = list(csv.reader(file))
            
            updated_rows = []
            for row in rows:
                if len(row) > 7 and row[7] == college_code:
                    # Clear the College Name (index 6) and College Code (index 7)
                    row[6] = "" 
                    row[7] = "" 
                updated_rows.append(row)

            with open(r'students.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(updated_rows)
        except FileNotFoundError:
            messagebox.showerror("File Error", "students.csv not found!")
            return

        student_info.delete(*student_info.get_children())
        load_from_csv()

        CollName_entry['values'] = list(college_mapping.keys())

        messagebox.showinfo("Success", f"College '{selected_college}' has been deleted. Associated students' college information has been cleared.")
        delete_college_window.destroy()

    delete_button = ttk.Button(delete_college_window, text="Delete College", command=delete_college, style="TButton")
    delete_button.pack(pady=20)


def load_from_csv():
    # Clear existing treeview items before loading
    for item in student_info.get_children():
        student_info.delete(item)
    try:
        with open(r'students.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if any(row):  
                    student_info.insert('', 'end', values=row)
    except FileNotFoundError:
        messagebox.showerror("File Error", "students.csv not found!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while loading students: {e}")
        
def delete_selected():
    selected_items = student_info.selection()
    if not selected_items:
        messagebox.showwarning("Selection Error", "No item selected")
        return

    # Get values of selected items before deleting from treeview
    items_to_delete_values = [student_info.item(item, 'values') for item in selected_items]

    for item in selected_items:
        student_info.delete(item)

    # Read all rows from the CSV
    with open(r'students.csv', mode='r', newline='') as file:
        rows = list(csv.reader(file))

    # Write back only the rows that were not selected for deletion
    with open(r'students.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            # The values from the treeview are strings, so we compare as a tuple of strings
            if tuple(map(str, row)) not in items_to_delete_values:
                writer.writerow(row)


def update_search_suggestions(event):
    search_term = search_var.get().lower()

    # Clear current treeview
    for item in student_info.get_children():
        student_info.delete(item)

    # If search is empty, reload all data
    if search_term == "":
        load_from_csv()
        return

    # Otherwise, filter and show matching data
    try:
        with open(r'students.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                if any(row) and any(search_term in str(value).lower() for value in row):
                    student_info.insert('', 'end', values=row)
    except FileNotFoundError:
        messagebox.showerror("File Error", "students.csv not found!")

def sort_by_column(column):
    try:

        column_index = student_info["columns"].index(column)

        
        data = []
        for child in student_info.get_children(''):
            values = student_info.item(child, 'values')
            if len(values) > column_index:
                data.append((values[column_index].strip().lower(), child))
            else:
                data.append(("", child))

        data.sort()

        for index, (value, child) in enumerate(data):
            student_info.move(child, '', index)

    except ValueError:
        messagebox.showerror("Error", f"Column '{column}' not found in Treeview.")

def validate_idnum(new_value):
    pattern = re.compile(r'^\d{0,4}(-\d{0,4})?$')
    return pattern.match(new_value) is not None


def open_add_college_window():
    add_college_window = Toplevel(root)
    add_college_window.title("Add College")
    add_college_window.geometry("400x400")

    new_college_name_var = StringVar()
    new_college_code_var = StringVar()
    new_programs_var = StringVar()

    Label(add_college_window, text="College Name:").pack(pady=5)
    Entry(add_college_window, textvariable=new_college_name_var).pack(pady=5)

    Label(add_college_window, text="College Code:").pack(pady=5)
    Entry(add_college_window, textvariable=new_college_code_var).pack(pady=5)

    Label(add_college_window, text="Programs (comma-separated):").pack(pady=5)
    Entry(add_college_window, textvariable=new_programs_var).pack(pady=5)

    def save_new_college():
        college_name = new_college_name_var.get().strip()
        college_code = new_college_code_var.get().strip()
        programs = new_programs_var.get().strip()

        if not college_name or not college_code or not programs:
            messagebox.showerror("Input Error", "All fields are required!")
            return

       
        try:
            with open(r'./college_programs.csv', mode='r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0] == college_code:
                        messagebox.showerror("Input Error", "College code already exists in college_programs.csv!")
                        return
        except FileNotFoundError:
            pass  

        try:
            with open(r'./college_mapping.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([college_name, college_code])
        except Exception as e:
            messagebox.showerror("File Error", f"Error writing to college_mapping.csv: {e}")
            return

        try:
            with open(r'./college_programs.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([college_code] + programs.split(','))
        except Exception as e:
            messagebox.showerror("File Error", f"Error writing to college_programs.csv: {e}")
            return
        
        college_mapping[college_name] = college_code
        college_programs[college_code] = programs.split(',')

        CollName_entry['values'] = list(college_mapping.keys())

        messagebox.showinfo("Success", "College and programs added successfully!")
        add_college_window.destroy()

    Button(add_college_window, text="Save College", command=save_new_college).pack(pady=20)

# ...existing code...
def open_edit_college_window():
    edit_college_window = Toplevel(root)
    edit_college_window.title("Edit College")
    edit_college_window.geometry("400x400")

    
    selected_college_var = StringVar()
    new_college_name_var = StringVar()
    new_college_code_var = StringVar()
    new_programs_var = StringVar()

    
    Label(edit_college_window, text="Select College to Edit:").pack(pady=5)
    college_combobox = ttk.Combobox(edit_college_window, values=list(college_mapping.keys()), textvariable=selected_college_var, state="readonly")
    college_combobox.pack(pady=5)

    Label(edit_college_window, text="New College Name:").pack(pady=5)
    Entry(edit_college_window, textvariable=new_college_name_var).pack(pady=5)

    Label(edit_college_window, text="New College Code:").pack(pady=5)
    Entry(edit_college_window, textvariable=new_college_code_var).pack(pady=5)

    Label(edit_college_window, text="Add Programs (comma-separated):").pack(pady=5)
    Entry(edit_college_window, textvariable=new_programs_var).pack(pady=5)

    # Autofill current college details when a college is selected
    def autofill_college_details(event):
        selected_college = selected_college_var.get()
        if selected_college in college_mapping:
            new_college_name_var.set(selected_college)
            new_college_code_var.set(college_mapping[selected_college])

    college_combobox.bind("<<ComboboxSelected>>", autofill_college_details)

    
    def save_college_changes():
        selected_college = selected_college_var.get()
        new_college_name = new_college_name_var.get().strip()
        new_college_code = new_college_code_var.get().strip()
        new_programs = new_programs_var.get().strip()

        if not selected_college:
            messagebox.showwarning("Selection Error", "No college selected!")
            return

        if not new_college_name or not new_college_code:
            messagebox.showerror("Input Error", "College name and code cannot be empty!")
            return

        
        old_college_code = college_mapping[selected_college]
        del college_mapping[selected_college]
        college_mapping[new_college_name] = new_college_code

        
        if old_college_code in college_programs:
            existing_programs = college_programs[old_college_code]
            new_program_list = existing_programs + new_programs.split(',') if new_programs else existing_programs
            college_programs[new_college_code] = list(set(new_program_list))  # Remove duplicates
            del college_programs[old_college_code]

        
        try:
            
            with open(r'./college_mapping.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                for college_name, college_code in college_mapping.items():
                    writer.writerow([college_name, college_code])

            
            with open(r'./college_programs.csv', mode='w', newline='') as file:
                writer = csv.writer(file)
                for college_code, programs in college_programs.items():
                    writer.writerow([college_code] + programs)
        except Exception as e:
            messagebox.showerror("File Error", f"Error updating CSV files: {e}")
            return
            

        
        CollName_entry['values'] = list(college_mapping.keys())

        messagebox.showinfo("Success", "College information updated successfully!")
        edit_college_window.destroy()

    Button(edit_college_window, text="Save Changes", command=save_college_changes).pack(pady=20)

root = Tk()

root.title("Student System Information")
root.geometry("1450x500")

frame = Frame(root, bg="white", bd=5, relief=RIDGE)
frame.place(width=1450, height=500)



idnum_var = StringVar()
fname_var = StringVar()
lname_var = StringVar()
sex_var = StringVar()
progcode_var = StringVar()
year_var = IntVar()
collname_var = StringVar()
collcode_var = StringVar()
search_var = StringVar()

# Saving student info

StuInfo = LabelFrame(frame, text="Student Information", font=("Arial", 12, "bold"), bg="#e0e0e0",fg="#800000", bd=5, relief=RIDGE)
StuInfo.grid(row=0, column=0, sticky="news")

idnum_label = Label(StuInfo, text="ID Number", font=("Arial", 10))
idnum_label.grid(row=0, column=0)
fname_label = Label(StuInfo, text="First Name", font=("Arial", 10))
fname_label.grid(row=0, column=1)
lname_label = Label(StuInfo, text="Last Name", font=("Arial", 10))
lname_label.grid(row=0, column=2)
sex_label = Label(StuInfo, text="Sex", font=("Arial", 10))
sex_label.grid(row=2, column=0)

# student info entry

vcmd = (root.register(validate_idnum), '%P')
idnum_entry = Entry(StuInfo, textvariable=idnum_var, font=("Arial", 10), validate='key', validatecommand=vcmd)
idnum_entry.grid(row=1, column=0)
fname_entry = Entry(StuInfo, textvariable=fname_var, font=("Arial", 10))
fname_entry.grid(row=1, column=1)
lname_entry = Entry(StuInfo, textvariable=lname_var, font=("Arial", 10))
lname_entry.grid(row=1, column=2)
Gender_entry = ttk.Combobox(StuInfo, values=["F", "M"], textvariable=sex_var, font=("Arial", 10), state='readonly')
Gender_entry.grid(row=3, column=0)

for widget in StuInfo.winfo_children():
    widget.grid_configure(padx=10, pady=10)

# saving college info
StuColl = LabelFrame(frame, text="College Information", font=("Arial", 12, "bold"), bg="#e0e0e0",fg="#800000", bd=5, relief=RIDGE)
StuColl.grid(row=1, column=0, sticky="news")

CollName_label = Label(StuColl, text="College Name:", font=("Arial", 10))
CollName_label.grid(row=0, column=0)
CollCode_label = Label(StuColl, text="College Code:", font=("Arial", 10))
CollCode_label.grid(row=0, column=2)

# college info entry
CollName_entry = ttk.Combobox(StuColl, values=list(college_mapping.keys()), textvariable=collname_var, font=("Arial", 10), state='readonly')
CollName_entry.grid(row=0, column=1)
CollName_entry.bind("<<ComboboxSelected>>", autofill_code)
CollCode_entry = Entry(StuColl, textvariable=collcode_var, font=("Arial", 10))
CollCode_entry.grid(row=0, column=3)

for widget in StuColl.winfo_children():
    widget.grid_configure(padx=10, pady=10)

# Saving Program Info
StuProg = LabelFrame(frame, text="Program Information", font=("Arial", 12, "bold"), bg="#e0e0e0",fg="#800000", bd=5, relief=RIDGE)
StuProg.grid(row=2, column=0, sticky="news")

program_label = Label(StuProg, text="Select Program:", font=("Arial", 10))
program_label.grid(row=0, column=0)

Year_label = Label(StuProg, text="Year Level", font=("Arial", 10))
Year_label.grid(row=2, column=0)

# Program Info
program_combobox = ttk.Combobox(StuProg, values=[], textvariable=progcode_var, font=("Arial", 10), state='readonly')
program_combobox.grid(row=0, column=1)
Year_entry = ttk.Combobox(StuProg, values=["1", "2", "3", "4"], textvariable=year_var, font=("Arial", 10), state='readonly')
Year_entry.grid(row=2, column=1)

for widget in StuProg.winfo_children():
    widget.grid_configure(padx=10, pady=10)

# Buttons
button_save = ttk.Button(frame, text="Save", command=save_to_csv, style="TButton")
button_save.grid(row=3, column=0, sticky="news", padx=50, pady=10)



Saved_student = LabelFrame(frame, text="Saved Students", font=("Arial", 12, "bold"), bg="#e0e0e0",fg="#800000", bd=5, relief=RIDGE)
Saved_student.place(x=600, y=0, width=840, height=400)
Search_frame = Frame(Saved_student, bg="#e0e0e0")
Search_frame.pack(side=TOP, fill=X)

search_entry = Entry(Search_frame, textvariable=search_var, font=("Arial", 10))
search_entry.grid(row=0, column=0, padx=20)
search_entry.bind('<KeyRelease>', update_search_suggestions)


edit_menu_button = Menubutton(Search_frame, text="Edit", relief=RAISED, font=("Arial", 10))
edit_menu_button.grid(row=0, column=3, padx=10)


edit_menu = Menu(edit_menu_button, tearoff=0)
edit_menu_button.config(menu=edit_menu)


edit_menu.add_command(label="Edit Student", command=open_edit_student_window)
edit_menu.add_command(label="Edit College", command=open_edit_college_window)
edit_menu.add_command(label="Add College", command=open_add_college_window)


delete_menu_button = Menubutton(Search_frame, text="Delete", relief=RAISED, font=("Arial", 10))
delete_menu_button.grid(row=0, column=1, padx=10)


delete_menu = Menu(delete_menu_button, tearoff=0)
delete_menu_button.config(menu=delete_menu)


delete_menu.add_command(label="Delete Student", command=delete_selected)
delete_menu.add_command(label="Delete College", command=open_delete_college_window)


sort_menu_button = Menubutton(Search_frame, text="Sort", relief=RAISED, font=("Arial", 10))
sort_menu_button.grid(row=0, column=2, padx=10)


sort_menu = Menu(sort_menu_button, tearoff=0)
sort_menu_button.config(menu=sort_menu)


sort_menu.add_command(label="Sort by ID Number", command=lambda: sort_by_column("ID Number"))
sort_menu.add_command(label="Sort by First Name", command=lambda: sort_by_column("First Name"))
sort_menu.add_command(label="Sort by Last Name", command=lambda: sort_by_column("Last Name"))


Data_frame = Frame(Saved_student, bg="#f0f0f0", bd=5, relief=RIDGE)
Data_frame.pack(side=TOP, fill=BOTH, expand=True)

yscroll = Scrollbar(Data_frame, orient=VERTICAL)
xscroll = Scrollbar(Data_frame, orient=HORIZONTAL)

student_info = ttk.Treeview(Data_frame, columns=("ID Number", "First Name", "Last Name", "Sex", "Program Code", "Year Level", "College Name", "College Code"), yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
yscroll.config(command=student_info.yview)
xscroll.config(command=student_info.xview)

yscroll.pack(side=RIGHT, fill=Y)
xscroll.pack(side=BOTTOM, fill=X)
student_info.pack(fill=BOTH, expand=True)

student_info.heading("ID Number", text="ID Number")
student_info.heading("First Name", text="First Name")
student_info.heading("Last Name", text="Last Name")
student_info.heading("Sex", text="Sex")
student_info.heading("Program Code", text="Program Code")
student_info.heading("Year Level", text="Year Level")
student_info.heading("College Name", text="College Name")
student_info.heading("College Code", text="College Code")

student_info['show'] = 'headings'

load_from_csv()

root.mainloop()