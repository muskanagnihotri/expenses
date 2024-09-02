import mysql.connector
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from prettytable import PrettyTable

# Database connection
def database_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="exp",
        password="muskan@123",
        database="expenses"
    )
    return connection

# Add expense
def add_expense(date, category, amount, gender, description):
    conn = database_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, category, amount, gender, description) VALUES (%s, %s, %s, %s, %s)",
                   (date, category, amount, gender, description))
    conn.commit()
    cursor.close()
    conn.close()

# View expenses

def view_expense():
    conn = database_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses")
    rec = cur.fetchall()
    
    table = PrettyTable()
    table.field_names = ["ID", "Date", "Category", "Amount ($)", "Gender", "Description"]
    
    for row in rec:
        try:
            amount = float(row[3])
            amount_str = f"{amount:,.2f}"
        except ValueError:
            amount_str = "N/A"  # Handle cases where amount is not numeric
        
        table.add_row([row[0], row[1], row[2], amount_str, row[4], row[5]])
    
    cur.close()
    conn.close()
    
    table.align["Date"] = "l"
    table.align["Category"] = "l"
    table.align["Amount ($)"] = "r"
    table.align["Gender"] = "l"
    table.align["Description"] = "l"
    table.horizontal_char = '*'
    table.vertical_char = '|'
    table.junction_char = '+'
    
    print(table)


# Generate summary
# Generate summary
def generate_summary():
    conn = database_connection()
    cur = conn.cursor()
    
    # Total expenses
    cur.execute("SELECT SUM(amount) FROM expenses")
    total_expense = cur.fetchone()[0]
    
    # Expenses by category
    cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    expense_by_category = cur.fetchall()
    
    # Maximum expense
    cur.execute("SELECT * FROM expenses ORDER BY amount DESC LIMIT 1")
    max_expense = cur.fetchone()
    
    # Minimum expense
    cur.execute("SELECT * FROM expenses ORDER BY amount ASC LIMIT 1")
    min_expense = cur.fetchone()
    
    cur.close()
    conn.close()
    
    # Display the summary in a readable format
    print("\n" + "="*40)
    print("   📊 Expense Summary Report 📊")
    print("="*40)
    
    # Total expenses
    if total_expense is not None:
        print(f"Total Expenses: ${total_expense:,.2f}")
    else:
        print("Total Expenses: N/A")
    
    # Expenses by category
    print("\nExpenses by Category:")
    table_category = PrettyTable()
    table_category.field_names = ["Category", "Amount ($)"]
    for category, amount in expense_by_category:
        table_category.add_row([category, f"{float(amount):,.2f}" if amount else "N/A"])
    print(table_category)
    
    # Maximum expense
    print("\nMaximum Expense:")
    if max_expense:
        table_max = PrettyTable()
        table_max.field_names = ["ID", "Date", "Category", "Amount ($)", "Gender", "Description"]
        try:
            amount = float(max_expense[3])
            amount_str = f"{amount:,.2f}"
        except ValueError:
            amount_str = "N/A"
        table_max.add_row([max_expense[0], max_expense[1], max_expense[2], amount_str, max_expense[4], max_expense[5]])
        print(table_max)
    else:
        print("No expenses found.")
    
    # Minimum expense
    print("\nMinimum Expense:")
    if min_expense:
        table_min = PrettyTable()
        table_min.field_names = ["ID", "Date", "Category", "Amount ($)", "Gender", "Description"]
        try:
            amount = float(min_expense[3])
            amount_str = f"{amount:,.2f}"
        except ValueError:
            amount_str = "N/A"
        table_min.add_row([min_expense[0], min_expense[1], min_expense[2], amount_str, min_expense[4], min_expense[5]])
        print(table_min)
    else:
        print("No expenses found.")

# Update expense
def update_expense(expense_id, date=None, category=None, amount=None, gender=None, description=None):
    conn = database_connection()
    cur = conn.cursor()

    if date:
        cur.execute("UPDATE expenses SET date = %s WHERE id = %s", (date, expense_id))
    if category:
        cur.execute("UPDATE expenses SET category = %s WHERE id = %s", (category, expense_id))
    if amount:
        cur.execute("UPDATE expenses SET amount = %s WHERE id = %s", (amount, expense_id))
    if gender:
        cur.execute("UPDATE expenses SET gender = %s WHERE id = %s", (gender, expense_id))
    if description:
        cur.execute("UPDATE expenses SET description = %s WHERE id = %s", (description, expense_id))

    conn.commit()
    cur.close()
    conn.close()

# Delete expense
def delete_expense(expense_id):
    conn = database_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=%s", (expense_id,))
    conn.commit()
    cur.close()
    conn.close()

# View expense by category
def view_expense_by_category(category):
    conn = database_connection()
    cur = conn.cursor()
    cur.execute("SELECT date, category, amount, gender, description FROM expenses WHERE category=%s", (category,))
    expense_by_category = cur.fetchall()
    
    table = PrettyTable()
    table.field_names = ["Date", "Category", "Amount ($)", "Gender", "Description"]
    
    for row in expense_by_category:
        table.add_row([row[0], row[1], f"{float(row[2]):,.2f}", row[3], row[4]])
    
    cur.close()
    conn.close()
    
    print("\n" + "="*40)
    print(f"   📂 Expenses for Category: {category} 📂")
    print("="*40)
    print(table)

# View expense by date range
def view_expense_by_date(start_date, end_date):
    conn = database_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, date, category, amount, gender, description FROM expenses WHERE date BETWEEN %s AND %s", (start_date, end_date))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Display the expenses in a readable format
    print(f"\nExpenses from {start_date} to {end_date}:")
    table = PrettyTable()
    table.field_names = ["ID", "Date", "Category", "Amount ($)", "Gender", "Description"]
    for row in rows:
        try:
            amount = float(row[3])
            amount_str = f"{amount:,.2f}"
        except ValueError:
            amount_str = "N/A"
        table.add_row([row[0], row[1], row[2], amount_str, row[4], row[5]])
    print(table)


# Monthly expense
def monthly_expense():
    conn = database_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT YEAR(date) AS year, MONTH(date) AS month, SUM(amount) AS total_amount FROM expenses GROUP BY year, month ORDER BY year, month")
    monthly_expenses = cur.fetchall()
    
    total_expense = sum(row[2] for row in monthly_expenses)
    average_expense = total_expense / len(monthly_expenses) if monthly_expenses else 0
    
    table = PrettyTable()
    table.field_names = ["Year", "Month", "Total Amount ($)"]
    
    for row in monthly_expenses:
        table.add_row([row[0], f"{row[1]:02d}", f"{float(row[2]):,.2f}"])
    
    cur.close()
    conn.close()
    
    print("\n" + "="*40)
    print("   📅 Monthly Expense Summary 📅")
    print("="*40)
    print(table)
    print(f"\nTotal Expense: ${total_expense:,.2f}")
    print(f"Average Monthly Expense: ${average_expense:,.2f}")

# Load expenses to DataFrame
def load_expenses_to_dataframe():
    conn = database_connection()
    query = "SELECT * FROM expenses"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Visualize expenses
def visualize_expenses():
    df = load_expenses_to_dataframe()
    way = input("Choose 'A' for Category or 'B' for Month: ").strip().upper()
    
    if way == "A":
        expenses_by_category = df.groupby('category')['amount'].sum()
        plt.figure(figsize=(10, 6))
        expenses_by_category.plot(kind='bar', title='Expenses by Category', rot=45)
        plt.xlabel('Category')
        plt.ylabel('Total Amount ($)')
        plt.tight_layout()
        plt.show()
    
    elif way == "B":
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        expenses_by_month = df.groupby('month')['amount'].sum()
        plt.figure(figsize=(10, 6))
        expenses_by_month.plot(kind='line', title='Expenses Over Time')
        plt.xlabel('Month')
        plt.ylabel('Total Amount ($)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    else:
        print("❗ Invalid option. Please enter 'A' or 'B'.")

# Analyze expenses
def analyze_expenses():
    df = load_expenses_to_dataframe()
    
    total_expenses = df['amount'].sum()
    mean_expense = df['amount'].mean()
    median_expense = df['amount'].median()

    print("\n" + "="*40)
    print(" 📊 Expense Analysis Report 📊 ")
    print("="*40)
    print(f"🟢 Total Expenses: ${total_expenses:,.2f}")
    print(f"🔵 Mean Expense: ${mean_expense:,.2f}")
    print(f"🟠 Median Expense: ${median_expense:,.2f}")

    # Expenses by category
    expenses_by_category = df.groupby('category')['amount'].sum().sort_values(ascending=False)
    print("\nExpenses by Category:")
    print(expenses_by_category)

    # Box plot for outliers
    plt.figure(figsize=(10, 6))
    df.boxplot(column='amount', by='category')
    plt.title('Expense Distribution by Category')
    plt.suptitle('')
    plt.xlabel('Category')
    plt.ylabel('Amount ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Date validation
def validate_date(date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False

# Check if value is numeric
def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

# Main function
def main():
    while True:
        print("\n" + "="*40)
        print("   🌟 Personal Expense Tracker 🌟")
        print("="*40)
        print("1. ➕ Add an Expense")
        print("2. 👀 View Expenses")
        print("3. 📄 Generate Summary Report")
        print("4. ✏️ Update an Expense")
        print("5. ❌ Delete an Expense")
        print("6. 📂 View Expenses by Category")
        print("7. 🗓️ View Expenses by Date Range")
        print("8. 📅 Monthly Expense Summary")
        print("9. 📊 Visualize Expenses")
        print("10. 📈 Analyze Expenses")
        print("11. 🚪 Exit")
        print("="*40)

        choice = input("Choose an option (1-11): ")
        
        if choice == '1':
            print("\n" + "="*40)
            print("   🟢 Add an Expense 🟢")
            print("="*40)
            date = input("Enter date (YYYY-MM-DD): ")
            if not validate_date(date):
                print("\n❗ Invalid date format. Please enter a valid date in YYYY-MM-DD format.")
                continue
            category = input("Enter category: ")
            amount = input("Enter amount: ")
            if not is_numeric(amount):
                print("\n❗ Invalid amount. Please enter a numeric value.")
                continue
            gender = input("Enter gender: ")
            description = input("Enter description: ")
            add_expense(date, category, amount, gender, description)
            print("\n✅ Expense added successfully!")

        elif choice == '2':
            view_expense()
            print("✅ Here are your expenses.")
            
        elif choice == '3':
            generate_summary()
            print("✅ Summary report generated.")
            
        elif choice == '4':
            expense_id = input("Enter the ID of the expense to update: ")
            date = input("Enter new date (YYYY-MM-DD) (leave blank to keep current): ")
            category = input("Enter new category (leave blank to keep current): ")
            amount = input("Enter new amount (leave blank to keep current): ")
            if amount and not is_numeric(amount):
                print("\n❗ Invalid amount. Please enter a numeric value.")
                continue
            gender = input("Enter new gender (leave blank to keep current): ")
            description = input("Enter new description (leave blank to keep current): ")
            update_expense(expense_id, date, category, amount, gender, description)
            print("\n✅ Expense updated successfully!")
            
        elif choice == '5':
            expense_id = input("Enter the ID of the expense to delete: ")
            delete_expense(expense_id)
            print("\n✅ Expense deleted successfully!")
            
        elif choice == '6':
            category = input("Enter category to view expenses: ")
            view_expense_by_category(category)
            
        elif choice == '7':
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            if not validate_date(start_date) or not validate_date(end_date):
                print("\n❗ Invalid date format. Please enter valid dates in YYYY-MM-DD format.")
                continue
            view_expense_by_date(start_date, end_date)
            
        elif choice == '8':
            monthly_expense()
            
        elif choice == '9':
            visualize_expenses()
            
        elif choice == '10':
            analyze_expenses()
            
        elif choice == '11':
            print("\n👋 Exiting the Personal Expense Tracker. Goodbye!")
            break
            
        else:
            print("\n❗ Invalid option. Please choose a valid option (1-11).")

if __name__ == "__main__":
    main()
