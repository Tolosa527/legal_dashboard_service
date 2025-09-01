import reflex as rx
from app.states.statistics.statistics_data_state import StatisticsDataState


def navigate_back_to_statistics_dashboard():
    """Navigate back to the statistics dashboard."""
    return rx.redirect("/statistics")


def statistics_type_detail_header() -> rx.Component:
    """Header component for the statistics type detail page."""
    return rx.box(
        rx.container(
            rx.vstack(
                # Breadcrumb navigation
                rx.hstack(
                    rx.link(
                        rx.hstack(
                            rx.icon("arrow-left", size=16),
                            rx.text("Dashboard", size="2", weight="medium"),
                            spacing="2",
                            align="center",
                        ),
                        href="/statistics",
                        color="blue.600",
                        _hover={"color": "blue.800"},
                        style={"text_decoration": "none"},
                    ),
                    rx.text("/", size="2", color="gray.400"),
                    rx.text(
                        rx.cond(
                            StatisticsDataState.selected_statistics_type,
                            StatisticsDataState.selected_statistics_type,
                            StatisticsDataState.get_current_statistics_type_from_url,
                        ),
                        size="2",
                        color="gray.600",
                        weight="medium",
                    ),
                    spacing="2",
                    align="center",
                    margin_bottom="1rem",
                ),
                # Page title
                rx.hstack(
                    rx.heading(
                        rx.text(
                            "Statistics Type: ",
                            rx.cond(
                                StatisticsDataState.selected_statistics_type,
                                StatisticsDataState.selected_statistics_type,
                                StatisticsDataState.get_current_statistics_type_from_url,
                            ),
                        ),
                        size="7",
                        color="gray.800",
                        weight="bold",
                    ),
                    rx.badge(
                        "Detailed View",
                        size="2",
                        variant="surface",
                        color_scheme="purple",
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            max_width="1200px",
            margin_x="auto",
            padding="2rem",
        ),
        width="100%",
        background="linear-gradient(135deg, rgba(147, 51, 234, 0.1) 0%, rgba(196, 181, 253, 0.1) 100%)",
        border_bottom="1px solid var(--gray-200)",
    )


def statistics_type_overview_card() -> rx.Component:
    """Overview card showing basic stats for the statistics type."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("bar-chart-3", size=24, color="purple.600"),
                rx.heading("Overview", size="4", color="gray.800"),
                spacing="3",
                align="center",
            ),
            rx.divider(),
            rx.grid(
                # Success Rate
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Success Rate", size="2", color="gray.600", weight="medium"
                        ),
                        rx.hstack(
                            rx.text(
                                StatisticsDataState.get_statistics_type_detail_data[
                                    "success_rate"
                                ],
                                size="6",
                                weight="bold",
                                color="green.700",
                            ),
                            rx.text("%", size="4", color="gray.600"),
                            spacing="1",
                            align="baseline",
                        ),
                        spacing="1",
                        align="center",
                    ),
                ),
                # Status
                rx.box(
                    rx.vstack(
                        rx.text("Status", size="2", color="gray.600", weight="medium"),
                        rx.badge(
                            StatisticsDataState.get_statistics_type_detail_data[
                                "status"
                            ],
                            size="3",
                            variant="surface",
                            color_scheme=rx.cond(
                                StatisticsDataState.get_statistics_type_detail_data[
                                    "status"
                                ]
                                == "Good",
                                "green",
                                rx.cond(
                                    StatisticsDataState.get_statistics_type_detail_data[
                                        "status"
                                    ]
                                    == "Warning",
                                    "orange",
                                    "red",
                                ),
                            ),
                        ),
                        spacing="1",
                        align="center",
                    ),
                ),
                # Success Records
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Successful", size="2", color="gray.600", weight="medium"
                        ),
                        rx.text(
                            StatisticsDataState.get_statistics_type_detail_data[
                                "success_records"
                            ],
                            size="6",
                            weight="bold",
                            color="green.700",
                        ),
                        spacing="1",
                        align="center",
                    ),
                ),
                columns="3",
                spacing="6",
                width="100%",
            ),
            spacing="4",
            align="start",
            width="100%",
        ),
        padding="2rem",
        background="white",
        border="1px solid var(--gray-200)",
        border_radius="xl",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    )


def create_checkin_checkout_summary_card() -> rx.Component:
    """Summary card showing check-in vs check-out statistics."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("calendar-check", size=24, color="indigo.600"),
                rx.heading("Check-in vs Check-out Summary", size="4", color="gray.800"),
                spacing="3",
                align="center",
            ),
            rx.divider(),
            rx.grid(
                # Check-in Success Rate
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Check-in Success",
                            size="2",
                            color="gray.600",
                            weight="medium",
                        ),
                        rx.hstack(
                            rx.text(
                                StatisticsDataState.get_statistics_type_detail_data.get(
                                    "checkin_success_rate", "0.0"
                                ),
                                size="6",
                                weight="bold",
                                color="green.700",
                            ),
                            rx.text("%", size="4", color="gray.600"),
                            spacing="1",
                            align="baseline",
                        ),
                        spacing="1",
                        align="center",
                    ),
                ),
                # Check-out Success Rate
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Check-out Success",
                            size="2",
                            color="gray.600",
                            weight="medium",
                        ),
                        rx.hstack(
                            rx.text(
                                StatisticsDataState.get_statistics_type_detail_data.get(
                                    "checkout_success_rate", "0.0"
                                ),
                                size="6",
                                weight="bold",
                                color="blue.700",
                            ),
                            rx.text("%", size="4", color="gray.600"),
                            spacing="1",
                            align="baseline",
                        ),
                        spacing="1",
                        align="center",
                    ),
                ),
                # Total Records
                rx.box(
                    rx.vstack(
                        rx.text(
                            "Total Records", size="2", color="gray.600", weight="medium"
                        ),
                        rx.text(
                            StatisticsDataState.get_statistics_type_detail_data[
                                "total_records"
                            ],
                            size="6",
                            weight="bold",
                            color="purple.700",
                        ),
                        spacing="1",
                        align="center",
                    ),
                ),
                columns="3",
                spacing="6",
                width="100%",
            ),
            spacing="4",
            align="start",
            width="100%",
        ),
        padding="2rem",
        background="white",
        border="1px solid var(--gray-200)",
        border_radius="xl",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
    )


def create_state_button(
    state_name: str, count: int, operation_type: str = "combined"
) -> rx.Component:
    """Create a clickable button for a specific state."""

    # Map state names to their corresponding handlers based on operation type
    checkin_handlers = {
        "SUCCESS": StatisticsDataState.show_checkin_success_reasons,
        "ERROR": StatisticsDataState.show_checkin_error_reasons,
        "COMPLETE": StatisticsDataState.show_checkin_complete_reasons,
        "CONFIRMED": StatisticsDataState.show_checkin_confirmed_reasons,
        "PROGRESS": StatisticsDataState.show_checkin_progress_reasons,
        "IN_PROGRESS": StatisticsDataState.show_checkin_in_progress_reasons,
        "NEW": StatisticsDataState.show_checkin_new_reasons,
        "INVALID": StatisticsDataState.show_checkin_invalid_reasons,
        "EXPIRED": StatisticsDataState.show_checkin_expired_reasons,
        "CANCELED": StatisticsDataState.show_checkin_canceled_reasons,
    }

    checkout_handlers = {
        "SUCCESS": StatisticsDataState.show_checkout_success_reasons,
        "ERROR": StatisticsDataState.show_checkout_error_reasons,
        "COMPLETE": StatisticsDataState.show_checkout_complete_reasons,
        "CONFIRMED": StatisticsDataState.show_checkout_confirmed_reasons,
        "PROGRESS": StatisticsDataState.show_checkout_progress_reasons,
        "IN_PROGRESS": StatisticsDataState.show_checkout_in_progress_reasons,
        "NEW": StatisticsDataState.show_checkout_new_reasons,
        "INVALID": StatisticsDataState.show_checkout_invalid_reasons,
        "EXPIRED": StatisticsDataState.show_checkout_expired_reasons,
        "CANCELED": StatisticsDataState.show_checkout_canceled_reasons,
    }

    combined_handlers = {
        "SUCCESS": StatisticsDataState.show_combined_success_reasons,
        "ERROR": StatisticsDataState.show_combined_error_reasons,
        "COMPLETE": StatisticsDataState.show_combined_complete_reasons,
        "CONFIRMED": StatisticsDataState.show_combined_confirmed_reasons,
        "PROGRESS": StatisticsDataState.show_combined_progress_reasons,
        "IN_PROGRESS": StatisticsDataState.show_combined_in_progress_reasons,
        "NEW": StatisticsDataState.show_combined_new_reasons,
        "INVALID": StatisticsDataState.show_combined_invalid_reasons,
        "EXPIRED": StatisticsDataState.show_combined_expired_reasons,
        "CANCELED": StatisticsDataState.show_combined_canceled_reasons,
    }

    # Define color schemes for different states
    color_schemes = {
        "SUCCESS": {
            "color": "green",
            "bg": "green.50",
            "border": "green.200",
            "hover_bg": "green.100",
        },
        "COMPLETE": {
            "color": "blue",
            "bg": "blue.50",
            "border": "blue.200",
            "hover_bg": "blue.100",
        },
        "CONFIRMED": {
            "color": "teal",
            "bg": "teal.50",
            "border": "teal.200",
            "hover_bg": "teal.100",
        },
        "PROGRESS": {
            "color": "orange",
            "bg": "orange.50",
            "border": "orange.200",
            "hover_bg": "orange.100",
        },
        "IN_PROGRESS": {
            "color": "orange",
            "bg": "orange.50",
            "border": "orange.200",
            "hover_bg": "orange.100",
        },
        "NEW": {
            "color": "purple",
            "bg": "purple.50",
            "border": "purple.200",
            "hover_bg": "purple.100",
        },
        "ERROR": {
            "color": "red",
            "bg": "red.50",
            "border": "red.200",
            "hover_bg": "red.100",
        },
        "INVALID": {
            "color": "red",
            "bg": "red.50",
            "border": "red.200",
            "hover_bg": "red.100",
        },
        "EXPIRED": {
            "color": "red",
            "bg": "red.50",
            "border": "red.200",
            "hover_bg": "red.100",
        },
        "CANCELED": {
            "color": "gray",
            "bg": "gray.50",
            "border": "gray.200",
            "hover_bg": "gray.100",
        },
    }

    # Get the appropriate handler for this state and operation type
    if operation_type == "checkin":
        handler = checkin_handlers.get(
            state_name, StatisticsDataState.show_checkin_success_reasons
        )
    elif operation_type == "checkout":
        handler = checkout_handlers.get(
            state_name, StatisticsDataState.show_checkout_success_reasons
        )
    else:
        handler = combined_handlers.get(
            state_name, StatisticsDataState.show_combined_success_reasons
        )

    colors = color_schemes.get(state_name, color_schemes["SUCCESS"])

    # Add operation type prefix to display name
    display_name = state_name
    if operation_type == "checkin":
        display_name = f"CI: {state_name}"
    elif operation_type == "checkout":
        display_name = f"CO: {state_name}"

    return rx.button(
        rx.hstack(
            rx.text(
                display_name,
                weight="bold",
                size="4",
                color=f"{colors['color']}.700",
            ),
        ),
        variant="outline",
        size="3",
        on_click=handler,
        background=colors["bg"],
        border_color=colors["border"],
        border_radius="lg",
        padding="0.75rem 3rem",
        margin="2px",
        cursor="pointer",
        transition="all 0.2s ease-in-out",
        _hover={
            "background": colors["hover_bg"],
            "transform": "translateY(-1px)",
            "box_shadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
        },
        _active={
            "transform": "translateY(0px)",
        },
    )


def reasons_modal() -> rx.Component:
    """Modal component to show reasons for a selected state."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("info", size=20, color="purple.600"),
                    rx.text(
                        f"Reasons for State: {StatisticsDataState.selected_state}",
                        weight="bold",
                    ),
                    align="center",
                    spacing="2",
                )
            ),
            rx.dialog.description(
                "Detailed breakdown of reasons for this state",
                size="2",
                color="gray.600",
                margin_bottom="1rem",
            ),
            rx.cond(
                StatisticsDataState.state_reasons,
                # Show reasons table when data is available
                rx.vstack(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell(
                                    "OPERATION", weight="medium"
                                ),
                                rx.table.column_header_cell("REASON", weight="medium"),
                                rx.table.column_header_cell("COUNT", weight="medium"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                StatisticsDataState.get_paginated_reasons,
                                lambda reason_data: rx.table.row(
                                    rx.table.cell(
                                        rx.badge(
                                            reason_data["operation"],
                                            size="1",
                                            variant="surface",
                                            color_scheme=rx.cond(
                                                reason_data["operation"] == "CHECK_IN",
                                                "green",
                                                "blue",
                                            ),
                                        ),
                                        text_align="center",
                                    ),
                                    rx.table.cell(
                                        reason_data["reason"],
                                        text_align="left",
                                    ),
                                    rx.table.cell(
                                        reason_data["count"],
                                        text_align="right",
                                        weight="medium",
                                    ),
                                ),
                            ),
                        ),
                        width="100%",
                        border="1px solid var(--gray-200)",
                        border_radius="lg",
                        overflow="hidden",
                    ),
                    # Pagination info and controls
                    rx.hstack(
                        rx.text(
                            f"Showing page {StatisticsDataState.reasons_current_page} "
                            f"of {StatisticsDataState.get_total_pages} "
                            f"({StatisticsDataState.total_reasons_count} total "
                            f"reasons)",
                            size="2",
                            color="gray.600",
                        ),
                        rx.spacer(),
                        rx.hstack(
                            rx.button(
                                "← Previous",
                                variant="outline",
                                size="2",
                                disabled=rx.cond(
                                    StatisticsDataState.has_previous_page, False, True
                                ),
                                on_click=StatisticsDataState.go_to_previous_page,
                            ),
                            rx.button(
                                "Next →",
                                variant="outline",
                                size="2",
                                disabled=rx.cond(
                                    StatisticsDataState.has_next_page, False, True
                                ),
                                on_click=StatisticsDataState.go_to_next_page,
                            ),
                            spacing="2",
                        ),
                        justify="between",
                        width="100%",
                        margin_top="1rem",
                    ),
                    spacing="3",
                ),
                # Show "no reasons" message when no data
                rx.vstack(
                    rx.icon(
                        "search-x",
                        size=48,
                        color="gray.400",
                    ),
                    rx.heading(
                        "No reasons found",
                        size="5",
                        color="gray.600",
                        text_align="center",
                    ),
                    rx.text(
                        "No reason data available for this state.",
                        size="3",
                        color="gray.500",
                        text_align="center",
                    ),
                    spacing="2",
                    align="center",
                    padding="2rem",
                    background="gray.50",
                    border_radius="lg",
                    border="2px dashed var(--gray-300)",
                    width="100%",
                ),
            ),
            rx.dialog.close(
                rx.button(
                    "Close",
                    variant="outline",
                    margin_top="1rem",
                    on_click=StatisticsDataState.close_reasons_modal,
                ),
            ),
            max_width="600px",
            padding="2rem",
        ),
        open=StatisticsDataState.show_reasons_modal,
        on_open_change=StatisticsDataState.close_reasons_modal,
    )


def statistics_type_state_distribution_charts() -> rx.Component:
    """Combined and separate state distribution charts for check-in/check-out."""
    # Define colors for different states
    state_colors = [
        "#10B981",  # Green for SUCCESS
        "#EF4444",  # Red for ERROR
        "#3B82F6",  # Blue for NEW/IN_PROGRESS
        "#F59E0B",  # Amber for COMPLETE
        "#8B5CF6",  # Purple for CANCELED
        "#6B7280",  # Gray for other states
        "#EC4899",  # Pink for additional states
        "#06B6D4",  # Cyan
        "#84CC16",  # Lime
        "#F97316",  # Orange
    ]

    return rx.cond(
        StatisticsDataState.get_statistics_type_state_distribution,
        # Show distribution charts when data is available
        rx.vstack(
            # Combined State Distribution
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon("pie-chart", size=24, color="purple.600"),
                        rx.heading(
                            "Combined State Distribution",
                            size="4",
                            color="gray.800",
                            font_weight="600",
                        ),
                        justify="start",
                        align="center",
                        spacing="3",
                        margin_bottom="1.5rem",
                    ),
                    rx.box(
                        rx.recharts.pie_chart(
                            rx.recharts.pie(
                                *[
                                    rx.recharts.cell(
                                        fill=color,
                                        stroke="white",
                                        stroke_width=1,
                                    )
                                    for color in state_colors
                                ],
                                data=(
                                    StatisticsDataState.get_statistics_type_state_distribution
                                ),
                                data_key="value",
                                name_key="name",
                                cx="50%",
                                cy="50%",
                                outer_radius="110",
                                label=True,
                                label_line=True,
                            ),
                            rx.recharts.legend(
                                vertical_align="bottom",
                                height=50,
                            ),
                            rx.recharts.graphing_tooltip(),
                            width="100%",
                            height=400,
                        ),
                        width="100%",
                        min_width="600px",
                        overflow="auto",
                    ),
                    spacing="4",
                    align="center",
                    width="100%",
                ),
                padding="2rem",
                background="white",
                border="1px solid var(--gray-200)",
                border_radius="lg",
                box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                width="100%",
            ),
            # Check-in vs Check-out side by side
            rx.grid(
                # Check-in Distribution
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("log-in", size=20, color="green.600"),
                            rx.heading(
                                "Check-in Distribution",
                                size="3",
                                color="gray.800",
                                font_weight="600",
                            ),
                            justify="start",
                            align="center",
                            spacing="2",
                            margin_bottom="1rem",
                        ),
                        rx.box(
                            rx.recharts.pie_chart(
                                rx.recharts.pie(
                                    *[
                                        rx.recharts.cell(
                                            fill=color,
                                            stroke="white",
                                            stroke_width=1,
                                        )
                                        for color in state_colors
                                    ],
                                    data=(
                                        StatisticsDataState.get_statistics_type_checkin_distribution
                                    ),
                                    data_key="value",
                                    name_key="name",
                                    cx="50%",
                                    cy="50%",
                                    outer_radius="90",
                                    label=True,
                                    label_line=True,
                                ),
                                rx.recharts.legend(
                                    vertical_align="bottom",
                                    height=40,
                                ),
                                rx.recharts.graphing_tooltip(),
                                width="100%",
                                height=300,
                            ),
                            width="100%",
                            overflow="auto",
                        ),
                        spacing="3",
                        align="center",
                        width="100%",
                    ),
                    padding="1.5rem",
                    background="white",
                    border="1px solid var(--gray-200)",
                    border_radius="lg",
                    box_shadow="0 2px 4px rgba(0, 0, 0, 0.1)",
                    width="100%",
                ),
                # Check-out Distribution
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("log-out", size=20, color="blue.600"),
                            rx.heading(
                                "Check-out Distribution",
                                size="3",
                                color="gray.800",
                                font_weight="600",
                            ),
                            justify="start",
                            align="center",
                            spacing="2",
                            margin_bottom="1rem",
                        ),
                        rx.box(
                            rx.recharts.pie_chart(
                                rx.recharts.pie(
                                    *[
                                        rx.recharts.cell(
                                            fill=color,
                                            stroke="white",
                                            stroke_width=1,
                                        )
                                        for color in state_colors
                                    ],
                                    data=(
                                        StatisticsDataState.get_statistics_type_checkout_distribution
                                    ),
                                    data_key="value",
                                    name_key="name",
                                    cx="50%",
                                    cy="50%",
                                    outer_radius="90",
                                    label=True,
                                    label_line=True,
                                ),
                                rx.recharts.legend(
                                    vertical_align="bottom",
                                    height=40,
                                ),
                                rx.recharts.graphing_tooltip(),
                                width="100%",
                                height=300,
                            ),
                            width="100%",
                            overflow="auto",
                        ),
                        spacing="3",
                        align="center",
                        width="100%",
                    ),
                    padding="1.5rem",
                    background="white",
                    border="1px solid var(--gray-200)",
                    border_radius="lg",
                    box_shadow="0 2px 4px rgba(0, 0, 0, 0.1)",
                    width="100%",
                ),
                columns="2",
                spacing="4",
                width="100%",
            ),
            # Clickable state buttons section
            rx.box(
                rx.vstack(
                    rx.text(
                        "Click on a state below to see detailed reasons:",
                        size="2",
                        color="gray.600",
                        margin_bottom="0.5rem",
                    ),
                    # Combined states buttons
                    rx.box(
                        rx.text(
                            "Combined States:",
                            size="1",
                            color="gray.500",
                            weight="medium",
                            margin_bottom="0.25rem",
                        ),
                        rx.flex(
                            rx.foreach(
                                StatisticsDataState.get_statistics_type_state_distribution,
                                lambda state_data: create_state_button(
                                    state_data["name"], state_data["value"], "combined"
                                ),
                            ),
                            wrap="wrap",
                            gap="2",
                        ),
                        margin_bottom="1rem",
                    ),
                    # Check-in states buttons
                    rx.box(
                        rx.text(
                            "Check-in States:",
                            size="1",
                            color="gray.500",
                            weight="medium",
                            margin_bottom="0.25rem",
                        ),
                        rx.flex(
                            rx.foreach(
                                StatisticsDataState.get_statistics_type_checkin_distribution,
                                lambda state_data: create_state_button(
                                    state_data["name"], state_data["value"], "checkin"
                                ),
                            ),
                            wrap="wrap",
                            gap="2",
                        ),
                        margin_bottom="1rem",
                    ),
                    # Check-out states buttons
                    rx.box(
                        rx.text(
                            "Check-out States:",
                            size="1",
                            color="gray.500",
                            weight="medium",
                            margin_bottom="0.25rem",
                        ),
                        rx.flex(
                            rx.foreach(
                                StatisticsDataState.get_statistics_type_checkout_distribution,
                                lambda state_data: create_state_button(
                                    state_data["name"], state_data["value"], "checkout"
                                ),
                            ),
                            wrap="wrap",
                            gap="2",
                        ),
                    ),
                    spacing="2",
                ),
                padding="1rem",
                background="gray.50",
                border_radius="lg",
                border="1px solid var(--gray-200)",
            ),
            spacing="4",
        ),
        # Show placeholder when no data is available
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("pie-chart", size=24, color="purple.600"),
                    rx.heading("State Distribution", size="4", color="gray.800"),
                    spacing="3",
                    align="center",
                ),
                rx.divider(),
                rx.box(
                    rx.vstack(
                        rx.icon("database", size=48, color="gray.400"),
                        rx.text(
                            "No state data available",
                            size="4",
                            color="gray.600",
                            weight="medium",
                            text_align="center",
                        ),
                        rx.text(
                            "No state distribution data found "
                            "for this statistics type.",
                            size="2",
                            color="gray.500",
                            text_align="center",
                            max_width="400px",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    padding="3rem",
                    background="gray.50",
                    border_radius="lg",
                    border="2px dashed var(--gray-300)",
                    width="100%",
                ),
                spacing="4",
                align="start",
                width="100%",
            ),
            padding="2rem",
            background="white",
            border="1px solid var(--gray-200)",
            border_radius="xl",
            box_shadow=(
                "0 4px 6px -1px rgba(0, 0, 0, 0.1), "
                "0 2px 4px -1px rgba(0, 0, 0, 0.06)"
            ),
            min_height="400px",
        ),
    )


def statistics_type_recent_records() -> rx.Component:
    """Component showing recent records for this statistics type."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("clock", size=24, color="orange.600"),
                rx.heading("Recent Records", size="4", color="gray.800"),
                spacing="3",
                align="center",
            ),
            rx.divider(),
            rx.cond(
                StatisticsDataState.recent_records_loading,
                # Show loading state
                rx.box(
                    rx.vstack(
                        rx.spinner(size="3", color="purple.600"),
                        rx.text(
                            "Loading recent records...",
                            size="3",
                            color="gray.600",
                            text_align="center",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    padding="3rem",
                    width="100%",
                ),
                rx.cond(
                    StatisticsDataState.get_statistics_type_recent_records,
                    # Table with actual data from state
                    rx.vstack(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell(
                                        "CHECK-IN STATE", weight="medium"
                                    ),
                                    rx.table.column_header_cell(
                                        "CHECK-OUT STATE", weight="medium"
                                    ),
                                    rx.table.column_header_cell(
                                        "REASON", weight="medium"
                                    ),
                                ),
                            ),
                            rx.table.body(
                                rx.foreach(
                                    StatisticsDataState.get_statistics_type_recent_records,
                                    lambda record, i: rx.table.row(
                                        rx.table.cell(
                                            rx.badge(
                                                record["checkin_state"],
                                                size="2",
                                                variant="surface",
                                                color_scheme=rx.cond(
                                                    (
                                                        (
                                                            record["checkin_state"]
                                                            == "SUCCESS"
                                                        )
                                                        | (
                                                            record["checkin_state"]
                                                            == "CONFIRMED"
                                                        )
                                                        | (
                                                            record["checkin_state"]
                                                            == "COMPLETE"
                                                        )
                                                    ),
                                                    "green",
                                                    rx.cond(
                                                        (
                                                            (
                                                                record["checkin_state"]
                                                                == "NEW"
                                                            )
                                                            | (
                                                                record["checkin_state"]
                                                                == "IN_PROGRESS"
                                                            )
                                                            | (
                                                                record["checkin_state"]
                                                                == "PROGRESS"
                                                            )
                                                        ),
                                                        "blue",
                                                        "red",
                                                    ),
                                                ),
                                            )
                                        ),
                                        rx.table.cell(
                                            rx.badge(
                                                record["checkout_state"],
                                                size="2",
                                                variant="surface",
                                                color_scheme=rx.cond(
                                                    (
                                                        (
                                                            record["checkout_state"]
                                                            == "SUCCESS"
                                                        )
                                                        | (
                                                            record["checkout_state"]
                                                            == "CONFIRMED"
                                                        )
                                                        | (
                                                            record["checkout_state"]
                                                            == "COMPLETE"
                                                        )
                                                    ),
                                                    "green",
                                                    rx.cond(
                                                        (
                                                            (
                                                                record["checkout_state"]
                                                                == "NEW"
                                                            )
                                                            | (
                                                                record["checkout_state"]
                                                                == "IN_PROGRESS"
                                                            )
                                                            | (
                                                                record["checkout_state"]
                                                                == "PROGRESS"
                                                            )
                                                        ),
                                                        "blue",
                                                        "red",
                                                    ),
                                                ),
                                            )
                                        ),
                                        rx.table.cell(
                                            record.get("reason", "N/A"),
                                            text_align="left",
                                        ),
                                    ),
                                ),
                            ),
                            width="100%",
                            border="1px solid var(--gray-200)",
                            border_radius="lg",
                            overflow="hidden",
                        ),
                        rx.text(
                            "Showing the 10 most recent records",
                            size="2",
                            color="gray.500",
                            align="right",
                            padding_top="2",
                        ),
                        width="100%",
                    ),
                    # Placeholder when no data is available
                    rx.box(
                        rx.vstack(
                            rx.icon("database", size=48, color="gray.400"),
                            rx.text(
                                "No recent records available",
                                size="4",
                                color="gray.600",
                                weight="medium",
                                text_align="center",
                            ),
                            rx.text(
                                "No records found for this statistics type.",
                                size="2",
                                color="gray.500",
                                text_align="center",
                                max_width="400px",
                            ),
                            spacing="3",
                            align="center",
                        ),
                        padding="3rem",
                        background="gray.50",
                        border_radius="lg",
                        border="2px dashed var(--gray-300)",
                        width="100%",
                    ),
                ),
            ),
            spacing="4",
            align="start",
            width="100%",
        ),
        padding="2rem",
        background="white",
        border="1px solid var(--gray-200)",
        border_radius="xl",
        box_shadow=(
            "0 4px 6px -1px rgba(0, 0, 0, 0.1), " "0 2px 4px -1px rgba(0, 0, 0, 0.06)"
        ),
        min_height="400px",
        width="100%",
    )


def statistics_type_detail_page() -> rx.Component:
    """Main component for the statistics type detail page."""
    return rx.box(
        statistics_type_detail_header(),
        rx.container(
            rx.vstack(
                # Overview cards
                rx.grid(
                    statistics_type_overview_card(),
                    create_checkin_checkout_summary_card(),
                    columns="2",
                    spacing="6",
                    width="100%",
                ),
                # State distribution charts
                statistics_type_state_distribution_charts(),
                # Recent records card
                statistics_type_recent_records(),
                spacing="6",
                align="start",
                width="100%",
            ),
            max_width="1200px",
            margin_x="auto",
            padding="2rem",
        ),
        # Add the modal component
        reasons_modal(),
        width="100%",
        min_height="100vh",
        background=(
            "linear-gradient(180deg, rgba(245, 243, 255, 0.8) 0%, "
            "rgba(250, 245, 255, 0.95) 20%, rgba(255, 255, 255, 0.98) 100%)"
        ),
        # Load statistics type from URL and fetch recent records when component mounts
        on_mount=[
            StatisticsDataState.load_statistics_type_from_url,
            StatisticsDataState.fetch_recent_records_for_statistics_type,
        ],
    )
