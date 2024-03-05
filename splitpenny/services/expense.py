from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from collections import defaultdict
from typing import Dict
from decimal import Decimal
from datetime import datetime

from splitpenny.database.models import Bucket, User, Expense
from splitpenny.schemas.expense import SplitType

async def calculate_expenses_status(db: AsyncSession, bucket_id: int, show_as_usernames: bool) -> Dict[str, Dict]:
    # Fetch the bucket, its members, and expenses
    bucket_result = await db.execute(select(Bucket).where(Bucket.id == bucket_id).options(selectinload(Bucket.members), selectinload(Bucket.expenses)))
    bucket = bucket_result.scalars().first()
    if not bucket:
        return {"error": "Bucket not found"}
    
    transactions = defaultdict(lambda: defaultdict(lambda: Decimal(0)))

    # First pass: Calculate the transactions based on expenses and settlements
    for expense in bucket.expenses:
        split_amount = expense.amount / Decimal(len(bucket.members)) if expense.split_type != "Settlement" else expense.amount
        for member in bucket.members:
            if expense.split_type != "Settlement":
                if member.id != expense.paid_by_id:  # Skip the payer for equal splits
                    transactions[expense.paid_by_id][member.id] += split_amount
                    transactions[member.id][expense.paid_by_id] -= split_amount
            else:
                if expense.paid_to_id:  # Ensure there's a payee for the settlement
                    transactions[expense.paid_by_id][expense.paid_to_id] -= split_amount
                    transactions[expense.paid_to_id][expense.paid_by_id] += split_amount

    # Optional: Simplify or adjust transactions before converting IDs to usernames
    transactions = await simplify_transactions(transactions=transactions)

    # Second pass: Convert user IDs to usernames if required
    if show_as_usernames:
        user_ids = set(transactions.keys()) | {peer_id for peers in transactions.values() for peer_id in peers}
        users_result = await db.execute(select(User.id, User.username).where(User.id.in_(user_ids)))
        user_id_to_username = {id: username for id, username in users_result}
        
        # Convert transactions to use usernames
        transactions_with_usernames = defaultdict(lambda: defaultdict(Decimal))
        for payer_id, peers in transactions.items():
            payer_username = user_id_to_username.get(payer_id, str(payer_id))
            for peer_id, amount in peers.items():
                peer_username = user_id_to_username.get(peer_id, str(peer_id))
                transactions_with_usernames[payer_username][peer_username] = amount
        transactions = transactions_with_usernames

    transactions_with_status = {}

    for payer, peers in transactions.items():
        total_owed = sum(amount for amount in peers.values() if amount < 0)
        is_settled_up = total_owed == Decimal(0)
        transactions_with_status[payer] = {
            "transactions": peers,
            "is_settled_up": is_settled_up
        }

    # If showing as usernames, replace IDs with usernames in the structure
    if show_as_usernames:
        user_ids = set(transactions.keys()) | {peer_id for peers in transactions.values() for peer_id in peers}
        users_result = await db.execute(select(User.id, User.username).where(User.id.in_(user_ids)))
        user_id_to_username = {id: username for id, username in users_result}

        transactions_with_usernames_and_status = {}
        for payer_id, details in transactions_with_status.items():
            payer_username = user_id_to_username.get(payer_id, str(payer_id))
            peer_transactions = {user_id_to_username.get(peer_id, str(peer_id)): amount for peer_id, amount in details["transactions"].items()}
            transactions_with_usernames_and_status[payer_username] = {
                "transactions": peer_transactions,
                "is_settled_up": details["is_settled_up"]
            }
        transactions_with_status = transactions_with_usernames_and_status

    return {
        "transactions": transactions_with_status
    }

async def simplify_transactions(transactions):
    for user_id in transactions:
        for peer_id, amount in transactions[user_id].items():
            if transactions[peer_id][user_id] > 0:
                # If both owe each other, reduce the debt to a single direction
                if amount > transactions[peer_id][user_id]:
                    transactions[user_id][peer_id] -= transactions[peer_id][user_id]
                    transactions[peer_id][user_id] = Decimal(0)
                else:
                    transactions[peer_id][user_id] -= amount
                    transactions[user_id][peer_id] = Decimal(0)
    return transactions

async def settle_up(db: AsyncSession, bucket_id: int, paid_by_id: int, paid_to_id: int, amount: float, description: str | None):
    settlement_expense = Expense(
        description=description,
        amount=amount,
        split_type=SplitType.SETTLEMENT,
        bucket_id=bucket_id,
        paid_by_id=paid_by_id,
        paid_to_id=paid_to_id,
        created_at=datetime.utcnow()
    )

    db.add(settlement_expense)
    await db.commit()
