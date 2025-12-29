
class AuthService:
    """
    Mock Authentication Service for Leevin OS.
    Handles user login and role-based access control.
    """
    
    # Mock Database
    USERS = {
        "admin": {
            "password": "123", # In production, hash this!
            "role": "Admin",
            "name": "Super Admin"
        },
        "writer": {
            "password": "123",
            "role": "Protocol Writer",
            "name": "Dr. Writer"
        },
        "reviewer": {
            "password": "123",
            "role": "Protocol Reviewer",
            "name": "Dr. Reviewer"
        },
        "user": {
            "password": "123",
            "role": "ClinicalOps",
            "name": "Dr. Smith"
        }
    }
    
    # Role Permissions
    PERMISSIONS = {
        "Admin": [
            "Dashboard",
            "Module 1: The Cleaner",
            "Module 2: The Auto-Coder",
            "Module 3: The Builder"
        ],
        "Protocol Writer": [
            "Protocol Drafter",
            "Protocol Digitizer"
        ],
        "Protocol Reviewer": [
            "Protocol Review",
            "Audit Trail"
        ],
        "ClinicalOps": [
            "Dashboard",
            "Module 1: The Cleaner",
            "Module 2: The Auto-Coder"
        ]
    }

    @staticmethod
    def login(username, password):
        """
        Verifies credentials and returns user object if successful.
        """
        user = AuthService.USERS.get(username)
        if user and user['password'] == password:
            return {
                "username": username,
                "role": user["role"],
                "name": user["name"]
            }
        return None

    @staticmethod
    def get_modules_by_role(role):
        """
        Returns list of allowed modules for a given role.
        """
        return AuthService.PERMISSIONS.get(role, [])
