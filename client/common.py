from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class Repo:
    name: str
    path: 'Path'

class Role(Enum):
    User = 'user'
    Admin = 'admin'
    Owner = 'owner'

    def is_admin(self):
        return self != self.User
