import enum


class UserRole(str, enum.Enum):
    ORGANIZER = "ORGANIZER"
    PLAYER = "PLAYER"

class ParticipationType(str, enum.Enum):
    TEAM = "TEAM"
    INDIVIDUAL = "INDIVIDUAL"


class TournamentFormat(str, enum.Enum):
    ROUND_ROBIN = "ROUND_ROBIN"
    KNOCKOUT = "KNOCKOUT"


class TournamentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    REGISTRATION_OPEN = "REGISTRATION_OPEN"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"