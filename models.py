# models.py
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import date

@dataclass
class Book:
    ISBN: str
    Title: str
    Author: str
    CopiesTotal: int
    CopiesAvailable: int

    @classmethod
    def from_csv_row(cls, row: dict):
        return cls(
            ISBN=row['ISBN'],
            Title=row['Title'],
            Author=row['Author'],
            CopiesTotal=int(row['CopiesTotal']),
            CopiesAvailable=int(row['CopiesAvailable'])
        )

    def to_csv_row(self):
        d = asdict(self)
        d['CopiesTotal'] = str(self.CopiesTotal)
        d['CopiesAvailable'] = str(self.CopiesAvailable)
        return d

@dataclass
class Member:
    MemberID: str
    Name: str
    PasswordHash: str
    Email: str
    JoinDate: str  # ISO YYYY-MM-DD

    @classmethod
    def from_csv_row(cls, row: dict):
        return cls(
            MemberID=row['MemberID'],
            Name=row['Name'],
            PasswordHash=row['PasswordHash'],
            Email=row['Email'],
            JoinDate=row['JoinDate']
        )

    def to_csv_row(self):
        return asdict(self)

@dataclass
class Loan:
    LoanID: str
    MemberID: str
    ISBN: str
    IssueDate: str  # ISO
    DueDate: str
    ReturnDate: Optional[str] = ""  # empty string if not returned

    @classmethod
    def from_csv_row(cls, row: dict):
        return cls(
            LoanID=row['LoanID'],
            MemberID=row['MemberID'],
            ISBN=row['ISBN'],
            IssueDate=row['IssueDate'],
            DueDate=row['DueDate'],
            ReturnDate=row.get('ReturnDate', '')
        )

    def to_csv_row(self):
        return asdict(self)
