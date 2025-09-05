# storage.py
import csv
from pathlib import Path
from typing import List, Dict
from models import Book, Member, Loan

def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        return [row for row in reader]

def write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

class DataStore:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.books_file = self.data_dir / 'books.csv'
        self.members_file = self.data_dir / 'members.csv'
        self.loans_file = self.data_dir / 'loans.csv'
        self._cache = {}

    # Books
    def load_books(self) -> List[Book]:
        rows = read_csv(self.books_file)
        return [Book.from_csv_row(r) for r in rows]

    def save_books(self, books: List[Book]):
        rows = [b.to_csv_row() for b in books]
        fieldnames = ['ISBN','Title','Author','CopiesTotal','CopiesAvailable']
        write_csv(self.books_file, rows, fieldnames)

    # Members
    def load_members(self) -> List[Member]:
        rows = read_csv(self.members_file)
        return [Member.from_csv_row(r) for r in rows]

    def save_members(self, members: List[Member]):
        rows = [m.to_csv_row() for m in members]
        fieldnames = ['MemberID','Name','PasswordHash','Email','JoinDate']
        write_csv(self.members_file, rows, fieldnames)

    # Loans
    def load_loans(self) -> List[Loan]:
        rows = read_csv(self.loans_file)
        return [Loan.from_csv_row(r) for r in rows]

    def save_loans(self, loans: List[Loan]):
        rows = [l.to_csv_row() for l in loans]
        fieldnames = ['LoanID','MemberID','ISBN','IssueDate','DueDate','ReturnDate']
        write_csv(self.loans_file, rows, fieldnames)
