import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
from datetime import datetime, timedelta
import numpy as np
from mysql.connector import Error
import matplotlib.pyplot as plt

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',    # Update with your MySQL username
            password='thegnas58',  # Update with your MySQL password
            database='perishable_management_system'  # Update with your MySQL database
        )
        return connection
    except Error as e:
        st.error(f"Error: {e}")
        return None

def display_impact_dashboard():
    st.title("🏪 Food Source Impact Analytics Dashboard")
    
    try:
        conn = create_connection()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Get all food sources for selection
        cursor.execute("SELECT SOURCE_ID, NAME FROM FOOD_SOURCES")
        sources = dict(cursor.fetchall())
        
        # Sidebar for source selection
        st.sidebar.header("📊 Dashboard Controls")
        selected_source = st.sidebar.selectbox(
            "Select Food Source",
            options=list(sources.keys()),
            format_func=lambda x: sources[x]
        )
        
        # Get impact data for the selected source
        cursor.execute("SELECT GetFoodSourceImpact(%s)", (selected_source,))
        impact_data = cursor.fetchone()[0]
        
        # Parse impact data for selected source
        impact_metrics = {}
        for metric in impact_data.split(', '):
            key, value = metric.split(': ')
            impact_metrics[key] = value.replace(' kg', '') if 'kg' in value else value
        
        # Show Key Performance Metrics for the selected source
        st.header("📈 Selected Source Impact")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style='padding: 20px; background-color: #f0f2f6; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 2px solid #ddd;'>
                <h3 style='color: black;'>Total Food Items</h3>
                <h2 style='color: black;'>{impact_metrics.get('Total Food Items Provided', 'N/A')}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div style='padding: 20px; background-color: #f0f2f6; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 2px solid #ddd;'>
                <h3 style='color: black;'>NGOs Supported</h3>
                <h2 style='color: black;'>{impact_metrics.get('Total NGOs Supported', 'N/A')}</h2>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div style='padding: 20px; background-color: #f0f2f6; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 2px solid #ddd;'>
                <h3 style='color: black;'>People Helped</h3>
                <h2 style='color: black;'>{impact_metrics.get('Total People Helped', 'N/A')}</h2>
            </div>
            """, unsafe_allow_html=True)

        # Monthly Donation Trends for the selected source
        st.header("📊 Monthly Donation Analysis")
        cursor.execute(f"""
            SELECT 
                DATE_FORMAT(dt.DATE_TIME, '%Y-%m') as month,
                SUM(d.QUANTITY) as total_quantity
            FROM DONATES_TO dt
            JOIN DONATIONS d ON dt.DONATION_ID = d.DONATION_ID
            WHERE d.SOURCE_ID = {selected_source}
            GROUP BY DATE_FORMAT(dt.DATE_TIME, '%Y-%m')
            ORDER BY month
        """)
        donation_trends = pd.DataFrame(cursor.fetchall(), columns=['month', 'quantity'])
        
        if not donation_trends.empty:
            fig = px.line(donation_trends, 
                         x='month', 
                         y='quantity',
                         title='Monthly Donation Quantities',
                         labels={'month': 'Month', 'quantity': 'Quantity (kg)'},
                         line_shape='spline')
            st.plotly_chart(fig, use_container_width=True)
        
        # Display general statistics (not specific to any source)
        st.header("📊 General Impact Statistics")
        
        # General food item statistics (across all sources)
        cursor.execute("""
            SELECT 
                SUM(d.QUANTITY) as total_quantity,
                COUNT(DISTINCT d.SOURCE_ID) as total_sources,
                COUNT(DISTINCT n.NGO_ID) as total_ngos,
                SUM(d.QUANTITY) / COUNT(DISTINCT n.NGO_ID) as avg_donated_per_ngo
            FROM DONATIONS d
            JOIN DONATES_TO dt ON d.DONATION_ID = dt.DONATION_ID
            JOIN NGO n ON d.NGO_ID = n.NGO_ID
        """)
        general_stats = cursor.fetchone()
        
        st.markdown(f"""
        <div style='padding: 20px; background-color: #f0f2f6; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 2px solid #ddd;'>
            <h3 style='color: black;'>Total Food Items Donated (Across All Sources)</h3>
            <h2 style='color: black;'>{general_stats[0]:,.0f} kg</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='padding: 20px; background-color: #f0f2f6; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 2px solid #ddd;'>
            <h3 style='color: black;'>Total Sources Contributing</h3>
            <h2 style='color: black;'>{general_stats[1]}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='padding: 20px; background-color: #f0f2f6; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 2px solid #ddd;'>
            <h3 style='color: black;'>Total NGOs Supported</h3>
            <h2 style='color: black;'>{general_stats[2]}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='padding: 20px; background-color: #f0f2f6; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 2px solid #ddd;'>
            <h3 style='color: black;'>Average Quantity Donated Per NGO</h3>
            <h2 style='color: black;'>{general_stats[3]:,.0f} kg</h2>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()



# Function to manage food sources
def manage_food_sources(conn):
    c = conn.cursor()
    st.subheader("Manage Food Sources")

    # Display all food sources with headers
    st.write("### List of Food Sources")
    c.execute("SELECT * FROM FOOD_SOURCES")
    sources = c.fetchall()
    if sources:
        st.table([['Source ID', 'Name', 'Contact Name', 'Contact', 'Email', 'Details', 'Locality', 'Pincode']] + sources)
    else:
        st.info("No food sources available.")

    # Operation options
    operation = st.radio("Select Operation", ['Update Source', 'Delete Source', 'View Source Details'])

    # 2. Update an Existing Food Source
    if operation == 'Update Source':
        st.write("### Update Food Source")
        source_id = st.number_input("Enter Source ID to update", min_value=1)
        c.execute("SELECT * FROM FOOD_SOURCES WHERE SOURCE_ID = %s", (source_id,))
        source = c.fetchone()

        if source:
            st.write("Current Details:")
            st.write(f"Name: {source[1]}, Contact Name: {source[2]}, Contact: {source[3]}, Email: {source[4]}, Details: {source[5]}, Locality: {source[6]}, Pincode: {source[7]}")

            # Input fields for updated values
            updated_name = st.text_input("Update Source Name", value=source[1])
            updated_contact_name = st.text_input("Update Contact Name", value=source[2])
            updated_contact = st.text_input("Update Contact Info", value=source[3])
            updated_email = st.text_input("Update Email", value=source[4])
            updated_details = st.text_area("Update Details", value=source[5])
            updated_locality = st.text_input("Update Locality", value=source[6])
            updated_pincode = st.text_input("Update Pincode", value=source[7])

            if st.button("Update Source"):
                try:
                    c.execute(
                        "UPDATE FOOD_SOURCES SET NAME = %s, CONTACT_NAME = %s, CONTACT = %s, EMAIL = %s, DETAILS = %s, LOCALITY = %s, PINCODE = %s WHERE SOURCE_ID = %s",
                        (updated_name, updated_contact_name, updated_contact, updated_email, updated_details, updated_locality, updated_pincode, source_id)
                    )
                    conn.commit()
                    st.success("Food Source updated successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Food Source not found. Please enter a valid Source ID.")

    # 3. Delete a Food Source
    elif operation == 'Delete Source':
        st.write("### Delete Food Source")
        source_id = st.number_input("Enter Source ID to delete", min_value=1)

        if st.button("Delete Source"):
            try:
                c.execute("DELETE FROM FOOD_SOURCES WHERE SOURCE_ID = %s", (source_id,))
                conn.commit()
                if c.rowcount > 0:
                    st.success("Food Source deleted successfully!")
                else:
                    st.warning("Source ID not found.")
            except Exception as e:
                st.error(f"Error: {e}")

    # 4. View a Single Food Source
    elif operation == 'View Source Details':
        st.write("### View Food Source Details")
        source_id = st.number_input("Enter Source ID to view", min_value=1)
        c.execute("SELECT * FROM FOOD_SOURCES WHERE SOURCE_ID = %s", (source_id,))
        source = c.fetchone()

        if source:
            st.write(f"Source ID: {source[0]}")
            st.write(f"Name: {source[1]}")
            st.write(f"Contact Name: {source[2]}")
            st.write(f"Contact Info: {source[3]}")
            st.write(f"Email: {source[4]}")
            st.write(f"Details: {source[5]}")
            st.write(f"Locality: {source[6]}")
            st.write(f"Pincode: {source[7]}")
        else:
            st.warning("Food Source not found. Please enter a valid Source ID.")

def manage_food_items(conn):
    c = conn.cursor()
    st.subheader("Manage Food Items")

    # Display all food items with headers
    st.write("### List of Food Items")
    c.execute("SELECT * FROM FOOD_ITEM")
    items = c.fetchall()
    if items:
        st.table([['Food ID', 'Name', 'Quantity', 'Category', 'Expiry Date', 'Source ID']] + items)
    else:
        st.info("No food items available.")

    # Operation options
    operation = st.radio("Select Operation", ['Create Item', 'Update Item', 'Delete Item', 'View Item Details'])

    # 1. Create a New Food Item
    if operation == 'Create Item':
        st.write("### Create New Food Item")
        name = st.text_input("Enter Item Name")
        quantity = st.number_input("Enter Quantity", min_value=1, step=1)
        category = st.text_input("Enter Category")
        expiry_date = st.date_input("Enter Expiry Date")
        source_id = st.number_input("Enter Source ID", min_value=1)

        if st.button("Create Item"):
            try:
                c.execute(
                    "INSERT INTO FOOD_ITEM (NAME, QUANTITY, CATEGORY, EXPIRY_DATE, SOURCE_ID) VALUES (%s, %s, %s, %s, %s)",
                    (name, quantity, category, expiry_date, source_id)
                )
                conn.commit()
                st.success("Food item created successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    # 2. Update an Existing Food Item
    elif operation == 'Update Item':
        st.write("### Update Food Item")
        food_id = st.number_input("Enter Food ID to update", min_value=1)
        c.execute("SELECT * FROM FOOD_ITEM WHERE FOOD_ID = %s", (food_id,))
        item = c.fetchone()
        if item:
            st.write("Current Details:")
            st.write(f"Food ID: {item[0]}, Name: {item[1]}, Quantity: {item[2]}, Category: {item[3]}, Expiry Date: {item[4]}, Source ID: {item[5]}")

            updated_name = st.text_input("Update Name", value=item[1])
            updated_quantity = st.number_input("Update Quantity", min_value=1, step=1, value=item[2])
            updated_category = st.text_input("Update Category", value=item[3])
            updated_expiry_date = st.date_input("Update Expiry Date", value=item[4])
            updated_source_id = st.number_input("Update Source ID", min_value=1, value=item[5])

            if st.button("Update Item"):
                try:
                    c.execute(
                        "UPDATE FOOD_ITEM SET NAME = %s, QUANTITY = %s, CATEGORY = %s, EXPIRY_DATE = %s, SOURCE_ID = %s WHERE FOOD_ID = %s",
                        (updated_name, updated_quantity, updated_category, updated_expiry_date, updated_source_id, food_id)
                    )
                    conn.commit()
                    st.success("Food item updated successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Food ID not found. Please enter a valid Food ID.")

    # 3. Delete a Food Item
    elif operation == 'Delete Item':
        st.write("### Delete Food Item")
        food_id = st.number_input("Enter Food ID to delete", min_value=1)
        if st.button("Delete Item"):
            try:
                c.execute("DELETE FROM FOOD_ITEM WHERE FOOD_ID = %s", (food_id,))
                conn.commit()
                if c.rowcount > 0:
                    st.success("Food item deleted successfully!")
                else:
                    st.warning("Food ID not found.")
            except Exception as e:
                st.error(f"Error: {e}")

    # 4. View a Single Food Item
    elif operation == 'View Item Details':
        st.write("### View Food Item Details")
        food_id = st.number_input("Enter Food ID to view", min_value=1)
        c.execute("SELECT * FROM FOOD_ITEM WHERE FOOD_ID = %s", (food_id,))
        item = c.fetchone()
        if item:
            st.write(f"Food ID: {item[0]}")
            st.write(f"Name: {item[1]}")
            st.write(f"Quantity: {item[2]}")
            st.write(f"Category: {item[3]}")
            st.write(f"Expiry Date: {item[4]}")
            st.write(f"Source ID: {item[5]}")
        else:
            st.warning("Food item not found. Please enter a valid Food ID.")

def get_top_demanded_categories(conn, top_n):
    c = conn.cursor()
    c.execute("CALL GetTopDemandedCategories(%s)", (top_n,))
    result = c.fetchall()
    
    if result:
        st.subheader(f"Top {top_n} Most Demanded Food Categories")
        
        # Convert result to a pandas DataFrame
        columns = ['Source ID', 'Source Name', 'NGO ID', 'NGO Name', 'Requested Category', 'Request Count']
        df = pd.DataFrame(result, columns=columns)
        
        # Display the results in a table
        st.write(df)
        
        # Create a bar graph
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(df['Requested Category'], df['Request Count'])
        ax.set_xlabel('Requested Category')
        ax.set_ylabel('Request Count')
        ax.set_title(f"Top {top_n} Most Demanded Food Categories")
        ax.tick_params(axis='x', rotation=90)
        st.pyplot(fig)
    else:
        st.warning("No data available.")

# Streamlit main function to run the app
def main():
    # Connect to the database
    conn = mysql.connector.connect(
        host="localhost",  # Replace with your database host
        user="root",  # Replace with your database user
        password="thegnas58",  # Replace with your database password
        database="perishable_management_system"  # Replace with your database name
    )
    
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose a tab", ["Home", "Manage Info","Make Donation ","Top Categories"])
    
    if app_mode == "Home":
        st.subheader("Welcome to the Perishable Management System")
        st.write("Use the side menu to navigate to different sections.")
        display_impact_dashboard()
        
    
    elif app_mode == "Manage Info":
        manage_food_sources(conn)

    elif app_mode == "Make Donation ":
        manage_food_items(conn)
    
    elif app_mode == "Top Categories":
        st.title("Top Demanded Food Categories")
    
        with st.form(key='top_n_form'):
            top_n = st.number_input("Enter the number of top categories to display:", min_value=1, step=1, value=3)
            submit_button = st.form_submit_button(label='Get Top Demanded Categories')
        
        if submit_button:
            get_top_demanded_categories(conn, top_n)
        
    
    # Close the connection
    conn.close()

# Run the app
if __name__ == "__main__":
    main()
