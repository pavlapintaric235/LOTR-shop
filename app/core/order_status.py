from collections.abc import Iterable

ORDER_STATUS_PENDING = "pending"
ORDER_STATUS_CONFIRMED = "confirmed"
ORDER_STATUS_PROCESSING = "processing"
ORDER_STATUS_SHIPPED = "shipped"
ORDER_STATUS_DELIVERED = "delivered"
ORDER_STATUS_CANCELLED = "cancelled"
ORDER_STATUS_PAYMENT_FAILED = "payment_failed"

ORDER_STATUSES = {
    ORDER_STATUS_PENDING,
    ORDER_STATUS_CONFIRMED,
    ORDER_STATUS_PROCESSING,
    ORDER_STATUS_SHIPPED,
    ORDER_STATUS_DELIVERED,
    ORDER_STATUS_CANCELLED,
    ORDER_STATUS_PAYMENT_FAILED,
}

VALID_ORDER_STATUS_TRANSITIONS: dict[str, set[str]] = {
    ORDER_STATUS_PENDING: {
        ORDER_STATUS_CONFIRMED,
        ORDER_STATUS_CANCELLED,
        ORDER_STATUS_PAYMENT_FAILED,
    },
    ORDER_STATUS_CONFIRMED: {
        ORDER_STATUS_PROCESSING,
        ORDER_STATUS_CANCELLED,
    },
    ORDER_STATUS_PROCESSING: {
        ORDER_STATUS_SHIPPED,
        ORDER_STATUS_CANCELLED,
    },
    ORDER_STATUS_SHIPPED: {
        ORDER_STATUS_DELIVERED,
    },
    ORDER_STATUS_DELIVERED: set(),
    ORDER_STATUS_CANCELLED: set(),
    ORDER_STATUS_PAYMENT_FAILED: set(),
}


def is_valid_order_status(status: str) -> bool:
    return status in ORDER_STATUSES


def can_transition_order_status(current_status: str, new_status: str) -> bool:
    if current_status == new_status:
        return True
    allowed_statuses: Iterable[str] = VALID_ORDER_STATUS_TRANSITIONS.get(current_status, set())
    return new_status in allowed_statuses