from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.team import TeamRepository
from app.repositories.team_member import TeamMemberRepository
from app.repositories.workspace_member import WorkspaceMemberRepository
from app.models.team import Team
from app.models.team_member import TeamMember
from app.schemas.team import TeamCreate, TeamUpdate
from app.core.enums.common import TeamMemberRole, WorkspaceMemberRole
from app.core.exceptions import (
    DuplicateError,
    ObjectNotFoundError,
    ForbiddenError,
)


class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.team_repo = TeamRepository(db)
        self.member_repo = TeamMemberRepository(db)
        self.ws_member_repo = WorkspaceMemberRepository(db)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _require_workspace_admin(self, workspace_id: int, user_id: int) -> None:
        """Raise ForbiddenError if the user is not an OWNER or ADMIN of the workspace."""
        ws_member = await self.ws_member_repo.get_by_user_and_workspace(
            user_id=user_id, workspace_id=workspace_id
        )
        if not ws_member or ws_member.role not in [
            WorkspaceMemberRole.OWNER,
            WorkspaceMemberRole.ADMIN,
        ]:
            raise ForbiddenError(
                message="Only workspace owners and admins can manage teams"
            )

    async def _require_team_exists(self, team_id: int) -> Team:
        """Return team or raise ObjectNotFoundError."""
        team = await self.team_repo.get_by_id(team_id)
        if not team:
            raise ObjectNotFoundError(
                message=f"Team {team_id} not found",
                details={"team_id": team_id},
            )
        return team

    # ------------------------------------------------------------------
    # Team CRUD
    # ------------------------------------------------------------------

    async def get_team(self, team_id: int) -> Optional[Team]:
        return await self.team_repo.get_by_id(team_id)

    async def get_teams(
        self,
        workspace_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        teams, total = await self.team_repo.get_all_by_workspace(
            workspace_id=workspace_id,
            skip=skip,
            limit=limit,
            search=search,
        )
        return {"teams": teams, "total": total, "skip": skip, "limit": limit}

    async def create_team(
        self,
        team_data: TeamCreate,
        current_user_id: int,
    ) -> Team:
        """Create a team; caller must be workspace OWNER or ADMIN."""
        await self._require_workspace_admin(team_data.workspace_id, current_user_id)

        name_taken = await self.team_repo.name_exists_in_workspace(
            name=team_data.name, workspace_id=team_data.workspace_id
        )
        if name_taken:
            raise DuplicateError(
                message=f"A team named '{team_data.name}' already exists in this workspace",
                details={"name": team_data.name, "workspace_id": team_data.workspace_id},
            )

        team = Team(
            **team_data.model_dump(),
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
        )
        return await self.team_repo.create(team)

    async def update_team(
        self,
        team_id: int,
        team_data: TeamUpdate,
        current_user_id: int,
    ) -> Optional[Team]:
        """Update a team; caller must be workspace OWNER or ADMIN."""
        team = await self._require_team_exists(team_id)
        await self._require_workspace_admin(team.workspace_id, current_user_id)

        update_data = team_data.model_dump(exclude_unset=True)

        # Duplicate name check only when name is being changed
        if "name" in update_data and update_data["name"] != team.name:
            name_taken = await self.team_repo.name_exists_in_workspace(
                name=update_data["name"],
                workspace_id=team.workspace_id,
                exclude_id=team_id,
            )
            if name_taken:
                raise DuplicateError(
                    message=f"A team named '{update_data['name']}' already exists in this workspace",
                    details={"name": update_data["name"]},
                )

        if not update_data:
            return team

        update_data["updated_by_id"] = current_user_id
        return await self.team_repo.update(team_id, **update_data)

    async def delete_team(self, team_id: int, current_user_id: int) -> bool:
        """Soft-delete a team; caller must be workspace OWNER or ADMIN."""
        team = await self._require_team_exists(team_id)
        await self._require_workspace_admin(team.workspace_id, current_user_id)
        return await self.team_repo.soft_delete(team_id, current_user_id)

    # ------------------------------------------------------------------
    # Team member management
    # ------------------------------------------------------------------

    async def get_team_members(
        self,
        team_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        await self._require_team_exists(team_id)
        members, total = await self.member_repo.get_by_team(
            team_id=team_id, skip=skip, limit=limit
        )
        return {"members": members, "total": total, "skip": skip, "limit": limit}

    async def add_member(
        self,
        team_id: int,
        user_id: int,
        role: TeamMemberRole,
        current_user_id: int,
    ) -> TeamMember:
        """Add a user to a team; caller must be workspace OWNER or ADMIN."""
        team = await self._require_team_exists(team_id)
        await self._require_workspace_admin(team.workspace_id, current_user_id)

        existing = await self.member_repo.get_by_user_and_team(
            user_id=user_id, team_id=team_id
        )
        if existing:
            raise DuplicateError(
                message=f"User {user_id} is already a member of team {team_id}",
                details={"user_id": user_id, "team_id": team_id},
            )

        new_member = TeamMember(
            team_id=team_id,
            user_id=user_id,
            role=role.value,
            created_by_id=current_user_id,
            updated_by_id=current_user_id,
        )
        return await self.member_repo.create(new_member)

    async def update_member_role(
        self,
        team_id: int,
        user_id: int,
        new_role: TeamMemberRole,
        current_user_id: int,
    ) -> Optional[TeamMember]:
        """Update a team member's role; caller must be workspace OWNER or ADMIN."""
        team = await self._require_team_exists(team_id)
        await self._require_workspace_admin(team.workspace_id, current_user_id)

        member = await self.member_repo.update_role(
            team_id=team_id, user_id=user_id, role=new_role
        )
        if not member:
            raise ObjectNotFoundError(
                message=f"User {user_id} is not a member of team {team_id}",
                details={"user_id": user_id, "team_id": team_id},
            )
        return member

    async def remove_member(
        self,
        team_id: int,
        user_id: int,
        current_user_id: int,
    ) -> bool:
        """Remove a member from a team; caller must be workspace OWNER or ADMIN."""
        team = await self._require_team_exists(team_id)
        await self._require_workspace_admin(team.workspace_id, current_user_id)

        existing = await self.member_repo.get_by_user_and_team(
            user_id=user_id, team_id=team_id
        )
        if not existing:
            raise ObjectNotFoundError(
                message=f"User {user_id} is not a member of team {team_id}",
                details={"user_id": user_id, "team_id": team_id},
            )

        return await self.member_repo.soft_delete(existing.id, current_user_id)
