import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector

# Function to connect to MySQL database
def connect_db():
    try:
        db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="adarsh",
            database="GST_filling"
        )
        return db_connection
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error connecting to database: {err}")
        return None

# Function to handle login
def login():
    if username_entry.get() == "admin" and password_entry.get() == "admin":
        show_tables()
    else:
        messagebox.showerror("Error", "Invalid username or password")

# Function to show tables
def show_tables():
    tables_window = tk.Toplevel(root)
    tables_window.title("Tables")
    tables_window.geometry("300x300")


    db_connection = connect_db()
    if db_connection:
        cursor = db_connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()

        for table in tables:
            table_name = table[0]
            table_button = tk.Button(tables_window, text=table_name, command=lambda name=table_name: show_table_options(name))
            table_button.pack()

# Function to show table options
def show_table_options(table_name):
    table_options_window = tk.Toplevel(root)
    table_options_window.title(table_name)
    table_options_window.geometry("300x150")

    display_button = tk.Button(table_options_window, text="Display", command=lambda: display_table_content(table_name))
    display_button.pack()

    delete_button = tk.Button(table_options_window, text="Delete", command=lambda: delete_from_table(table_name))
    delete_button.pack()

    insert_button = tk.Button(table_options_window, text="Insert", command=lambda: insert_into_table(table_name))
    insert_button.pack()

    update_button = tk.Button(table_options_window, text="Update", command=lambda: update_table_content(table_name))
    update_button.pack()

# Function to display table content
def display_table_content(table_name):
    # Create a new window to display table content
    table_window = tk.Toplevel(root)
    table_window.title(f"Table Content: {table_name}")

    # Connect to the database
    db_connection = connect_db()
    if db_connection:
        cursor = db_connection.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        table_content = cursor.fetchall()
        cursor.close()

        # Create a frame to hold the table content
        content_frame = tk.Frame(table_window)
        content_frame.pack(pady=10)

        # Add headers
        headers = [description[0] for description in cursor.description]
        for col, header in enumerate(headers):
            header_label = tk.Label(content_frame, text=header, relief=tk.RIDGE, width=15)

            header_label.grid(row=0, column=col, padx=5, pady=5)

        # Add table content
        for row_idx, row in enumerate(table_content):
            for col_idx, value in enumerate(row):
                cell_label = tk.Label(content_frame, text=value, relief=tk.RIDGE, width=15)
                cell_label.grid(row=row_idx + 1, column=col_idx, padx=5, pady=5)

        # Add a scrollbar if needed
        if len(table_content) > 10:  # Adjust the threshold as needed
            scrollbar = tk.Scrollbar(table_window, orient=tk.VERTICAL, command=content_frame.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            content_frame.configure(yscrollcommand=scrollbar.set)


# Function to delete data from table
# Function to delete data from table
def delete_from_table(table_name):
    # Create a new window for delete operation
    delete_window = tk.Toplevel(root)
    delete_window.title(f"Delete from {table_name}")

    # Connect to the database
    db_connection = connect_db()
    if db_connection:
        cursor = db_connection.cursor()

        # Get the primary key column name
        cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
        primary_key_column = cursor.fetchone()[4]

        # Get the primary key value from the user
        tk.Label(delete_window, text=f"Enter {primary_key_column}:").pack(pady=5)
        primary_key_entry = tk.Entry(delete_window)
        primary_key_entry.pack(pady=5)

        def delete_row():
            primary_key_value = primary_key_entry.get()
            if primary_key_value:
                try:
                    # Execute delete query
                    cursor.execute(f"DELETE FROM {table_name} WHERE {primary_key_column} = %s", (primary_key_value,))
                    db_connection.commit()
                    tk.messagebox.showinfo("Success", "Row deleted successfully!")
                    delete_window.destroy()
                except Exception as e:
                    tk.messagebox.showerror("Error", str(e))
                finally:
                    # Close cursor and connection
                    cursor.close()
                    db_connection.close()
            else:
                tk.messagebox.showerror("Error", "Please enter a value!")

        # Delete button
        delete_button = tk.Button(delete_window, text="Delete", command=delete_row)
        delete_button.pack(pady=5)

        # Undo option
        def undo_delete():
            try:
                db_connection.rollback()
                tk.messagebox.showinfo("Undo", "Delete operation undone successfully!")
            except Exception as e:
                tk.messagebox.showerror("Error", str(e))

        undo_button = tk.Button(delete_window, text="Undo", command=undo_delete)
        undo_button.pack(pady=5)

    else:
        tk.messagebox.showerror("Error", "Could not connect to the database.")


# Function to insert data into table
def insert_into_table(table_name):
    # Create a new window for data entry
    insert_window = tk.Toplevel(root)
    insert_window.title(f"Insert into {table_name}")

    # Connect to the database
    db_connection = connect_db()
    if db_connection:
        cursor = db_connection.cursor()

        # Get all column names
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column[0] for column in cursor.fetchall()]

        # Entry fields for each column
        entry_fields = {}
        for column in columns:
            tk.Label(insert_window, text=f"{column}:").pack(pady=5)
            entry = tk.Entry(insert_window)
            entry.pack(pady=5)
            entry_fields[column] = entry

        def insert_row():
            # Get values from entry fields
            values = [entry_fields[column].get() for column in columns]

            # Check if any field is empty
            if any(value == "" for value in values):
                tk.messagebox.showerror("Error", "Please fill in all fields!")
                return

            try:
                # Prepare and execute INSERT query
                query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(columns))})"
                cursor.execute(query, tuple(values))
                db_connection.commit()
                tk.messagebox.showinfo("Success", "New row inserted successfully!")
                insert_window.destroy()
            except Exception as e:
                tk.messagebox.showerror("Error", str(e))
            finally:
                # Close cursor and connection
                cursor.close()
                db_connection.close()

        # Insert button
        insert_button = tk.Button(insert_window, text="Insert", command=insert_row)
        insert_button.pack(pady=10)

    else:
        tk.messagebox.showerror("Error", "Could not connect to the database.")


# Function to update table content
def update_table_content(table_name):
    # Create a new window for update
    update_window = tk.Toplevel(root)
    update_window.title(f"Update {table_name}")

    # Connect to the database
    db_connection = connect_db()
    if db_connection:
        cursor = db_connection.cursor()

        try:
            # Get primary key column name
            cursor.execute(f"SHOW KEYS FROM {table_name} WHERE Key_name = 'PRIMARY'")
            primary_key_column = cursor.fetchone()[4]

            # Get all column names except the primary key column
            cursor.execute(f"SHOW COLUMNS FROM {table_name}")
            columns = [column[0] for column in cursor.fetchall() if column[0] != primary_key_column]

            # Entry fields for primary key and column to update
            primary_key_label = tk.Label(update_window, text=f"{primary_key_column}:")
            primary_key_label.grid(row=0, column=0, padx=5, pady=5)
            primary_key_entry = tk.Entry(update_window)
            primary_key_entry.grid(row=0, column=1, padx=5, pady=5)

            column_var = tk.StringVar()
            column_var.set(columns[0])  # Set default value for OptionMenu

            column_label = tk.Label(update_window, text="Select column to update:")
            column_label.grid(row=1, column=0, padx=5, pady=5)
            column_optionmenu = tk.OptionMenu(update_window, column_var, *columns)
            column_optionmenu.grid(row=1, column=1, padx=5, pady=5)

            new_value_label = tk.Label(update_window, text="Enter new value:")
            new_value_label.grid(row=2, column=0, padx=5, pady=5)
            new_value_entry = tk.Entry(update_window)
            new_value_entry.grid(row=2, column=1, padx=5, pady=5)

            def update_row():
                # Get values from entry fields
                primary_key_value = primary_key_entry.get()
                column_to_update = column_var.get()
                new_value = new_value_entry.get()

                # Check if any field is empty
                if any(value == "" for value in [primary_key_value, new_value]):
                    tk.messagebox.showerror("Error", "Please fill in all fields!")
                    return

                try:
                    # Prepare and execute UPDATE query
                    query = f"UPDATE {table_name} SET {column_to_update} = %s WHERE {primary_key_column} = %s"
                    cursor.execute(query, (new_value, primary_key_value))
                    db_connection.commit()
                    tk.messagebox.showinfo("Success", "Row updated successfully!")
                    update_window.destroy()
                except Exception as e:
                    tk.messagebox.showerror("Error", str(e))
                finally:
                    # Close cursor and connection
                    cursor.close()
                    db_connection.close()

            # Update button
            update_button = tk.Button(update_window, text="Update", command=update_row)
            update_button.grid(row=3, column=0, columnspan=2, pady=10)

        except Exception as e:
            tk.messagebox.showerror("Error", str(e))
            # Close cursor and connection if an exception occurs
            cursor.close()
            db_connection.close()

    else:
        tk.messagebox.showerror("Error", "Could not connect to the database.")


# Main GUI
root = tk.Tk()
root.title("Login")
root.geometry("300x150")

# Username
username_label = tk.Label(root, text="Username:")
username_label.grid(row=0, column=0)
username_entry = tk.Entry(root)
username_entry.grid(row=0, column=1)

# Password
password_label = tk.Label(root, text="Password:")
password_label.grid(row=1, column=0)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=1, column=1)

# Login button
login_button = tk.Button(root, text="Login", command=login)
login_button.grid(row=2, column=0, columnspan=2)

root.mainloop()
