from enum import Enum


class Entity(str, Enum):
    User = "User"
    Product = "Product"
    Category = "Category"
    Role = "Role"
    ANY = "ANY"


class Permission(str, Enum):
    Read = "Read"
    Create = "Create"
    Update = "Update"
    Delete = "Delete"
    ALL = "ALL"
