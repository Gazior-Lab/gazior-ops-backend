import enum as pyEnum


class InvitationStatus(PyEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class WorkspaceMemberRole(pyEnum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"
    GUEST = "GUEST"




# UserRoleEnum
# WorkspaceRoleEnum
# TaskStatusEnum
# TaskPriorityEnum
# ProjectStatusEnum
# InvitationStatusEnum
# VisibilityEnum