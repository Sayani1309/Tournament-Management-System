import enum


class UserRole(str, enum.Enum):
    ORGANIZER = "ORGANIZER"
    PLAYER = "PLAYER"