
import tempfile
from pathlib import Path
from storage import DataStore
from models import Book, Member, Loan
from main import issue_book, return_book, next_loan_id
from utils import today_iso, add_days_iso
import builtins
import pytest

# helper: create sample CSVs in tmpdir
def setup_sample_data(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    store = DataStore(data_dir)
    books = [Book(ISBN='9780132350884', Title='Clean Code', Author='Robert C. Martin', CopiesTotal=3, CopiesAvailable=3)]
    members = [Member(MemberID='1001', Name='Ananya', PasswordHash='pbkdf2$fake$salthash', Email='a@b.com', JoinDate=today_iso())]
    loans = []
    store.save_books(books)
    store.save_members(members)
    store.save_loans(loans)
    return store

def test_issue_and_return(tmp_path, monkeypatch):
    store = setup_sample_data(tmp_path)
    # simulate inputs for issue_book: isbn and member id
    inputs = iter(['9780132350884','1001'])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    issue_book(store)
    # after issue, copies available should be 2
    books = store.load_books()
    assert books[0].CopiesAvailable == 2

    # find loan id
    loans = store.load_loans()
    assert len(loans) == 1
    loan_id = loans[0].LoanID

    # simulate return (enter LoanID)
    inputs2 = iter([loan_id])
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs2))
    return_book(store)
    loans = store.load_loans()
    assert loans[0].ReturnDate != ""
    books = store.load_books()
    assert books[0].CopiesAvailable == 3
