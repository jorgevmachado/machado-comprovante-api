from enum import Enum


class StatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    LOCKED = "LOCKED"
    INACTIVE = "INACTIVE"


class ProcessingStatusEnum(str, Enum):
    FAILED = "FAILED"
    RECEIVED = "RECEIVED"
    PROCESSED = "PROCESSED"
    PROCESSING = "PROCESSING"
