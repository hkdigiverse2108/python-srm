from datetime import datetime
from beanie import PydanticObjectId
from app.core.base_schema import MongoBaseSchema

class IncentiveSlabBase(MongoBaseSchema):
    min_units: int
    max_units: int
    incentive_per_unit: float
    slab_bonus: float

class IncentiveSlabCreate(IncentiveSlabBase):
    pass

class IncentiveSlabUpdate(MongoBaseSchema):
    min_units: int | None = None
    max_units: int | None = None
    incentive_per_unit: float | None = None
    slab_bonus: float | None = None

class IncentiveSlabRead(IncentiveSlabBase):
    id: PydanticObjectId

# Calculation & Slips
class IncentiveCalculationRequest(MongoBaseSchema):
    user_id: PydanticObjectId
    period: str  # YYYY-MM
    closed_units: int | None = None
    force_recalculate: bool = False


class IncentiveBulkCalculationRequest(MongoBaseSchema):
    period: str  # YYYY-MM


class IncentiveBulkCalculationResponse(MongoBaseSchema):
    period: str
    processed_users: int
    created_slips: int
    skipped_existing: int
    skipped_disabled: int
    failed_users: int
    failures: list[dict]

class MonthlyIncentiveBreakdown(MongoBaseSchema):
    month_label: str
    count: int
    base_incentive: float

class IncentiveSlipRead(MongoBaseSchema):
    id: PydanticObjectId
    user_id: PydanticObjectId
    period: str
    target: int
    achieved: int
    percentage: float
    applied_slab: str | None = None
    amount_per_unit: float | None = None
    slab_bonus_amount: float | None = 0.0
    is_visible_to_employee: bool = False
    employee_remarks: str | None = None
    manager_remarks: str | None = None
    total_incentive: float
    generated_at: datetime
    user_name: str | None = None
    monthly_breakdown: list[MonthlyIncentiveBreakdown] | None = None


class IncentivePreviewResponse(MongoBaseSchema):
    user_id: PydanticObjectId
    user_name: str
    period: str
    target: int
    confirmed_tasks: int
    pending_tasks: int
    refunded_tasks: int
    total_tasks_in_period: int
    slab_range: str | None = None
    incentive_per_task: float
    base_incentive: float
    slab_bonus: float
    total_incentive: float
    percentage: float
    slip_exists: bool
    monthly_breakdown: list[MonthlyIncentiveBreakdown] | None = None
    audit_window_start: str | None = None
    audit_window_end: str | None = None

