
from mysql.connector import Error
import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Database connection function
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

def manage_drivers(conn):
    c = conn.cursor()
    st.subheader("Manage Drivers")

    # Display all Drivers with headers
    st.write("### List of Drivers")
    c.execute("SELECT * FROM DRIVERS")
    drivers = c.fetchall()
    if drivers:
        st.table([['Driver ID', 'Name', 'Phone Number', 'Email', 'License Number', 'Vehicle Type', 
                   'Vehicle Number', 'Availability Status', 'Last Pickup Date', 'Total Completed Pickups']] + drivers)
    else:
        st.info("No Drivers available.")

    # Operation options
    operation = st.radio("Select Operation", ['Update Driver', 'Delete Driver', 'View Driver Details'])

    # 2. Update an Existing Driver
    if operation == 'Update Driver':
        st.write("### Update Driver")
        driver_id = st.number_input("Enter Driver ID to update", min_value=1)
        c.execute("SELECT * FROM DRIVERS WHERE DRIVER_ID = %s", (driver_id,))
        driver = c.fetchone()

        if driver:
            st.write("Current Details:")
            st.write(f"Name: {driver[1]}, Phone: {driver[2]}, Email: {driver[3]}, License: {driver[4]}, "
                     f"Vehicle Type: {driver[5]}, Vehicle Number: {driver[6]}, Status: {driver[7]}, "
                     f"Last Pickup: {driver[8]}, Total Pickups: {driver[9]}")

            # Input fields for updated values
            updated_name = st.text_input("Update Driver Name", value=driver[1])
            updated_phone = st.text_input("Update Phone Number", value=driver[2])
            updated_email = st.text_input("Update Email", value=driver[3])
            updated_license = st.text_input("Update License Number", value=driver[4] if driver[4] else "")
            updated_vehicle_type = st.text_input("Update Vehicle Type", value=driver[5] if driver[5] else "")
            updated_vehicle_number = st.text_input("Update Vehicle Number", value=driver[6] if driver[6] else "")
            updated_status = st.selectbox("Update Availability Status", ['Available', 'Busy', 'Off-Duty'], 
                                          index=['Available', 'Busy', 'Off-Duty'].index(driver[7]))

            if st.button("Update Driver"):
                try:
                    c.execute(
                        "UPDATE DRIVERS SET NAME = %s, PHONE_NUMBER = %s, EMAIL = %s, LICENSE_NUMBER = %s, "
                        "VEHICLE_TYPE = %s, VEHICLE_NUMBER = %s, AVAILABILITY_STATUS = %s WHERE DRIVER_ID = %s",
                        (updated_name, updated_phone, updated_email, updated_license, updated_vehicle_type,
                         updated_vehicle_number, updated_status, driver_id)
                    )
                    conn.commit()
                    st.success("Driver updated successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Driver not found. Please enter a valid Driver ID.")

    # 3. Delete a Driver
    elif operation == 'Delete Driver':
        st.write("### Delete Driver")
        driver_id = st.number_input("Enter Driver ID to delete", min_value=1)

        if st.button("Delete Driver"):
            try:
                c.execute("DELETE FROM DRIVERS WHERE DRIVER_ID = %s", (driver_id,))
                conn.commit()
                if c.rowcount > 0:
                    st.success("Driver deleted successfully!")
                else:
                    st.warning("Driver ID not found.")
            except Exception as e:
                st.error(f"Error: {e}")

    # 4. View a Single Driver
    elif operation == 'View Driver Details':
        st.write("### View Driver Details")
        driver_id = st.number_input("Enter Driver ID to view", min_value=1)
        c.execute("SELECT * FROM DRIVERS WHERE DRIVER_ID = %s", (driver_id,))
        driver = c.fetchone()

        if driver:
            st.write(f"Driver ID: {driver[0]}")
            st.write(f"Name: {driver[1]}")
            st.write(f"Phone Number: {driver[2]}")
            st.write(f"Email: {driver[3]}")
            st.write(f"License Number: {driver[4]}")
            st.write(f"Vehicle Type: {driver[5]}")
            st.write(f"Vehicle Number: {driver[6]}")
            st.write(f"Availability Status: {driver[7]}")
            st.write(f"Last Pickup Date: {driver[8]}")
            st.write(f"Total Completed Pickups: {driver[9]}")
        else:
            st.warning("Driver not found. Please enter a valid Driver ID.")

def display_driver_statistics():
    st.title("🚚 Driver Analytics Dashboard")
    
    try:
        conn = create_connection()
        cursor = conn.cursor()
        
        # Create columns for key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Total Drivers
        with col1:
            cursor.execute("SELECT COUNT(*) FROM DRIVERS")
            total_drivers = cursor.fetchone()[0]
            st.metric(
                label="Total Drivers",
                value=total_drivers,
                delta=None
            )
        
        # Available Drivers
        with col2:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM DRIVERS 
                WHERE availability_status = 'Available'
            """)
            available_drivers = cursor.fetchone()[0]
            st.metric(
                label="Available Drivers",
                value=available_drivers,
                delta=None
            )
        
        # Total Pickups Today
        with col3:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM SCHEDULES 
                WHERE DATE = CURDATE()
            """)
            today_pickups = cursor.fetchone()[0]
            st.metric(
                label="Today's Pickups",
                value=today_pickups,
                delta=None
            )
        
        # Average Pickups per Driver
        with col4:
            cursor.execute("""
                SELECT AVG(total_completed_pickups) 
                FROM DRIVERS
            """)
            avg_pickups = cursor.fetchone()[0] or 0
            st.metric(
                label="Avg Pickups/Driver",
                value=f"{avg_pickups:.1f}",
                delta=None
            )

        # Driver Status Distribution
        st.subheader("👨‍💼 Driver Availability Status")
        cursor.execute("""
            SELECT availability_status, COUNT(*) as count 
            FROM DRIVERS 
            GROUP BY availability_status
        """)
        status_data = pd.DataFrame(cursor.fetchall(), 
                                 columns=['status', 'count'])
        
        if not status_data.empty:
            fig = go.Figure(data=[go.Pie(
                labels=status_data['status'],
                values=status_data['count'],
                hole=.3
            )])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        # Vehicle Type Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚗 Vehicle Type Distribution")
            cursor.execute("""
                SELECT vehicle_type, COUNT(*) as count 
                FROM FOOD_PICKUP 
                GROUP BY vehicle_type
            """)
            vehicle_data = pd.DataFrame(cursor.fetchall(), 
                                      columns=['vehicle_type', 'count'])
            
            if not vehicle_data.empty:
                fig = px.bar(vehicle_data, 
                           x='vehicle_type', 
                           y='count',
                           color='vehicle_type',
                           labels={'count': 'Number of Pickups', 
                                  'vehicle_type': 'Vehicle Type'})
                st.plotly_chart(fig)

        # Top Performing Drivers
        with col2:
            st.subheader("🏆 Top Performing Drivers")
            cursor.execute("""
                SELECT name, total_completed_pickups 
                FROM DRIVERS 
                ORDER BY total_completed_pickups DESC 
                LIMIT 5
            """)
            top_drivers = pd.DataFrame(cursor.fetchall(), 
                                     columns=['name', 'pickups'])
            
            if not top_drivers.empty:
                fig = px.bar(top_drivers, 
                           x='name', 
                           y='pickups',
                           labels={'pickups': 'Completed Pickups', 
                                  'name': 'Driver Name'})
                st.plotly_chart(fig)

        # Pickup Schedule Timeline
        st.subheader("📅 Upcoming Pickups Schedule")
        cursor.execute("""
            SELECT 
                s.DATE as pickup_date,
                COUNT(*) as pickup_count
            FROM SCHEDULES s
            WHERE s.DATE >= CURDATE()
            GROUP BY s.DATE
            ORDER BY s.DATE
            LIMIT 7
        """)
        schedule_data = pd.DataFrame(cursor.fetchall(), 
                                   columns=['date', 'pickups'])
        
        if not schedule_data.empty:
            fig = px.line(schedule_data, 
                         x='date', 
                         y='pickups',
                         markers=True,
                         labels={'pickups': 'Number of Pickups', 
                                'date': 'Date'})
            st.plotly_chart(fig, use_container_width=True)

         # Recent Activity Feed
        st.subheader("📋 Recent Pickup Activities")
        cursor.execute("""
            SELECT 
                d.name as driver_name,
                fp.status,
                fp.destination,
                fp.vehicle_type,
                s.DATE,
                TIME_FORMAT(s.TIME, '%H:%i') as formatted_time
            FROM DRIVERS d
            JOIN FOOD_PICKUP fp ON d.DRIVER_ID = fp.DRIVER_ID
            JOIN SCHEDULES s ON fp.PICKUP_ID = s.PICKUP_ID
            ORDER BY s.DATE DESC, s.TIME DESC
            LIMIT 5
        """)
        activities = cursor.fetchall()
        
        for activity in activities:
            with st.expander(
                f"{activity[0]} - {activity[4].strftime('%Y-%m-%d')} {activity[5]}"
            ):
                st.write(f"""
                    🚚 Vehicle: {activity[3]}
                    📍 Destination: {activity[2]}
                    📊 Status: {activity[1]}
                """)

    except Exception as e:
        st.error(f"Error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


def schedule_pickup(source_id, destination_input, vehicle_type_input, pickup_date, pickup_time):
    connection = create_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Call the stored procedure
            cursor.callproc('schedulePickup', [source_id, destination_input, vehicle_type_input, pickup_date, pickup_time])

            # Commit the transaction
            connection.commit()

            st.success("Pickup scheduled successfully!")
        except Error as e:
            st.error(f"Error executing procedure: {e}")
        finally:
            cursor.close()
            connection.close()


def main():
    # Establish a connection to the database
    conn = create_connection()
    if not conn:
        return

    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose a tab", ["Home", "Manage Drivers","Schedule Pickups "])

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
    
    # Close the database connection
    conn.close()

# Run the Streamlit app
if __name__ == "__main__":
    main()
