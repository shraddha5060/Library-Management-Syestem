# Library-Management-Syestem
This is a Command Line Interface (CLI) Library Management System built in Python.

It allows librarians and members to manage books, register users, borrow, return, and check overdue loans.

Data is stored in CSV files for persistence.
.

## 🚀 Features
👩‍🏫 For Librarians:
Add new books

Remove books

Register members

Issue and return books

View overdue books

## 👩‍💻 For Members:
Search books by title/author
Borrow books
View active and returned loans

## 🛠️ Tech Stack

Python 3.x

CSV file storage

## 📂 Project Structure
library-management-system/
│── main.py          # Entry point
│── models.py        # Book, Member, Loan classes
│── storage.py       # CSV file handling
│── auth.py          # Password hashing & verification
│── utils.py         # Date utilities
│── data/            # CSV files stored here
│   ├── books.csv
│   ├── members.csv
│   ├── loans.csv
│── README.md        # Project documentation

## Future Improvements

Replace CSV with SQLite or MySQL database

Add GUI or Web interface

Fine-grained access control
