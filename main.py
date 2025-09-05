# main.py
import argparse
from pathlib import Path
from storage import DataStore
from models import Book, Member, Loan
from auth import hash_password, verify_password
from utils import today_iso, add_days_iso, pretty_date_iso
import uuid
from datetime import date

SESSION = {'user': None, 'role': None}

def next_loan_id(loans):
    # simple incremental based on len+1 or UUID
    return str(uuid.uuid4())

def find_book(books, isbn):
    for b in books:
        if b.ISBN == isbn:
            return b
    return None

def add_book(store: DataStore):
    books = store.load_books()
    isbn = input("ISBN: ").strip()
    if find_book(books, isbn):
        print("ISBN already exists.")
        return
    title = input("Title: ").strip()
    author = input("Author: ").strip()
    try:
        total = int(input("CopiesTotal: ").strip())
    except ValueError:
        print("Invalid number.")
        return
    book = Book(ISBN=isbn, Title=title, Author=author, CopiesTotal=total, CopiesAvailable=total)
    books.append(book)
    store.save_books(books)
    print("Book added.")

def remove_book(store: DataStore):
    books = store.load_books()
    isbn = input("ISBN to remove: ").strip()
    book = find_book(books, isbn)
    if not book:
        print("Not found.")
        return
    books = [b for b in books if b.ISBN != isbn]
    store.save_books(books)
    print("Removed.")

def register_member(store: DataStore):
    members = store.load_members()
    mid = input("MemberID: ").strip()
    if any(m.MemberID == mid for m in members):
        print("MemberID exists.")
        return
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    confirm = input("Confirm Password: ").strip()
    if password != confirm:
        print("Password mismatch.")
        return
    ph = hash_password(password)
    member = Member(MemberID=mid, Name=name, PasswordHash=ph, Email=email, JoinDate=today_iso())
    members.append(member)
    store.save_members(members)
    print("Member registered.")

def login(store: DataStore):
    role = input("Role (librarian/member): ").strip().lower()
    if role not in ('librarian','member'):
        print("Invalid role.")
        return False
    if role == 'librarian':
        # for demo: simple librarian static password (in real app: separate user table)
        user = input("Librarian username: ").strip()
        pwd = input("Password: ").strip()
        # demo credentials
        if user == 'admin' and pwd == 'admin':
            SESSION['user'] = 'admin'
            SESSION['role'] = 'librarian'
            return True
        print("Bad librarian creds.")
        return False
    else:
        members = store.load_members()
        mid = input("MemberID: ").strip()
        pwd = input("Password: ").strip()
        member = next((m for m in members if m.MemberID == mid), None)
        if not member:
            print("No such member.")
            return False
        if verify_password(pwd, member.PasswordHash):
            SESSION['user'] = member.MemberID
            SESSION['role'] = 'member'
            print(f"Welcome {member.Name}")
            return True
        print("Bad password.")
        return False

def issue_book(store: DataStore):
    books = store.load_books()
    members = store.load_members()
    loans = store.load_loans()
    isbn = input("ISBN to issue: ").strip()
    member_id = input("Member ID: ").strip()
    book = find_book(books, isbn)
    if not book:
        print("Book not found.")
        return
    if book.CopiesAvailable <= 0:
        print("No copies available.")
        return
    if not any(m.MemberID == member_id for m in members):
        print("Member not found.")
        return
    # create loan
    loan_id = next_loan_id(loans)
    issue_date = today_iso()
    due_date = add_days_iso(issue_date, 14)
    loan = Loan(LoanID=loan_id, MemberID=member_id, ISBN=isbn, IssueDate=issue_date, DueDate=due_date, ReturnDate="")
    loans.append(loan)
    # update book
    book.CopiesAvailable -= 1
    store.save_loans(loans)
    store.save_books(books)
    print(f"\u2705 Book issued. Due on {pretty_date_iso(due_date)}.")

def return_book(store: DataStore):
    loans = store.load_loans()
    books = store.load_books()
    loan_id = input("LoanID (or MemberID+ISBN) to return: ").strip()
    loan = None
    # try direct match
    for l in loans:
        if l.LoanID == loan_id:
            loan = l
            break
    if not loan:
        # allow MemberID+ISBN
        parts = loan_id.split()
        if len(parts) == 2:
            m, isbn = parts
            for l in loans:
                if l.MemberID == m and l.ISBN == isbn and l.ReturnDate == "":
                    loan = l
                    break
    if not loan:
        print("Loan not found.")
        return
    if loan.ReturnDate:
        print("Already returned.")
        return
    loan.ReturnDate = today_iso()
    # restore book
    b = find_book(books, loan.ISBN)
    if b:
        b.CopiesAvailable += 1
    store.save_loans(loans)
    store.save_books(books)
    print("Return recorded.")

def overdue_report(store: DataStore):
    loans = store.load_loans()
    overdue = []
    from utils import parse_iso
    for l in loans:
        if (not l.ReturnDate) and parse_iso(l.DueDate) < date.today():
            overdue.append(l)
    if not overdue:
        print("No overdue loans.")
        return
    print("Overdue:")
    for l in overdue:
        print(f"Loan {l.LoanID} Member {l.MemberID} ISBN {l.ISBN} Due {l.DueDate}")

def search_catalog(store: DataStore):
    books = store.load_books()
    q = input("Search title/author keyword: ").strip().lower()
    results = [b for b in books if q in b.Title.lower() or q in b.Author.lower()]
    if not results:
        print("No results.")
        return
    for b in results:
        print(f"{b.ISBN} | {b.Title} | {b.Author} | {b.CopiesAvailable}/{b.CopiesTotal}")

def my_loans(store: DataStore):
    loans = store.load_loans()
    user = SESSION.get('user')
    my = [l for l in loans if l.MemberID == user]
    if not my:
        print("No loans.")
        return
    for l in my:
        status = "Returned" if l.ReturnDate else f"Due {l.DueDate}"
        print(f"{l.LoanID} | {l.ISBN} | Issue {l.IssueDate} | {status}")

def librarian_menu(store: DataStore):
    while True:
        print("\n=== Librarian Dashboard ===")
        print("1. Add Book\n2. Register Member\n3. Issue Book\n4. Return Book\n5. Overdue List\n6. Logout")
        choice = input("> ").strip()
        if choice == '1':
            add_book(store)
        elif choice == '2':
            register_member(store)
        elif choice == '3':
            issue_book(store)
        elif choice == '4':
            return_book(store)
        elif choice == '5':
            overdue_report(store)
        elif choice == '6':
            SESSION.clear()
            break
        else:
            print("Bad choice.")

def member_menu(store: DataStore):
    while True:
        print("\n=== Member Dashboard ===")
        print("1. Search catalogue\n2. Borrow book\n3. My loans\n4. Logout")
        choice = input("> ").strip()
        if choice == '1':
            search_catalog(store)
        elif choice == '2':
            # borrow == issue (member can borrow self)
            isbn = input("ISBN to borrow: ").strip()
            member_id = SESSION['user']
            # reuse issue flow but simplified
            books = store.load_books()
            book = find_book(books, isbn)
            if not book:
                print("Book not found.")
            elif book.CopiesAvailable <= 0:
                print("No copies.")
            else:
                loans = store.load_loans()
                loan_id = next_loan_id(loans)
                issue_date = today_iso()
                due_date = add_days_iso(issue_date, 14)
                loan = Loan(LoanID=loan_id, MemberID=member_id, ISBN=isbn, IssueDate=issue_date, DueDate=due_date, ReturnDate="")
                loans.append(loan)
                book.CopiesAvailable -= 1
                store.save_loans(loans)
                store.save_books(books)
                print(f"Borrowed. Due {pretty_date_iso(due_date)}")
        elif choice == '3':
            my_loans(store)
        elif choice == '4':
            SESSION.clear()
            break
        else:
            print("Bad choice.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', default='./data')
    args = parser.parse_args()
    store = DataStore(Path(args.data_dir))

    print("Welcome to CLI Library")
    while True:
        print("\n1. Login\n2. Exit")
        c = input("> ").strip()
        if c == '1':
            if login(store):
                role = SESSION.get('role')
                if role == 'librarian':
                    librarian_menu(store)
                elif role == 'member':
                    member_menu(store)
        elif c == '2':
            break

if __name__ == '__main__':
    main()
