from enum import Enum, auto

class FieldMutability(Enum):
    IMMUTABLE = auto()   # Never changes
    MUTABLE = auto()     # Can change arbitrarily
    CONTROLLED = auto()  # Changes only through specific transitions/methods (e.g., approved)

class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    OUTPUTS_GENERATED = "outputs_generated"
    COMPLETED = "completed"
    CHECKS_FAILED = "checks_failed"
    CHECKS_ERROR = "checks_error"
    FAILED = "failed"

class CheckType(str, Enum):
    GENERIC = "generic"
    SPECIFIC = "specific"

class CheckOutcome(str, Enum):
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"

class CheckSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class EventType(str, Enum):

    # -------------------------------------------------------------------------
    # FINANCIAL MODEL
    # -------------------------------------------------------------------------
    MODEL_REGISTERED          = "model_registered"
    MODEL_ACTIVATED           = "model_activated"
    MODEL_DEACTIVATED         = "model_deactivated"

    # -------------------------------------------------------------------------
    # MODEL VERSION
    # -------------------------------------------------------------------------
    MODEL_VERSION_REGISTERED  = "model_version_registered"
    MODEL_VERSION_APPROVED    = "model_version_approved"
    MODEL_VERSION_REJECTED    = "model_version_rejected"
    MODEL_VERSION_DEPRECATED  = "model_version_deprecated"

    # -------------------------------------------------------------------------
    # PARAMETER SET
    # -------------------------------------------------------------------------
    PARAMETERS_REGISTERED     = "parameters_registered"
    PARAMETERS_APPROVED       = "parameters_approved"
    PARAMETERS_REJECTED       = "parameters_rejected"
    PARAMETERS_DEPRECATED     = "parameters_deprecated"

    # -------------------------------------------------------------------------
    # MODEL RUN
    # -------------------------------------------------------------------------
    RUN_STARTED               = "run_started"
    RUN_OUTPUTS_GENERATED     = "run_outputs_generated"
    RUN_FAILED                = "run_failed"

    # -------------------------------------------------------------------------
    # CHECKS
    # -------------------------------------------------------------------------
    CHECKS_STARTED            = "checks_started"
    CHECKS_COMPLETED          = "checks_completed"         
    CHECKS_FAILED             = "checks_failed"            
    CHECKS_NOT_EXECUTED       = "checks_not_executed"  

    # -------------------------------------------------------------------------
    # ACTIONS
    # -------------------------------------------------------------------------    
    ACTION_EXECUTED           = "action_executed"

    # -------------------------------------------------------------------------
    # SYSTEM
    # -------------------------------------------------------------------------
    SYSTEM_ERROR              = "system_error"
    SYSTEM_WARNING            = "system_warning"

class EventRelevance(str, Enum):
    MAJOR = "major"
    MINOR = "minor"