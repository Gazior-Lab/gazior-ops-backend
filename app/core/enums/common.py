from enum import Enum as PyEnum


class InvitationStatus(PyEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class WorkspaceMemberRole(PyEnum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"
    GUEST = "GUEST"


class InitiativeHealthStatus(PyEnum):
    ON_TRACK = "ON_TRACK"
    IN_REVIEW = "IN_REVIEW"
    NEEDS_FOCUS = "NEEDS_FOCUS"
    COMPLETED = "COMPLETED"



class ProjectStatus(PyEnum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class ProjectVisibility(PyEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"



class CycleStatus(PyEnum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


# UserRoleEnum
# WorkspaceRoleEnum
# TaskStatusEnum
# TaskPriorityEnum
# ProjectStatusEnum
# InvitationStatusEnum
# VisibilityEnum