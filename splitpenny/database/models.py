from tortoise import fields, models

# Modelo de usuarios
class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    username = fields.CharField(max_length=20, unique=True)
    full_name = fields.CharField(max_length=50, null=True)
    password = fields.CharField(max_length=128, null=True)
    is_active = fields.BooleanField(default=True)
    telegram_id = fields.IntField(null=True, unique=True)
    telegram_username = fields.CharField(max_lenght=50, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    owned_buckets = fields.ReverseRelation["Bucket"]
    member_buckets = fields.ManyToManyField("models.Bucket", related_name="members", through="bucket_member")
    expenses_paid = fields.ReverseRelation["Expense"]
    
# Modelo de Bucket
class Bucket(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    owner = fields.ForeignKeyField("models.User", related_name="owned_buckets")
    members = fields.ManyToManyField("models.User", related_name="member_buckets", through="bucket_member")
    expenses = fields.ReverseRelation["Expense"]
    created_at = fields.DatetimeField(auto_now_add=True)

# Modelo de Expense
class Expense(models.Model):
    id = fields.IntField(pk=True)
    description = fields.CharField(max_length=255)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    split_type = fields.CharField(max_length=50)
    bucket = fields.ForeignKeyField("models.Bucket", related_name="expenses")
    paid_by = fields.ForeignKeyField("models.User", related_name="expenses_paid")
    created_at = fields.DatetimeField(auto_now_add=True)