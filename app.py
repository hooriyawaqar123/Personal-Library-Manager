import streamlit as st
import sqlite3

# Connect to the database
def connect_db():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            author TEXT,
            year INTEGER,
            genre TEXT,
            read INTEGER
        )
    """)
    conn.commit()
    return conn, cursor

# Predefined list of genres
GENRES = [
    "Fantasy", "Horror", "Mystery", "Romance novel", "Science fiction", "Thriller",
    "Historical Fiction", "Adventure fiction", "Young adult", "Children's literature", "Fiction",
    "Historical", "Literary fiction", "Comedy", "Dystopian Fiction", "Gothic fiction",
    "Magic realism", "Short story", "Autobiography and memoir", "Contemporary fantasy",
    "Dark fantasy", "Romantic fantasy", "Graphic novel"
]

# Add a book to the database
def add_book(title, author, year, genre, read_status):
    if not title or not author or genre not in GENRES or year <= 800:
        return False
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM books WHERE title = ?", (title,))
    existing_book = cursor.fetchone()
    if existing_book:
        conn.close()
        return False  # Prevent duplicate titles
    cursor.execute("INSERT INTO books (title, author, year, genre, read) VALUES (?, ?, ?, ?, ?)",
                   (title, author, year, genre, int(read_status)))
    conn.commit()
    conn.close()
    return True

# Remove a book from the database
def remove_book(title):
    if not title:
        return False
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM books WHERE title = ?", (title,))
    book = cursor.fetchone()
    if not book:
        conn.close()
        return False  # Book does not exist
    cursor.execute("DELETE FROM books WHERE title = ?", (title,))
    conn.commit()
    conn.close()
    return True

# Search for books in the database
def search_books(query, search_by):
    conn, cursor = connect_db()
    if search_by == "Title":
        cursor.execute("SELECT * FROM books WHERE title LIKE ?", ("%" + query + "%",))
    else:
        cursor.execute("SELECT * FROM books WHERE author LIKE ?", ("%" + query + "%",))
    results = cursor.fetchall()
    conn.close()
    return results

# Get all books from the database
def get_all_books():
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return books

# Get statistics
def get_statistics():
    conn, cursor = connect_db()
    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM books WHERE read = 1")
    read_books = cursor.fetchone()[0]
    conn.close()
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0
    return total_books, percent_read

# Streamlit UI
st.title("📖 Personal Library Manager")

# Sidebar Navigation
menu = st.sidebar.radio("📌 Navigation", ["Add Book", "Remove Book", "Search Book", "View All Books", "Statistics"])

if menu == "Add Book":
    st.header("➕ Add a Book")
    title = st.text_input("📖 Enter the book title:")
    author = st.text_input("✍️ Enter the author:")
    year = st.number_input("📅 Enter the publication year:", min_value=800, step=1)
    genre = st.selectbox("🏷️ Select the genre:", GENRES)
    read_status = st.checkbox("✅ Have you read this book?")
    if st.button("📥 Add Book"):
        if add_book(title, author, int(year), genre, read_status):
            st.success("🎉 Book added successfully!")
        else:
            st.error("⚠️ Book already exists or fields are incorrect!")

elif menu == "Remove Book":
    st.header("❌ Remove a Book")
    remove_title = st.text_input("🗑️ Enter the title of the book to remove:")
    if st.button("🗑️ Remove Book"):
        if remove_book(remove_title):
            st.success("✅ Book removed successfully!")
        else:
            st.error("⚠️ Book not found!")

elif menu == "Search Book":
    st.header("🔎 Search for a Book")
    search_option = st.radio("🔍 Search by:", ("Title", "Author"))
    search_query = st.text_input("💬 Enter the search term:")
    if st.button("🔎 Search"):
        results = search_books(search_query, search_option)
        if results:
            for book in results:
                st.write(f"📖 {book[1]} by ✍️ {book[2]} ({book[3]}) - 🏷️ {book[4]} - {'✅ Read' if book[5] else '📖 Unread'}")
        else:
            st.warning("⚠️ No matching books found!")

elif menu == "View All Books":
    st.header("📚 All Books in Library")
    books = get_all_books()
    if not books:
        st.write("📭 Your library is empty!")
    else:
        for index, book in enumerate(books, start=1):
            st.write(f"{index}. 📖 {book[1]} by ✍️ {book[2]} ({book[3]}) - 🏷️ {book[4]} - {'✅ Read' if book[5] else '📖 Unread'}")

elif menu == "Statistics":
    st.header("📊 Library Statistics")
    total_books, percent_read = get_statistics()
    st.write(f"📚 Total books: {total_books}\n📖 Percentage read: {percent_read:.2f}%")
