import csv
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import re

# Load college programs from CSV
def load_college_programs():
    programs = {}
    try:
        with open(r'c:\codes\Simple-Student-Info-System-main\college_programs.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                college_code = row[0]
                program_list = row[1:]
                programs[college_code] = program_list
    except FileNotFoundError:
        messagebox.showerror("File Error", "college_programs.csv not found!")
    return programs

# Load college mapping from CSV
def load_college_mapping():
    mapping = {}
    try:
        with open(r'c:\codes\Simple-Student-Info-System-main\college_mapping.csv', mode='r') as file:
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

def autofill_program_code(event):
    selected_program = program_combobox.get()
    if selected_program:
        ProgCode_entry.delete(0, END)
        ProgCode_entry.insert(0, selected_program)

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

    with open(r'c:\codes\Simple-Student-Info-System-main\students.csv', mode='a') as file:
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

    # combobox for college selection
    Label(delete_college_window, text="Select College to Delete:", font=("Arial", 12)).pack(pady=10)
    college_combobox = ttk.Combobox(delete_college_window, values=list(college_mapping.keys()), state="readonly", font=("Arial", 10))
    college_combobox.pack(pady=10)

    # delete selected
    def delete_college():
        selected_college = college_combobox.get()
        if not selected_college:
            messagebox.showwarning("Selection Error", "No college selected!")
            return

        # Get the college code for the selected college
        college_code = college_mapping.get(selected_college)

        if not college_code:
            messagebox.showerror("Error", "Selected college does not exist!")
            return

        # Remove the college from the mapping
        del college_mapping[selected_college]

        # Remove the programs associated with the college
        if college_code in college_programs:
            del college_programs[college_code]

        # Remove students associated with the college from the CSV file
        try:
            with open(r'c:\codes\Simple-Student-Info-System-main\students.csv', 'r', newline='') as file:
                rows = list(csv.reader(file))

            with open(r'c:\codes\Simple-Student-Info-System-main\students.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                for row in rows:
                    # Ensure the row has enough columns before accessing index 7
                    if len(row) > 7 and row[7] != college_code:  # College Code is in the 8th column (index 7)
                        writer.writerow(row)
        except FileNotFoundError:
            messagebox.showerror("File Error", "students.csv not found!")
            return

        # Remove students associated with the college from the Treeview
        for child in student_info.get_children():
            values = student_info.item(child, 'values')
            # Ensure the row has enough columns before accessing index 7
            if len(values) > 7 and values[7] == college_code:  # College Code is in the 8th column (index 7)
                student_info.delete(child)

        # Update the college dropdowns
        CollName_entry['values'] = list(college_mapping.keys())

        # Show success message and close the window
        messagebox.showinfo("Success", f"College '{selected_college}' and its associated data have been deleted.")
        delete_college_window.destroy()

    # Add a delete button
    delete_button = ttk.Button(delete_college_window, text="Delete College", command=delete_college, style="TButton")
    delete_button.pack(pady=20)

def load_from_csv():
    try:
        with open(r'c:\codes\Simple-Student-Info-System-main\students.csv', mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                student_info.insert('', 'end', values=row)
    except FileNotFoundError:
        pass

def delete_selected():
    selected_item = student_info.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "No item selected")
        return

    for item in selected_item:
        student_info.delete(item)

    with open(r'c:\codes\Simple-Student-Info-System-main\students.csv', mode='r') as file:
        rows = list(csv.reader(file))

    with open(r'c:\codes\Simple-Student-Info-System-main\students.csv', mode='r') as file:
        writer = csv.writer(file)
        for row in rows:
            if not any(row == student_info.item(item, 'values') for item in selected_item):
                writer.writerow(row)

def update_search_suggestions(event):
    search_term = search_var.get().lower()

    matching_items = []
    for child in student_info.get_children():
        values = student_info.item(child, 'values')
        if any(search_term in str(value).lower() for value in values):
            matching_items.append(child)

    for item in student_info.get_children():
        student_info.detach(item)

    if search_term == "":
        load_from_csv()
    else:
        for item in matching_items:
            student_info.reattach(item, '', 'end')
            student_info.selection_set(item)
            student_info.see(item)
def sort_by_column(column):
    try:

        column_index = student_info["columns"].index(column)

        # Extract data from the Treeview, ensuring no out-of-range errors
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

root = Tk()

root.title("Student System Information")
root.geometry("1450x500")

frame = Frame(root, bg="#f0f0f0", bd=5, relief=RIDGE)
frame.place(width=1450, height=500)

# variables

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

StuInfo = LabelFrame(frame, text="Student Information", font=("Arial", 12, "bold"), bg="#e0e0e0", bd=5, relief=RIDGE)
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
StuColl = LabelFrame(frame, text="College Information", font=("Arial", 12, "bold"), bg="#e0e0e0", bd=5, relief=RIDGE)
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
StuProg = LabelFrame(frame, text="Program Information", font=("Arial", 12, "bold"), bg="#e0e0e0", bd=5, relief=RIDGE)
StuProg.grid(row=2, column=0, sticky="news")

program_label = Label(StuProg, text="Select Program:", font=("Arial", 10))
program_label.grid(row=0, column=0)
ProgCode_label = Label(StuProg, text="Program Code", font=("Arial", 10))
ProgCode_label.grid(row=1, column=0)
Year_label = Label(StuProg, text="Year Level", font=("Arial", 10))
Year_label.grid(row=2, column=0)

# Program Info
program_combobox = ttk.Combobox(StuProg, values=[], textvariable=progcode_var, font=("Arial", 10), state='readonly')
program_combobox.grid(row=0, column=1)
program_combobox.bind("<<ComboboxSelected>>", autofill_program_code)
ProgCode_entry = Entry(StuProg, textvariable=progcode_var, font=("Arial", 10))
ProgCode_entry.grid(row=1, column=1)
Year_entry = ttk.Combobox(StuProg, values=["1", "2", "3", "4"], textvariable=year_var, font=("Arial", 10), state='readonly')
Year_entry.grid(row=2, column=1)

for widget in StuProg.winfo_children():
    widget.grid_configure(padx=10, pady=10)

# Buttons
button_save = ttk.Button(frame, text="Save", command=save_to_csv, style="TButton")
button_save.grid(row=3, column=0, sticky="news", padx=50, pady=10)

Saved_student = LabelFrame(frame, text="Saved Students", font=("Arial", 12, "bold"), bg="#e0e0e0", bd=5, relief=RIDGE)
Saved_student.place(x=600, y=0, width=840, height=400)
Search_frame = Frame(Saved_student, bg="#e0e0e0")
Search_frame.pack(side=TOP, fill=X)

search_entry = Entry(Search_frame, textvariable=search_var, font=("Arial", 10))
search_entry.grid(row=0, column=0, padx=20)
search_entry.bind('<KeyRelease>', update_search_suggestions)

# Button for college delete window
button_delete_college = ttk.Button(Search_frame, text="Delete College", command=lambda: open_delete_college_window(), style="TButton")
button_delete_college.grid(row=0, column=5, padx=10)

button_delete = ttk.Button(Search_frame, text="Delete", command=delete_selected, style="TButton")
button_delete.grid(row=0, column=1)

button_sort_id = ttk.Button(Search_frame, text="Sort by ID Number", command=lambda: sort_by_column("ID Number"), style="TButton")
button_sort_id.grid(row=0, column=2)

button_sort_fname = ttk.Button(Search_frame, text="Sort by First Name", command=lambda: sort_by_column("First Name"), style="TButton")
button_sort_fname.grid(row=0, column=3)

button_sort_lname = ttk.Button(Search_frame, text="Sort by Last Name", command=lambda: sort_by_column("Last Name"), style="TButton")
button_sort_lname.grid(row=0, column=4)

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