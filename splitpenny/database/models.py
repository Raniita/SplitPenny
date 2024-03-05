from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, Table
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func

class Base(DeclarativeBase):
    pass

# Association Table for Many-to-Many relationship between User and Bucket
bucket_member = Table('bucket_member', Base.metadata,
                      Column('user_id', ForeignKey('user.id'), primary_key=True),
                      Column('bucket_id', ForeignKey('bucket.id'), primary_key=True))

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(20), unique=True)
    full_name = Column(String(50), nullable=True)
    password = Column(String(128), nullable=True)
    is_active = Column(Boolean, default=True)
    telegram_id = Column(Integer, unique=True, nullable=True)
    telegram_username = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    modified_at = Column(DateTime(timezone=True), onupdate=func.now())
    owned_buckets = relationship("Bucket", back_populates="owner")
    expenses_paid = relationship("Expense", foreign_keys="[Expense.paid_by_id]", back_populates="paid_by")
    expenses_received = relationship("Expense", foreign_keys="[Expense.paid_to_id]", back_populates="paid_to")
    member_buckets = relationship("Bucket", secondary=bucket_member, back_populates="members", lazy="subquery")
    
class Bucket(Base):
    __tablename__ = "bucket"
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner = relationship("User", back_populates="owned_buckets")
    members = relationship("User", secondary=bucket_member, back_populates="member_buckets")
    expenses = relationship("Expense", back_populates="bucket")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class Expense(Base):
    __tablename__ = 'expense'
    id = Column(Integer, primary_key=True)
    description = Column(String(255))
    amount = Column(Numeric(10, 2))
    split_type = Column(String(50))
    bucket_id = Column(Integer, ForeignKey('bucket.id'))
    bucket = relationship("Bucket", back_populates="expenses")
    paid_by_id = Column(Integer, ForeignKey('user.id'))
    paid_by = relationship("User", foreign_keys=[paid_by_id], back_populates="expenses_paid")
    paid_to_id = Column(Integer, ForeignKey('user.id'), nullable=True)  # nullable for general expenses
    paid_to = relationship("User", foreign_keys=[paid_to_id], back_populates="expenses_received")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    