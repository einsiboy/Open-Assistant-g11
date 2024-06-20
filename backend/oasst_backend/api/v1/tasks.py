from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security.api_key import APIKey
from loguru import logger
from oasst_backend.api import deps
from oasst_backend.config import settings
from oasst_backend.prompt_repository import PromptRepository, TaskRepository
from oasst_backend.tree_manager import TreeManager
from oasst_backend.user_repository import UserRepository
from oasst_backend.utils.database_utils import CommitMode, async_managed_tx_function
from oasst_shared.exceptions import OasstError, OasstErrorCode
from oasst_shared.schemas import protocol as protocol_schema
from sqlmodel import Session
from starlette.status import HTTP_204_NO_CONTENT

router = APIRouter()


@router.post(
    "/",
    response_model=protocol_schema.AnyTask,
    dependencies=[
        Depends(
            deps.UserRateLimiter(
                times=settings.RATE_LIMIT_TASK_USER_TIMES,
                minutes=settings.RATE_LIMIT_TASK_USER_MINUTES,
            )
        ),
        Depends(
            deps.APIClientRateLimiter(
                times=settings.RATE_LIMIT_TASK_API_TIMES,
                minutes=settings.RATE_LIMIT_TASK_API_MINUTES,
            )
        ),
        Depends(
            deps.UserTaskTypeRateLimiter(
                [
                    protocol_schema.TaskRequestType.assistant_reply,
                ],
                times=settings.RATE_LIMIT_ASSISTANT_USER_TIMES,
                minutes=settings.RATE_LIMIT_ASSISTANT_USER_MINUTES,
            )
        ),
        Depends(
            deps.UserTaskTypeRateLimiter(
                [
                    protocol_schema.TaskRequestType.prompter_reply,
                ],
                times=settings.RATE_LIMIT_PROMPTER_USER_TIMES,
                minutes=settings.RATE_LIMIT_PROMPTER_USER_MINUTES,
            )
        ),
    ],
)  # work with Union once more types are added
def request_task(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    request: protocol_schema.TaskRequest,
) -> Any:
    """
    ORIGINAL DOCSTRING:
    Create new task.

    ChatGPT GENERATED DOCSTRING:
    Handles the creation of a new task based on a user's request, utilizing various
    dependencies for rate limiting and authentication. It uses the provided session,
    API key, and request data to process and potentially store a task using underlying
    repository management.

    :param db: Database session dependency injected by FastAPI.
    :param api_key: API key for authentication, provided by the client.
    :param request: Task request details provided by the client.
    :return: The created task object as defined by the protocol schema.
    """
    api_client = deps.api_auth(api_key, db)

    try:
        pr = PromptRepository(db, api_client, client_user=request.user)
        pr.ensure_user_is_enabled()

        tm = TreeManager(db, pr)
        task, message_tree_id, parent_message_id = tm.next_task(desired_task_type=request.type, lang=request.lang)
        pr.task_repository.store_task(task, message_tree_id, parent_message_id, request.collective)

    except OasstError:
        raise
    except Exception:
        logger.exception("Failed to generate task..")
        raise OasstError("Failed to generate task.", OasstErrorCode.TASK_GENERATION_FAILED)
    return task


@router.post("/availability", response_model=dict[protocol_schema.TaskRequestType, int])
def tasks_availability(
    *,
    user: Optional[protocol_schema.User] = None,
    lang: Optional[str] = "en",
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
):
    """
    ORIGINAL DOCSTRING:
    Query task availability.

    ChatGPT GENERATED DOCSTRING:
    Queries and returns the availability of different task types for a given user and language.
    This function uses authentication and session management to access and calculate task
    availability through a series of repository and manager calls.

    :param user: Optional; the user for whom the task availability is being checked.
    :param lang: Optional; the language context for the task availability, defaults to English.
    :param db: Database session dependency injected by FastAPI.
    :param api_key: API key for authentication, provided by the client.
    :return: Dictionary of task types and their respective availability counts.
    """
    api_client = deps.api_auth(api_key, db)

    try:
        pr = PromptRepository(db, api_client, client_user=user)
        tm = TreeManager(db, pr)
        return tm.determine_task_availability(lang)

    except OasstError:
        raise
    except Exception:
        logger.exception("Task availability query failed.")
        raise OasstError("Task availability query failed.", OasstErrorCode.TASK_AVAILABILITY_QUERY_FAILED)


@router.post("/{task_id}/ack", response_model=None, status_code=HTTP_204_NO_CONTENT)
def tasks_acknowledge(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    task_id: UUID,
    ack_request: protocol_schema.TaskAck,
) -> None:
    """
    ORIGINAL DOCSTRING:
    The frontend acknowledges a task.

    ChatGPT GENERATED DOCSTRING:
    Processes an acknowledgment for a completed task by binding the task ID to a frontend message ID
    within the database. Utilizes the provided session, API key, and task data for the operation,
    while logging the acknowledgment for system tracing.

    :param db: Database session dependency injected by FastAPI.
    :param api_key: API key for authentication, provided by the client.
    :param frontend_user: Frontend user ID that correlates to the user making the acknowledgment.
    :param task_id: Unique identifier for the task being acknowledged.
    :param ack_request: Contains details about the acknowledgment from the frontend.
    """
    api_client = deps.api_auth(api_key, db)

    try:
        pr = PromptRepository(db, api_client, frontend_user=frontend_user)

        # here we store the message id in the database for the task
        logger.info(f"Frontend ACK task_id={task_id}")
        logger.debug(f"{ack_request=}.")
        pr.task_repository.bind_frontend_message_id(task_id=task_id, frontend_message_id=ack_request.message_id)

    except OasstError:
        raise
    except Exception:
        logger.exception("Failed to acknowledge task.")
        raise OasstError("Failed to acknowledge task.", OasstErrorCode.TASK_ACK_FAILED)


@router.post("/{task_id}/nack", response_model=None, status_code=HTTP_204_NO_CONTENT)
def tasks_acknowledge_failure(
    *,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
    frontend_user: deps.FrontendUserId = Depends(deps.get_frontend_user_id),
    task_id: UUID,
    nack_request: protocol_schema.TaskNAck,
) -> None:
    """
    ORIGINAL DOCSTRING:
    The frontend reports failure to implement a task.

    ChatGPT GENERATED DOCSTRING:
    Handles the report of a failed task implementation, marking the task as skipped with a reason.
    This involves logging the failure and updating the task status within the database based on
    the provided session, API key, and task data.

    :param db: Database session dependency injected by FastAPI.
    :param api_key: API key for authentication, provided by the client.
    :param frontend_user: Frontend user ID that correlates to the user reporting the failure.
    :param task_id: Unique identifier for the task that failed.
    :param nack_request: Contains details about the failure, including the reason for the failure.
    """
    try:
        logger.info(f"Frontend reports failure to implement task {task_id=}, {nack_request=}.")
        api_client = deps.api_auth(api_key, db)
        pr = PromptRepository(db, api_client, frontend_user=frontend_user)
        pr.skip_task(task_id=task_id, reason=nack_request.reason)
    except (KeyError, RuntimeError):
        logger.exception("Failed to not acknowledge task.")
        raise OasstError("Failed to not acknowledge task.", OasstErrorCode.TASK_NACK_FAILED)


@router.post("/interaction", response_model=protocol_schema.TaskDone)
async def tasks_interaction(
    *,
    api_key: APIKey = Depends(deps.get_api_key),
    interaction: protocol_schema.AnyInteraction,
) -> Any:
    """
    ORIGINAL DOCSTRING:
    The frontend reports an interaction.

    ChatGPT GENERATED DOCSTRING:
    Processes a user interaction reported from the frontend, potentially concluding with
    a task completion. This asynchronous function manages the transaction of handling the
    interaction, updating user activity, and returning the resultant task state.

    :param api_key: API key for authentication, provided by the client.
    :param interaction: Details of the user interaction that needs to be processed.
    :return: The final state of the task after processing the interaction.
    """

    @async_managed_tx_function(CommitMode.COMMIT)
    async def interaction_tx(session: deps.Session):
        api_client = deps.api_auth(api_key, session)
        pr = PromptRepository(session, api_client, client_user=interaction.user)
        tm = TreeManager(session, pr)
        ur = UserRepository(session, api_client)
        task = await tm.handle_interaction(interaction)
        if type(task) is protocol_schema.TaskDone:
            ur.update_user_last_activity(user=pr.user, update_streak=True)
        return task

    try:
        return await interaction_tx()
    except OasstError:
        raise
    except Exception:
        logger.exception("Interaction request failed.")
        raise OasstError("Interaction request failed.", OasstErrorCode.TASK_INTERACTION_REQUEST_FAILED)


@router.post("/close", response_model=protocol_schema.TaskDone)
def close_collective_task(
    close_task_request: protocol_schema.TaskClose,
    db: Session = Depends(deps.get_db),
    api_key: APIKey = Depends(deps.get_api_key),
):
    """
    ORIGINAL DOCSTRING:
    Close a task as complete.

    ChatGPT GENERATED DOCSTRING:
    Marks a collective task as completed based on the request, using session management
    and authentication. It updates the task's status in the database to reflect its closure.

    :param close_task_request: Contains details of the task to be closed.
    :param db: Database session dependency injected by FastAPI.
    :param api_key: API key for authentication, provided by the client.
    :return: Confirmation of the task closure represented by a `TaskDone` schema.
    """
    api_client = deps.api_auth(api_key, db)
    tr = TaskRepository(db, api_client)
    tr.close_task(close_task_request.message_id)
    return protocol_schema.TaskDone()
