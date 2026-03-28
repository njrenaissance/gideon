"""Shared Pydantic models — re-exported for convenience."""

from shared.models.auth import (
    LoginRequest,
    LogoutRequest,
    MfaConfirmRequest,
    MfaRequiredResponse,
    MfaSetupResponse,
    MfaStatusResponse,
    MfaVerifyRequest,
    RefreshRequest,
    TokenResponse,
)
from shared.models.base import MessageResponse
from shared.models.document import (
    DocumentResponse,
    DocumentSummary,
)
from shared.models.enums import (
    Classification,
    DocumentSource,
    MatterStatus,
    Role,
    TaskState,
)
from shared.models.firm import FirmResponse
from shared.models.health import HealthResponse, ReadinessResponse, ServiceChecks
from shared.models.matter import (
    CreateMatterRequest,
    MatterResponse,
    MatterSummary,
    UpdateMatterRequest,
)
from shared.models.matter_access import (
    GrantAccessRequest,
    MatterAccessResponse,
    RevokeAccessRequest,
)
from shared.models.prompt import CreatePromptRequest, PromptResponse, PromptSummary
from shared.models.task import (
    SubmitTaskRequest,
    TaskResponse,
    TaskSubmitResponse,
    TaskSummary,
    UpdateTaskRequest,
)
from shared.models.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
    UserSummary,
)

__all__ = [
    "Classification",
    "CreateMatterRequest",
    "CreatePromptRequest",
    "CreateUserRequest",
    "DocumentResponse",
    "DocumentSource",
    "DocumentSummary",
    "FirmResponse",
    "GrantAccessRequest",
    "HealthResponse",
    "LoginRequest",
    "LogoutRequest",
    "MatterAccessResponse",
    "MatterResponse",
    "MatterStatus",
    "MatterSummary",
    "MessageResponse",
    "MfaConfirmRequest",
    "MfaRequiredResponse",
    "MfaSetupResponse",
    "MfaStatusResponse",
    "MfaVerifyRequest",
    "PromptResponse",
    "PromptSummary",
    "ReadinessResponse",
    "RefreshRequest",
    "RevokeAccessRequest",
    "Role",
    "ServiceChecks",
    "SubmitTaskRequest",
    "TaskResponse",
    "TaskState",
    "TaskSubmitResponse",
    "TaskSummary",
    "TokenResponse",
    "UpdateMatterRequest",
    "UpdateTaskRequest",
    "UpdateUserRequest",
    "UserResponse",
    "UserSummary",
]
