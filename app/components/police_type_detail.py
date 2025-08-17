import reflex as rx
from app.states.police_data_state import PoliceDataState


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
                    rx.text(PoliceDataState.selected_police_type, size="2", color="gray.600", weight="medium"),
                    spacing="2",
                    align="center",
                    margin_bottom="1rem",
                ),
                # Page title
                rx.hstack(
                    rx.heading(
                        rx.text("Police Type: ", PoliceDataState.selected_police_type),
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
                # Total Records
                rx.box(
                    rx.vstack(
                        rx.text("Total Records", size="2", color="gray.600", weight="medium"),
                        rx.text(
                            PoliceDataState.get_police_type_detail_data["total_records"],
                            size="6",
                            weight="bold",
                            color="blue.700",
                        ),
                        spacing="1",
                        align="center",
                    ),
                ),
                # Success Rate
                rx.box(
                    rx.vstack(
                        rx.text("Success Rate", size="2", color="gray.600", weight="medium"),
                        rx.hstack(
                            rx.text(
                                PoliceDataState.get_police_type_detail_data["success_rate"],
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
                                PoliceDataState.get_police_type_detail_data["status"] == "Good",
                                "green",
                                rx.cond(
                                    PoliceDataState.get_police_type_detail_data["status"] == "Warning",
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
                        rx.text("Successful", size="2", color="gray.600", weight="medium"),
                        rx.text(
                            PoliceDataState.get_police_type_detail_data["success_records"],
                            size="6",
                            weight="bold",
                            color="green.700",
                        ),
                        spacing="1",
                        align="center",
                    ),
                ),
                columns="4",
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


def police_type_insights_placeholder() -> rx.Component:
    """Placeholder component for insights that will be populated later."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("trending-up", size=24, color="purple.600"),
                rx.heading("Detailed Insights", size="4", color="gray.800"),
                spacing="3",
                align="center",
            ),
            rx.divider(),
            rx.box(
                rx.vstack(
                    rx.icon("construction", size=48, color="gray.400"),
                    rx.text(
                        "Detailed insights will be added here",
                        size="4",
                        color="gray.600",
                        weight="medium",
                        text_align="center",
                    ),
                    rx.text(
                        "This section will contain charts, trends, and detailed analytics for this police type.",
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
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        min_height="400px",
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
            rx.box(
                rx.vstack(
                    rx.icon("database", size=48, color="gray.400"),
                    rx.text(
                        "Recent records will be displayed here",
                        size="4",
                        color="gray.600",
                        weight="medium",
                        text_align="center",
                    ),
                    rx.text(
                        "This section will show the latest police records for this type with their status and details.",
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
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        min_height="400px",
    )


def police_type_detail_page() -> rx.Component:
    """Main component for the police type detail page."""
    return rx.box(
        police_type_detail_header(),
        rx.container(
            rx.vstack(
                # Overview card
                police_type_overview_card(),
                # Grid layout for insights and recent records
                rx.grid(
                    police_type_insights_placeholder(),
                    police_type_recent_records(),
                    columns=rx.breakpoints(initial="1", lg="2"),
                    spacing="6",
                    width="100%",
                ),
                spacing="6",
                align="start",
                width="100%",
            ),
            max_width="1200px",
            margin_x="auto",
            padding="2rem",
        ),
        width="100%",
        min_height="100vh",
        background="linear-gradient(180deg, rgba(241, 245, 249, 0.8) 0%, rgba(248, 250, 252, 0.95) 20%, rgba(255, 255, 255, 0.98) 100%)",
    )
