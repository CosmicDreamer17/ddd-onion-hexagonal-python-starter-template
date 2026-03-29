class WorkManagementError(Exception):
    """Base exception for the work management bounded context."""


class OwnerRequiredError(WorkManagementError):
    """Raised when attempting to activate a work item without an assigned owner."""

    def __init__(self) -> None:
        super().__init__("Cannot activate a work item without an assigned owner.")


class InvalidStateTransitionError(WorkManagementError):
    """Raised when a state transition violates domain invariants."""

    def __init__(self, current_status: str, target_status: str) -> None:
        super().__init__(
            f"Cannot transition from '{current_status}' to '{target_status}'."
        )


class InvalidOwnerEmailError(WorkManagementError):
    """Raised when an invalid owner email is provided."""

    def __init__(self) -> None:
        super().__init__("A valid owner email must be provided.")


class WorkItemNotFoundError(WorkManagementError):
    """Raised when a work item cannot be found."""

    def __init__(self, item_id: object) -> None:
        super().__init__(f"WorkItem {item_id} not found.")
