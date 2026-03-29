class IntegrationManagementError(Exception):
    """Base exception for the integration management bounded context."""


class InvalidJobTransitionError(IntegrationManagementError):
    """Raised when a job state transition violates domain invariants."""

    def __init__(self, current_status: str, target_status: str) -> None:
        super().__init__(
            f"Cannot transition job from '{current_status}' to '{target_status}'."
        )
