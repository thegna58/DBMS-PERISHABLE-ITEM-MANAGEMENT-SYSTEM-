import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
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

def manage_ngos(conn):
    c = conn.cursor()
    st.subheader("Manage NGOs")

    # Display all NGOs with headers
    st.write("### Current List of NGOs")
    c.execute("SELECT * FROM NGO")
    ngos = c.fetchall()
    if ngos:
        st.table([['NGO ID', 'Name', 'Contact Name', 'Contact', 'Email', 'Category Req', 'Address']] + ngos)
    else:
        st.info("No NGOs available.")

    # Operation options
    operation = st.radio("Select Operation", ['Update NGO', 'Delete NGO', 'View NGO Details'])

    # 1. Update an Existing NGO
    if operation == 'Update NGO':
        st.write("### Update NGO")
        ngo_id = st.number_input("Enter NGO ID to update", min_value=1)
        c.execute("SELECT * FROM NGO WHERE NGO_ID = %s", (ngo_id,))
        ngo = c.fetchone()

        if ngo:
            st.write("Current Details:")
            st.write(f"Name: {ngo[1]}, Contact Name: {ngo[2]}, Contact: {ngo[3]}, Email: {ngo[4]}, "
                     f"Category Req: {ngo[5]}, Address: {ngo[6]}")

            # Input fields for updated values
            updated_name = st.text_input("Update NGO Name", value=ngo[1])
            updated_contact_name = st.text_input("Update Contact Name", value=ngo[2])
            updated_contact = st.text_input("Update Contact Info", value=ngo[3])
            updated_email = st.text_input("Update Email", value=ngo[4])
            updated_category_req = st.text_input("Update Category Requirement", value=ngo[5] if ngo[5] else "")
            updated_address = st.text_area("Update Address", value=ngo[6] if ngo[6] else "")

            if st.button("Update NGO"):
                try:
                    c.execute(
                        "UPDATE NGO SET NAME = %s, CONTACT_NAME = %s, CONTACT = %s, EMAIL = %s, CATEGORY_REQ = %s, ADDRESS = %s WHERE NGO_ID = %s",
                        (updated_name, updated_contact_name, updated_contact, updated_email, updated_category_req, updated_address, ngo_id)
                    )
                    conn.commit()
                    st.success("NGO updated successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("NGO not found. Please enter a valid NGO ID.")

    # 2. Delete an NGO
    elif operation == 'Delete NGO':
        st.write("### Delete NGO")
        ngo_id = st.number_input("Enter NGO ID to delete", min_value=1)

        if st.button("Delete NGO"):
            try:
                c.execute("DELETE FROM NGO WHERE NGO_ID = %s", (ngo_id,))
                conn.commit()
                if c.rowcount > 0:
                    st.success("NGO deleted successfully!")
                else:
                    st.warning("NGO ID not found.")
            except Exception as e:
                st.error(f"Error: {e}")

    # 3. View a Single NGO
    elif operation == 'View NGO Details':
        st.write("### View NGO Details")
        ngo_id = st.number_input("Enter NGO ID to view", min_value=1)
        c.execute("SELECT * FROM NGO WHERE NGO_ID = %s", (ngo_id,))
        ngo = c.fetchone()

        if ngo:
            st.write(f"NGO ID: {ngo[0]}")
            st.write(f"Name: {ngo[1]}")
            st.write(f"Contact Name: {ngo[2]}")
            st.write(f"Contact Info: {ngo[3]}")
            st.write(f"Email: {ngo[4]}")
            st.write(f"Category Req: {ngo[5]}")
            st.write(f"Address: {ngo[6]}")
        else:
            st.warning("NGO not found. Please enter a valid NGO ID.")

def manage_impact(conn):
    c = conn.cursor()
    st.subheader("Manage Impact Records")

    # Display all Impact Records with headers
    st.write("### Current Review")
    c.execute("SELECT * FROM IMPACT")
    impacts = c.fetchall()
    if impacts:
        st.table([['IMPACT ID', 'Source ID', 'NGO ID', 'Source', 'Destination', 'Feedback', 'Rate', 'People Helped']] + impacts)
    else:
        st.info("No Impact records available.")

    # Operation options
    operation = st.radio("Select Operation", ['Create Impact', 'Update Impact', 'Delete Impact', 'View Impact Details'])

    # 1. Create a New Impact Record
    if operation == 'Create Impact':
        st.write("### Create New Impact")
        
        # Input fields for new impact record
        source_id = st.number_input("Enter Source ID", min_value=1)
        ngo_id = st.number_input("Enter NGO ID", min_value=1)
        source = st.text_input("Enter Source", max_chars=255)
        destination = st.text_input("Enter Destination", max_chars=255)
        feedback = st.text_area("Enter Feedback")
        rate = st.number_input("Enter Rate (1-5)", min_value=1, max_value=5)
        people_helped = st.number_input("Enter Number of People Helped", min_value=0)

        if st.button("Create Impact"):
            try:
                c.execute(
                    "INSERT INTO IMPACT (SOURCE_ID, NGO_ID, SOURCE, DESTINATION, FEEDBACK, RATE, PEOPLE_HELPED) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (source_id, ngo_id, source, destination, feedback, rate, people_helped)
                )
                conn.commit()
                st.success("New Impact record created successfully!")
            except Exception as e:
                st.error(f"Error: {e}")

    # 2. Update an Existing Impact
    elif operation == 'Update Impact':
        st.write("### Update Impact")
        impact_id = st.number_input("Enter IMPACT ID to update", min_value=1)
        c.execute("SELECT * FROM IMPACT WHERE IMPACT_ID = %s", (impact_id,))
        impact = c.fetchone()

        if impact:
            st.write("Current Details:")
            st.write(f"Source ID: {impact[1]}, NGO ID: {impact[2]}, Source: {impact[3]}, Destination: {impact[4]}, "
                     f"Feedback: {impact[5]}, Rate: {impact[6]}, People Helped: {impact[7]}")

            # Input fields for updated values
            updated_source_id = st.number_input("Update Source ID", value=impact[1])
            updated_ngo_id = st.number_input("Update NGO ID", value=impact[2])
            updated_source = st.text_input("Update Source", value=impact[3])
            updated_destination = st.text_input("Update Destination", value=impact[4])
            updated_feedback = st.text_area("Update Feedback", value=impact[5] if impact[5] else "")
            updated_rate = st.number_input("Update Rate (1-5)", value=impact[6], min_value=1, max_value=5)
            updated_people_helped = st.number_input("Update People Helped", value=impact[7])

            if st.button("Update Impact"):
                try:
                    c.execute(
                        "UPDATE IMPACT SET SOURCE_ID = %s, NGO_ID = %s, SOURCE = %s, DESTINATION = %s, FEEDBACK = %s, RATE = %s, PEOPLE_HELPED = %s WHERE IMPACT_ID = %s",
                        (updated_source_id, updated_ngo_id, updated_source, updated_destination, updated_feedback, updated_rate, updated_people_helped, impact_id)
                    )
                    conn.commit()
                    st.success("Impact updated successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Impact not found. Please enter a valid IMPACT ID.")

    # 3. Delete an Impact
    elif operation == 'Delete Impact':
        st.write("### Delete Reviewt")
        impact_id = st.number_input("Enter IMPACT ID to delete", min_value=1)

        if st.button("Delete Reviewt"):
            try:
                c.execute("DELETE FROM IMPACT WHERE IMPACT_ID = %s", (impact_id,))
                conn.commit()
                if c.rowcount > 0:
                    st.success("Review deleted successfully!")
                else:
                    st.warning("IMPACT ID not found.")
            except Exception as e:
                st.error(f"Error: {e}")

    # 4. View a Single Impact
    elif operation == 'View  Details':
        st.write("### View Review  Details")
        impact_id = st.number_input("Enter IMPACT ID to view", min_value=1)
        c.execute("SELECT * FROM IMPACT WHERE IMPACT_ID = %s", (impact_id,))
        impact = c.fetchone()

        if impact:
            st.write(f"IMPACT ID: {impact[0]}")
            st.write(f"Source ID: {impact[1]}")
            st.write(f"NGO ID: {impact[2]}")
            st.write(f"Source: {impact[3]}")
            st.write(f"Destination: {impact[4]}")
            st.write(f"Feedback: {impact[5]}")
            st.write(f"Rate: {impact[6]}")
            st.write(f"People Helped: {impact[7]}")
        else:
            st.warning("Review not found. Please enter a valid Review ID.")

#ngo dashboard 
def display_ngo_statistics():
    st.title("NGO Impact Dashboard")
    
    try:
        conn = create_connection()
        
        # Create columns for key metrics
        col1, col2, col3 = st.columns(3)
        
        # Get total NGOs
        with col1:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM NGO")
            total_ngos = cursor.fetchone()[0]
            
            st.metric(
                label="Total NGOs",
                value=total_ngos,
                delta=None,
            )
        
        # Get total donations received
        with col2:
            cursor.execute("""
                SELECT SUM(QUANTITY) 
                FROM DONATIONS
            """)
            total_donations = cursor.fetchone()[0] or 0
            
            st.metric(
                label="Total Food Donated (kg)",
                value=f"{total_donations:,}",
                delta=None,
            )
        
        # Get total people helped
        with col3:
            cursor.execute("""
                SELECT SUM(PEOPLE_HELPED) 
                FROM IMPACT
            """)
            total_helped = cursor.fetchone()[0] or 0
            
            st.metric(
                label="Total People Helped",
                value=f"{total_helped:,}",
                delta=None,
            )
        
        # Donation Trends Over Time
        st.subheader("Donation Trends")
        cursor.execute("""
            SELECT 
                DATE(d.DATE_TIME) as date,
                SUM(dn.QUANTITY) as total_quantity
            FROM DONATES_TO d
            JOIN DONATIONS dn ON d.DONATION_ID = dn.DONATION_ID
            GROUP BY DATE(d.DATE_TIME)
            ORDER BY DATE(d.DATE_TIME)
        """)
        donation_trends = pd.DataFrame(cursor.fetchall(), columns=['date', 'total_quantity'])
        
        if not donation_trends.empty:
            fig = px.line(donation_trends, x='date', y='total_quantity',
                         title='Daily Donation Quantities',
                         labels={'date': 'Date', 'total_quantity': 'Total Quantity (kg)'})
            st.plotly_chart(fig)
        
        # NGO Category Distribution
        st.subheader("NGO Category Distribution")
        cursor.execute("""
            SELECT 
                COALESCE(CATEGORY_REQ, 'Unspecified') as category,
                COUNT(*) as count
            FROM NGO
            GROUP BY CATEGORY_REQ
        """)
        category_dist = pd.DataFrame(cursor.fetchall(), columns=['category', 'count'])
        
        if not category_dist.empty:
            fig = px.pie(category_dist, values='count', names='category',
                        title='NGO Distribution by Category')
            st.plotly_chart(fig)
        
        # Impact Ratings
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Impact Ratings Distribution")
            cursor.execute("""
                SELECT RATE, COUNT(*) as count
                FROM IMPACT
                GROUP BY RATE
                ORDER BY RATE
            """)
            ratings = pd.DataFrame(cursor.fetchall(), columns=['rating', 'count'])
            
            if not ratings.empty:
                fig = px.bar(ratings, x='rating', y='count',
                            title='Distribution of Impact Ratings',
                            labels={'rating': 'Rating', 'count': 'Number of Ratings'})
                st.plotly_chart(fig)
        
        with col2:
            st.subheader("Top NGOs by People Helped")
            cursor.execute("""
                SELECT 
                    n.NAME,
                    SUM(i.PEOPLE_HELPED) as total_helped
                FROM NGO n
                JOIN IMPACT i ON n.NGO_ID = i.NGO_ID
                GROUP BY n.NGO_ID, n.NAME
                ORDER BY total_helped DESC
                LIMIT 5
            """)
            top_ngos = pd.DataFrame(cursor.fetchall(), columns=['ngo', 'people_helped'])
            
            if not top_ngos.empty:
                fig = px.bar(top_ngos, x='ngo', y='people_helped',
                            title='Top NGOs by Impact',
                            labels={'ngo': 'NGO Name', 'people_helped': 'People Helped'})
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig)
        
        # Recent Activity Feed
        st.subheader("Recent NGO Activity")
        cursor.execute("""
            SELECT 
                n.NAME as ngo_name,
                d.QUANTITY as quantity,
                d.CATEGORY as category,
                dt.DATE_TIME as date_time
            FROM NGO n
            JOIN DONATIONS d ON n.NGO_ID = d.NGO_ID
            JOIN DONATES_TO dt ON d.DONATION_ID = dt.DONATION_ID
            ORDER BY dt.DATE_TIME DESC
            LIMIT 5
        """)
        recent_activities = cursor.fetchall()
        
        for activity in recent_activities:
            with st.expander(f"{activity[0]} - {activity[3].strftime('%Y-%m-%d %H:%M')}"):
                st.write(f"Received {activity[1]}kg of {activity[2]}")
        
        # Feedback Word Cloud (if you want to add this feature, you'll need to install wordcloud)
        st.subheader("Recent Feedback")
        cursor.execute("""
            SELECT 
                n.NAME as ngo_name,
                i.FEEDBACK as feedback,
                i.RATE as rating
            FROM NGO n
            JOIN IMPACT i ON n.NGO_ID = i.NGO_ID
            WHERE i.FEEDBACK IS NOT NULL
            ORDER BY i.IMPACT_ID DESC
            LIMIT 5
        """)
        feedbacks = cursor.fetchall()
        
        for feedback in feedbacks:
            with st.expander(f"{feedback[0]} - Rating: {'⭐' * feedback[2]}"):
                st.write(feedback[1])
                
    except mysql.connector.Error as err:
        st.error(f"Database Error: {err}")
    finally:
        if 'conn' in locals():
            conn.close()

# Function to render NGO details card
def display_ngo_card(ngo_data):
    with st.container():
        st.markdown("""
            <style>
                .ngo-card {
                    padding: 20px;
                    border-radius: 10px;
                    background-color: #f0f2f6;
                    margin-bottom: 20px;
                }
            </style>
        """, unsafe_allow_html=True)
        
        with st.expander(f"📍 {ngo_data['name']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Contact:** {ngo_data['contact_name']}")
                st.write(f"**Phone:** {ngo_data['contact']}")
            with col2:
                st.write(f"**Category:** {ngo_data['category_req'] or 'All Categories'}")
                st.write(f"**Email:** {ngo_data['email']}")
            
            if ngo_data['address']:
                st.write(f"**Address:** {ngo_data['address']}")

def handle_donation_request(ngo_id, required_category, required_quantity):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        # Call the backend function to get source
        cursor.execute("SELECT GetDonationSource(%s, %s, %s);", (ngo_id, required_category, required_quantity))
        source_id = cursor.fetchone()[0]  # Get the source_id from the result

        if source_id is None:
            # No source available
            st.error("No source available for the requested category and quantity.")
        else:
            # Source confirmed
            st.success(f"Donation source confirmed. Source ID: {source_id}. Donation processed successfully.")

    except Exception as e:
        st.error(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()

def main():
    # Establish a connection to the database
    conn = create_connection()
    if not conn:
        return

    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose a tab", ["Home", "Manage NGOs","Feedback","Donation "])

    if app_mode == "Home":
        st.subheader("Welcome to the Perishable Management System")
        st.write("Use the side menu to navigate to different sections.")
        display_ngo_statistics()

    elif app_mode == "Manage NGOs":
        manage_ngos(conn)

    elif app_mode == "Feedback":
        manage_impact(conn)

    elif app_mode == "Donation":
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
    # Close the database connection
    conn.close()

# Run the Streamlit app
if __name__ == "__main__":
    main()
