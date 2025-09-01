import reflex as rx
from app.states.police.police_data_state import PoliceDataState


def navigate_back_to_dashboard():
    """Navigate back to the police dashboard."""
    return rx.redirect("/police")


def police_type_detail_header() -> rx.Component:
    """Header component for the police type detail page."""
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
                        href="/police",
                        color="blue.600",
                        _hover={"color": "blue.800"},
                        style={"text_decoration": "none"},
                    ),
                    rx.text("/", size="2", color="gray.400"),
                    rx.text(
                        rx.cond(
                            PoliceDataState.selected_police_type,
                            PoliceDataState.selected_police_type,
                            PoliceDataState.get_current_police_type_from_url,
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
                            "Police Type: ",
                            rx.cond(
                                PoliceDataState.selected_police_type,
                                PoliceDataState.selected_police_type,
                                PoliceDataState.get_current_police_type_from_url,
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
                        color_scheme="blue",
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
        background="linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 197, 253, 0.1) 100%)",
        border_bottom="1px solid var(--gray-200)",
    )


def police_type_overview_card() -> rx.Component:
    """Overview card showing basic stats for the police type."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("bar-chart-3", size=24, color="blue.600"),
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
                                PoliceDataState.get_police_type_detail_data[
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
                            PoliceDataState.get_police_type_detail_data["status"],
                            size="3",
                            variant="surface",
                            color_scheme=rx.cond(
                                PoliceDataState.get_police_type_detail_data["status"]
                                == "Good",
                                "green",
                                rx.cond(
                                    PoliceDataState.get_police_type_detail_data[
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
                            PoliceDataState.get_police_type_detail_data[
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


def create_state_button(state_name: str, count: int) -> rx.Component:
    """Create a clickable button for a specific state."""

    # Map state names to their corresponding handlers
    handlers = {
        "SUCCESS": PoliceDataState.show_success_reasons,
        "ERROR": PoliceDataState.show_error_reasons,
        "COMPLETE": PoliceDataState.show_complete_reasons,
        "CONFIRMED": PoliceDataState.show_confirmed_reasons,
        "PROGRESS": PoliceDataState.show_progress_reasons,
        "IN_PROGRESS": PoliceDataState.show_in_progress_reasons,
        "NEW": PoliceDataState.show_new_reasons,
        "INVALID": PoliceDataState.show_invalid_reasons,
        "EXPIRED": PoliceDataState.show_expired_reasons,
        "CANCELED": PoliceDataState.show_canceled_reasons,
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

    # Get the appropriate handler for this state
    handler = handlers.get(state_name, PoliceDataState.show_success_reasons)
    colors = color_schemes.get(state_name, color_schemes["SUCCESS"])

    return rx.button(
        rx.hstack(
            rx.text(
                state_name,
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


def interactive_pie_chart_card(
    title: str,
    icon: str,
    icon_color: str,
    chart_data,
    cell_colors: list,
    on_click_handler,
) -> rx.Component:
    """Interactive pie chart card component with click handlers."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=24, color=icon_color),
                rx.heading(title, size="4", color="gray.800"),
                justify="start",
                align="center",
                spacing="2",
                margin_bottom="1rem",
            ),
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    *[rx.recharts.cell(fill=color) for color in cell_colors],
                    data=chart_data,
                    data_key="value",
                    name_key="name",
                    cx="50%",
                    cy="50%",
                    outer_radius="90",
                    label=True,
                    # Remove the on_click as it doesn't work properly
                ),
                rx.recharts.legend(),
                rx.recharts.graphing_tooltip(),
                width="100%",
                height=350,
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        padding="2rem",
        box_shadow="lg",
        border_radius="lg",
    )


def reasons_modal() -> rx.Component:
    """Modal component to show reasons for a selected state."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.hstack(
                    rx.icon("info", size=20, color="blue.600"),
                    rx.text(
                        f"Reasons for State: {PoliceDataState.selected_state}",
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
                PoliceDataState.state_reasons,
                # Show reasons table when data is available
                rx.vstack(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("REASON", weight="medium"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                PoliceDataState.get_paginated_reasons,
                                lambda reason_data: rx.table.row(
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
                            f"Showing page {PoliceDataState.reasons_current_page} "
                            f"of {PoliceDataState.get_total_pages} "
                            f"({PoliceDataState.total_reasons_count} total "
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
                                    PoliceDataState.has_previous_page, False, True
                                ),
                                on_click=PoliceDataState.go_to_previous_page,
                            ),
                            rx.button(
                                "Next →",
                                variant="outline",
                                size="2",
                                disabled=rx.cond(
                                    PoliceDataState.has_next_page, False, True
                                ),
                                on_click=PoliceDataState.go_to_next_page,
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
                    on_click=PoliceDataState.close_reasons_modal,
                ),
            ),
            max_width="500px",
            padding="2rem",
        ),
        open=PoliceDataState.show_reasons_modal,
        on_open_change=PoliceDataState.close_reasons_modal,
    )


def police_type_state_distribution_chart() -> rx.Component:
    """State distribution pie chart for the selected police type."""
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
        PoliceDataState.get_police_type_state_distribution,
        # Show interactive pie chart when data is available
        rx.vstack(
            rx.card(
                rx.vstack(
                    # Clean header with subtle styling
                    rx.hstack(
                        rx.icon("pie-chart", size=24, color="blue.600"),
                        rx.heading(
                            "State Distribution",
                            size="4",
                            color="gray.800",
                            font_weight="600",
                        ),
                        justify="start",
                        align="center",
                        spacing="3",
                        margin_bottom="1.5rem",
                    ),
                    # Improved pie chart with better proportions
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
                                    PoliceDataState.get_police_type_state_distribution
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
            # Add clickable state buttons below the chart
            rx.box(
                rx.text(
                    "Click on a state below to see detailed reasons:",
                    size="2",
                    color="gray.600",
                    margin_bottom="0.5rem",
                ),
                rx.flex(
                    rx.foreach(
                        PoliceDataState.get_police_type_state_distribution,
                        lambda state_data: create_state_button(
                            state_data["name"], state_data["value"]
                        ),
                    ),
                    wrap="wrap",
                    gap="2",
                ),
                padding="1rem",
                background="gray.50",
                border_radius="lg",
                border="1px solid var(--gray-200)",
            ),
            spacing="3",
        ),
        # Show placeholder when no data is available
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.icon("pie-chart", size=24, color="blue.600"),
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
                            "No state distribution data found " "for this police type.",
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


def police_type_recent_records() -> rx.Component:
    """Component showing recent records for this police type."""
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
                PoliceDataState.get_police_type_recent_records,
                # Table with actual data from state
                rx.vstack(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("STATE", weight="medium"),
                                rx.table.column_header_cell("REASON", weight="medium"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                PoliceDataState.get_police_type_recent_records,
                                lambda record, i: rx.table.row(
                                    rx.table.cell(
                                        rx.badge(
                                            record["state"],
                                            size="2",
                                            variant="surface",
                                            color_scheme=rx.cond(
                                                (
                                                    (record["state"] == "SUCCESS")
                                                    | (record["state"] == "CONFIRMED")
                                                    | (record["state"] == "COMPLETE")
                                                ),
                                                "green",
                                                rx.cond(
                                                    (
                                                        (record["state"] == "NEW")
                                                        | (
                                                            record["state"]
                                                            == "IN_PROGRESS"
                                                        )
                                                        | (
                                                            record["state"]
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
                                        record.get("reason", "N/A"), text_align="left"
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
                            "No records found for this police type.",
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


def police_type_detail_page() -> rx.Component:
    """Main component for the police type detail page."""
    return rx.box(
        police_type_detail_header(),
        rx.container(
            rx.vstack(
                # Overview card
                police_type_overview_card(),
                # State distribution chart
                police_type_state_distribution_chart(),
                # Recent records card below state distribution
                police_type_recent_records(),
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
            "linear-gradient(180deg, rgba(241, 245, 249, 0.8) 0%, "
            "rgba(248, 250, 252, 0.95) 20%, rgba(255, 255, 255, 0.98) 100%)"
        ),
    )
