import reflex as rx


def metric_card(icon: str, title: str, value, color: str) -> rx.Component:
    """Reusable metric card component."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=20, color=color),
                rx.text(title, size="2", color="gray.600"),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.cond(
                title == "Success Rate",
                rx.hstack(
                    rx.text(
                        value,
                        size="7",
                        weight="bold",
                        color=f"{color}.800",
                    ),
                    rx.text("%", size="4", color=f"{color}.600"),
                    spacing="1",
                    align="baseline",
                ),
                rx.text(
                    value,
                    size="7",
                    weight="bold",
                    color=f"{color}.800",
                ),
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        padding="1.5rem",
        box_shadow="sm",
        border_radius="lg",
        background="white",
    )


def stats_cards_section(
    get_total_records, get_success_rate, get_error_count, get_active_types
) -> rx.Component:
    """Stats cards section component."""
    return rx.grid(
        metric_card("database", "Total Records", get_total_records, "blue"),
        metric_card("check", "Success Rate", get_success_rate, "green"),
        metric_card("triangle-alert", "Error Count", get_error_count, "red"),
        metric_card("layers", "Active Types", get_active_types, "purple"),
        columns="4",
        spacing="4",
        width="100%",
        margin_bottom="2rem",
    )
