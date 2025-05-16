import streamlit as st
import mysql.connector
import pandas as pd

# Initialize session state
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'total_price' not in st.session_state:
    st.session_state.total_price = 0

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host =  "sql12.freesqldatabase.com",
        user =  "sql12779229",
        password = "ZRXgDP3VQY",
        database = "sql12779229",
        port =  3306
    )

# ===================== ADMIN PANEL =======================
def admin_panel():
    st.subheader("Admin Panel")

    admin_username = "Deepak Prajapat"
    admin_password = "@deep7067"

    n = st.text_input("Enter Your Name ")
    p = st.text_input("Enter Your Password", type="password")

    if st.button("Enter"):
        if n == admin_username and p == admin_password:
            st.session_state.admin_authenticated = True
        else:
            st.error("❌ Invalid credentials")

    if st.session_state.get("admin_authenticated", False):
        st.success("✅ Welcome Deepak")
        options = ["Add Product", "Show Products", "Update Product", "Delete Product"]
        choice = st.selectbox("Choose an operation:", options)
        st.session_state.admin_choice = choice

        db = get_db_connection()
        cursor = db.cursor()

        # Store choice separately to persist across reruns
        choice = st.session_state.get("admin_choice")

        if choice == "Add Product":
            product_name = st.text_input("Product Name")
            price = st.number_input("Product Price", min_value=0)
            quantity = st.number_input("Product Quantity", min_value=0)

            if st.button("Add Product"):
                if product_name:
                    total = price * quantity
                    query = "INSERT INTO product3(name, price, quantity, total) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (product_name, price, quantity, total))
                    db.commit()
                    st.success("✅ Product added successfully!")
                else:
                    st.warning("Please enter a valid product name.")

        elif choice == "Show Products":
            cursor.execute("SELECT * FROM product3")
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=["Name", "Price", "Quantity", "Total"])
            st.dataframe(df)

        elif choice == "Update Product":
            cursor.execute("SELECT * FROM product3")
            data = cursor.fetchall()

            if data:
                df = pd.DataFrame(data, columns=["Name", "Price", "Quantity", "Total"])
                st.dataframe(df)

                product_names = [row[0] for row in data]
                selected_product = st.selectbox("Select Product by Name", product_names)

                new_price = st.number_input("New Price", min_value=0.0, step=1.0)
                new_qty = st.number_input("New Quantity", min_value=0, step=1)

                if st.button("Update Product"):
                    total = new_price * new_qty
                    query = "UPDATE product3 SET price=%s, quantity=%s, total=%s WHERE name=%s"
                    cursor.execute(query, (new_price, new_qty, total, selected_product))
                    db.commit()
                    st.success(f"✅ Product '{selected_product}' updated successfully!")

        elif choice == "Delete Product":
            cursor.execute("SELECT * FROM product3")
            data = cursor.fetchall()

            if data:
                df = pd.DataFrame(data, columns=["Name", "Price", "Quantity", "Total"])
                st.dataframe(df)

                product_names = [row[0] for row in data]
                selected_product = st.selectbox("Select Product to Delete", product_names)

                if st.button("Delete Product"):
                    query = "DELETE FROM product3 WHERE name = %s"
                    cursor.execute(query, (selected_product,))
                    db.commit()
                    st.success(f"🗑️ Product '{selected_product}' deleted successfully!")
            else:
                st.warning("No products available to delete.")


# ===================== USER PANEL =======================
def user_panel():
    st.subheader("User Panel - Shop Now")
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("SELECT name, price, quantity FROM product3 WHERE quantity > 0")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["Name", "Price", "Quantity"])
    st.dataframe(df)
    Available_product = [row[0] for row in data]
    product_id = st.selectbox("Select Your Product" , Available_product)
    qty = st.number_input("Enter Quantity", min_value=1)

    if st.button("Add to Cart"):
        cursor.execute("SELECT name, price, quantity FROM product3 WHERE name=%s", (product_id,))
        product = cursor.fetchone()

        if product:
            name, price, available_qty = product
            if qty <= available_qty:
                total = qty * price
                st.session_state.cart.append((name, qty, price, total))
                st.session_state.total_price += total

                # Update database quantity
                new_qty = available_qty - qty
                cursor.execute("UPDATE product3 SET quantity=%s, total=price*%s WHERE name=%s", (new_qty, new_qty, product_id))
                db.commit()
                st.success("🛒 Product added to cart.")
            else:
                st.warning("Not enough stock available.")
        else:
            st.error("Product not found.")

    if st.button("View Cart"):
        if st.session_state.cart:
            st.write("🛍️ **Your Cart:**")
            cart_df = pd.DataFrame(st.session_state.cart, columns=["Product", "Qty", "Price", "Total"])
            st.dataframe(cart_df)
            st.write("### 💰 Total Price: ₹", st.session_state.total_price)
        else:
            st.info("Your cart is empty.")
    if st.button("Bill"):
        if st.session_state.cart:
            st.session_state.show_bill_form = True
        else:
            st.info("🛒 Cart is empty. Add items first.")

    if st.session_state.get("show_bill_form", False):
        st.subheader("🧾 Generate Bill")
        name = st.text_input("Enter your name to generate bill:")
        if st.button("Generate Bill"):
            if name.strip() == "":
                st.warning("⚠️ Please enter your name to generate the bill.")
            else:
                st.success(f"🧾 Bill for {name}")
                cart_df = pd.DataFrame(st.session_state.cart, columns=["Product", "Qty", "Price", "Total"])
                st.dataframe(cart_df)
                st.write("### Grand Total: ₹", st.session_state.total_price)
                st.write("✅ Thank you for shopping with us!")

                # Clear cart and form
                st.session_state.cart = []
                st.session_state.total_price = 0
                st.session_state.show_bill_form = False

# ===================== MAIN APP =======================
def main():
    st.title("🛒 Grocery Shop Management System")
    st.markdown("<small>Build By Deepak Prajapati</small>", unsafe_allow_html=True)
    mode = st.sidebar.selectbox("Login as", ["User", "Admin"])
    if mode == "Admin":
        admin_panel()
    else:
        user_panel()

if __name__ == '__main__':
    main()
