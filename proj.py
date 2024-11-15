import streamlit as st
import mysql.connector
import bcrypt
from mysql.connector import Error

# Initialize session state for role and authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'role' not in st.session_state:
    st.session_state.role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'logout' not in st.session_state:
    st.session_state.logout = False

# Callback functions for state management
def handle_login(username, password):
    role = login_user(username, password)
    if role:
        st.session_state.authenticated = True
        st.session_state.role = role
        st.session_state.username = username
        return True
    return False

def handle_logout():
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.logout = True

# Database connection and other utility functions remain the same
def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='thegnas58',
            database='perishable_management_system'
        )
        return connection
    except Error as e:
        st.error(f"Error: {e}")
        return None

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode(), hashed_password)

def create_tables():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS USERS (
                USERNAME VARCHAR(50) UNIQUE NOT NULL PRIMARY KEY,
                PASSWORD VARCHAR(255) NOT NULL,
                ROLE ENUM('Admin', 'NGO', 'Driver', 'Food Source') NOT NULL
            )
            """)
            conn.commit()
        except Error as e:
            st.error(f"Error creating tables: {e}")
        finally:
            cursor.close()
            conn.close()

def register_user(username, password, role, additional_info=None):
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        hashed_pwd = hash_password(password)
        
        try:
            # Handle additional info for non-admin roles
            if role == 'NGO':
                query = """INSERT INTO NGO (NAME, CONTACT_NAME, CONTACT, EMAIL) 
                           VALUES (%s, %s, %s, %s)"""
                cursor.execute(query, additional_info)
                conn.commit()
                user_id = cursor.lastrowid

            elif role == 'Driver':
                query = """INSERT INTO DRIVERS (NAME, PHONE_NUMBER, EMAIL) 
                           VALUES (%s, %s, %s)"""
                cursor.execute(query, additional_info)
                conn.commit()
                user_id = cursor.lastrowid

            elif role == 'Food Source':
                query = """INSERT INTO FOOD_SOURCES (NAME, CONTACT_NAME, CONTACT, EMAIL) 
                           VALUES (%s, %s, %s, %s)"""
                cursor.execute(query, additional_info)
                conn.commit()
                user_id = cursor.lastrowid

            # Admin role doesn't need additional info
            if role == 'Admin':
                user_query = """INSERT INTO USERS (USERNAME, PASSWORD, ROLE) 
                                VALUES (%s, %s, %s)"""
                cursor.execute(user_query, (username, hashed_pwd, role))
                conn.commit()
                st.success("Admin registration successful!")
            else:
                if user_id:
                    user_query = """INSERT INTO USERS (USERNAME, PASSWORD, ROLE) 
                                    VALUES (%s, %s, %s)"""
                    cursor.execute(user_query, (username, hashed_pwd, role))
                    conn.commit()
                    st.success("Registration successful!")
                else:
                    st.error("Failed to retrieve ID for the user")

        except Error as e:
            conn.rollback()
            st.error(f"Registration failed: {e}")
        finally:
            cursor.close()
            conn.close()


def login_user(username, password):
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            query = """SELECT * FROM USERS WHERE USERNAME = %s"""
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            
            if user and check_password(user['PASSWORD'].encode(), password):
                return user['ROLE']
            else:
                st.error("Invalid username or password")
            
        except Error as e:
            st.error(f"Login error: {e}")
        finally:
            cursor.close()
            conn.close()
    return None

# Role-specific pages
def admin_dashboard():
    st.title("Admin Dashboard")
    
    # Sidebar navigation for admin
    admin_menu = st.sidebar.selectbox(
        "Admin Menu",
        ["Overview", "Manage NGOs", "Manage Drivers", "Manage Food Sources", "Reports"]
    )
    
    if admin_menu == "Overview":
        st.subheader("System Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total NGOs", "12")
        with col2:
            st.metric("Active Drivers", "8")
        with col3:
            st.metric("Food Sources", "15")
            
    elif admin_menu == "Manage NGOs":
        st.subheader("NGO Management")
        # Add NGO management functionality
        st.write("Here you can view and manage NGO registrations")
        
    elif admin_menu == "Manage Drivers":
        st.subheader("Driver Management")
        # Add driver management functionality
        st.write("Here you can view and manage drivers")
        
    elif admin_menu == "Manage Food Sources":
        st.subheader("Food Source Management")
        # Add food source management functionality
        st.write("Here you can view and manage food sources")
        
    elif admin_menu == "Reports":
        st.subheader("System Reports")
        # Add reporting functionality
        st.write("View system reports and analytics")
 
from ngo import manage_ngos,manage_impact,display_ngo_statistics,handle_donation_request

def ngo_dashboard():
    st.title("NGO Dashboard")
    
    conn = create_connection()
    if not conn:
        return

    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose a tab", ["Home", "Manage NGOs Info","Feedback","Donation"])

    if app_mode == "Home":
        st.subheader("Welcome to the Perishable Management System")
        st.write("Use the side menu to navigate to different sections.")
        display_ngo_statistics()

    elif app_mode == "Manage NGOs Info":
        manage_ngos(conn)

    elif app_mode == "Feedback":
        manage_impact(conn)
    
    if app_mode == "Donation":
        st.title("Donation Source Management")
        # Input fields for the user
        ngo_id = st.number_input("Enter NGO ID", min_value=1, step=1)
        required_category = st.text_input("Enter Required Category")
        required_quantity_input = st.text_input("Enter Required Quantity")

        # Handle the case where the user might input non-numeric values for required_quantity
        if required_quantity_input:
            try:
                # Attempt to convert the entered value into an integer
                required_quantity = int(required_quantity_input)
            except ValueError:
                # Show an error message if the value is not a valid integer
                st.error("Please enter a valid numeric value for required quantity.")
                return
        else:
            required_quantity = 0  # Default to 0 if no input is provided

        # Submit button to request a donation source
        if st.button("Request Donation Source"):
            if required_quantity > 0:
                handle_donation_request(ngo_id, required_category, required_quantity)
            else:
                st.error("Please enter a valid quantity greater than 0.")

from pickups import manage_drivers,display_driver_statistics,schedule_pickup

def driver_dashboard():
    conn = create_connection()
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose a tab", ["Home", "Manage Drivers","Schedule Pickups"])

    if app_mode == "Home":
        st.subheader("Welcome to the Perishable Management System")
        st.write("Use the side menu to navigate to different sections.")
        display_driver_statistics()

    elif app_mode == "Manage Drivers":
        manage_drivers(conn)
    
    elif app_mode=="Schedule Pickups":
        st.title("Pickup Scheduling")
    
        # Streamlit form for user input
        with st.form(key='pickup_form'):
            source_id = st.number_input("Source ID", min_value=1, step=1)
            destination_input = st.text_input("Destination")
            vehicle_type_input = st.selectbox("Vehicle Type", ["Car", "Van", "Truck"])
            pickup_date = st.date_input("Pickup Date")
            pickup_time = st.time_input("Pickup Time")

            submit_button = st.form_submit_button("Schedule Pickup")
        
        if submit_button:
            if source_id and destination_input and vehicle_type_input and pickup_date and pickup_time:
                # Execute the procedure
                schedule_pickup(source_id, destination_input, vehicle_type_input, pickup_date, pickup_time)
            else:
                st.error("Please fill in all the fields!")
    

from food import  manage_food_sources,display_impact_dashboard,manage_food_items,get_top_demanded_categories


def food_source_dashboard():
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
        
def login_page():
    st.subheader("Login to Your Account")
    
    # Using columns for better layout
    col1, col2 = st.columns([2, 1])
    with col1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type='password', key="login_password")
        
        if st.button("Login", key="login_button"):
            handle_login(username, password)

def register_page():
    st.subheader("Create a New Account")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    role = st.selectbox("Select Role", ["Admin", "NGO", "Driver", "Food Source"])
    
    if role == "NGO":
        additional_info = (
            st.text_input("NGO Name"),
            st.text_input("Contact Name"),
            st.text_input("Contact Number"),
            st.text_input("Email"),
        )
    elif role == "Driver":
        additional_info = (
            st.text_input("Driver Name"),
            st.text_input("Phone Number"),
            st.text_input("Email")
        )
    elif role == "Food Source":
        additional_info = (
            st.text_input("Food Source Name"),
            st.text_input("Contact Name"),
            st.text_input("Contact Number"),
            st.text_input("Email"),
        )
    else:
        additional_info = None  # No additional info needed for Admin
    
    if st.button("Register"):
        if username and password:
            register_user(username, password, role, additional_info)
        else:
            st.warning("Please fill in all fields")

def main():
    st.title("Perishable Management System")
    
    # Sidebar for navigation
    with st.sidebar:
        if st.session_state.authenticated:
            st.write(f"Welcome, {st.session_state.username}")
            if st.button("Logout", key="logout_button"):
                handle_logout()
        else:
            menu = ["Home", "Login", "Register"]
            choice = st.selectbox("Menu", menu, key="main_menu")
            
    # Main content area
    if not st.session_state.authenticated:
        if 'main_menu' not in st.session_state:
            st.session_state.main_menu = "Home"
            
        if st.session_state.main_menu == "Home":
            st.markdown("""
    ## 🥕 **Perishable Management System** 🥦

    ### Welcome to the Perishable Management System 🌍

    Our mission is to bridge the gap between food surplus and scarcity by efficiently managing the redistribution of perishable food items. We connect NGOs, food sources, and delivery partners to ensure that no edible food goes to waste, helping to combat hunger and reduce food waste in communities.

    ---

    ### 🌱 **Did You Know?**

    - **1.3 billion tons** of food is wasted globally every year — that’s nearly **one-third of all food produced** for human consumption!
    - Meanwhile, **1 in 9 people** in the world suffer from hunger. That’s nearly **820 million people** who do not have enough to eat.
    - By saving just **25% of wasted food**, we could feed all of the world’s undernourished people.
    - Reducing food waste is one of the **top 3 solutions** to address climate change, as it accounts for **8% of global greenhouse gas emissions**.

    ---

    ### 💡 **How We Make a Difference**

    - 🍎 **Food Sources** donate surplus perishable items.
    - 🚚 **Drivers** ensure timely pick-up and delivery to those in need.
    - 🏥 **NGOs** and organizations receive and distribute food to the hungry.

    Join us in our mission to create a sustainable future by making sure no food goes to waste! 🌍🍽️

    ---

    ### 👤 **Please Login or Register to Continue**

    If you are a **Food Source**, **Driver**, or **NGO**, log in to access your dashboard and start contributing to a world with less waste and more smiles!
    """)
            
        elif st.session_state.main_menu == "Login":
            login_page()
            
        elif st.session_state.main_menu == "Register":
            register_page()
            
    else:
        # Display role-specific dashboard
        if st.session_state.role == "Admin":
            admin_dashboard()
        elif st.session_state.role == "NGO":
            ngo_dashboard()
        elif st.session_state.role == "Driver":
            driver_dashboard()
        elif st.session_state.role == "Food Source":
            food_source_dashboard()

if __name__ == '__main__':
    create_tables()
    main()