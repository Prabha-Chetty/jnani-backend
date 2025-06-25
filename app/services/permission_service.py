from pymongo.database import Database

def get_all_permissions(db: Database):
    # In a real app, you might have a predefined list of permissions
    # or manage them in the database.
    # For now, we'll return a hardcoded list.
    permissions = [
        {"id": "manage_users", "name": "Manage Users", "description": "Create, edit, and delete users."},
        {"id": "manage_roles", "name": "Manage Roles", "description": "Create, edit, and delete roles."},
        {"id": "manage_faculties", "name": "Manage Faculties", "description": "Manage faculty records."},
        {"id": "manage_students", "name": "Manage Students", "description": "Manage student records."},
        {"id": "manage_content", "name": "Manage Content", "description": "Manage website content."},
    ]
    return permissions 