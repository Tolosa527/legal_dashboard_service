import reflex as rx


def status_card(type_data, route_prefix="police-type") -> rx.Component:
    """Individual status card component for police/statistics type status."""
    return rx.link(
        rx.card(
            rx.vstack(
                # Header with colored indicator bar
                rx.hstack(
                    rx.box(
                        width="4px",
                        height="32px",
                        background=rx.cond(
                            type_data["status"] == "Good",
                            "green.500",
                            rx.cond(
                                type_data["status"] == "Warning",
                                "orange.500",
                                "red.500",
                            ),
                        ),
                        border_radius="2px",
                    ),
                    rx.hstack(
                        rx.cond(
                            type_data["status"] == "Good",
                            rx.icon("check", size=28, color="green.600"),
                            rx.cond(
                                type_data["status"] == "Warning",
                                rx.icon("triangle-alert", size=28, color="orange.600"),
                                rx.icon("circle-x", size=28, color="red.600"),
                            ),
                        ),
                        rx.vstack(
                            rx.tooltip(
                                rx.text(
                                    type_data["type"],
                                    size="2",
                                    weight="bold",
                                    color="gray.800",
                                    white_space="nowrap",
                                    overflow="hidden",
                                    text_overflow="ellipsis",
                                    max_width="120px",
                                    line_height="1.2",
                                ),
                                content=type_data["type"],
                            ),
                            rx.badge(
                                type_data["status"],
                                size="1",
                                variant="surface",
                                color_scheme=rx.cond(
                                    type_data["status"] == "Good",
                                    "green",
                                    rx.cond(
                                        type_data["status"] == "Warning",
                                        "orange",
                                        "red",
                                    ),
                                ),
                            ),
                            spacing="1",
                            align="start",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    justify="start",
                    align="center",
                    spacing="3",
                    width="100%",
                ),
                # Statistics section - more compact layout
                rx.vstack(
                    # Success rate row
                    rx.hstack(
                        rx.text(
                            "Success Rate",
                            size="1",
                            color="gray.600",
                            weight="medium",
                        ),
                        rx.hstack(
                            rx.text(
                                type_data["success_rate"],
                                size="4",
                                weight="bold",
                                color=rx.cond(
                                    type_data["status"] == "Good",
                                    "green.700",
                                    rx.cond(
                                        type_data["status"] == "Warning",
                                        "orange.700",
                                        "red.700",
                                    ),
                                ),
                            ),
                            rx.text(
                                "%",
                                size="2",
                                color="gray.600",
                            ),
                            spacing="1",
                            align="baseline",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                    ),
                    # ...removed Records row...
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="1.25rem",
            background=rx.cond(
                type_data["status"] == "Good",
                "linear-gradient(135deg, var(--green-25) 0%, var(--green-50) 100%)",
                rx.cond(
                    type_data["status"] == "Warning",
                    "linear-gradient(135deg, var(--orange-25) 0%, var(--orange-50) 100%)",
                    "linear-gradient(135deg, var(--red-25) 0%, var(--red-50) 100%)",
                ),
            ),
            border=rx.cond(
                type_data["status"] == "Good",
                "2px solid var(--green-200)",
                rx.cond(
                    type_data["status"] == "Warning",
                    "2px solid var(--orange-200)",
                    "2px solid var(--red-200)",
                ),
            ),
            border_radius="xl",
            box_shadow=rx.cond(
                type_data["status"] == "Good",
                "0 4px 6px -1px rgba(34, 197, 94, 0.1), 0 2px 4px -1px rgba(34, 197, 94, 0.06)",
                rx.cond(
                    type_data["status"] == "Warning",
                    "0 4px 6px -1px rgba(251, 146, 60, 0.1), 0 2px 4px -1px rgba(251, 146, 60, 0.06)",
                    "0 4px 6px -1px rgba(239, 68, 68, 0.1), 0 2px 4px -1px rgba(239, 68, 68, 0.06)",
                ),
            ),
            _hover={
                "transform": "translateY(-2px)",
                "box_shadow": rx.cond(
                    type_data["status"] == "Good",
                    "0 8px 15px -3px rgba(34, 197, 94, 0.15), 0 4px 6px -2px rgba(34, 197, 94, 0.1)",
                    rx.cond(
                        type_data["status"] == "Warning",
                        "0 8px 15px -3px rgba(251, 146, 60, 0.15), 0 4px 6px -2px rgba(251, 146, 60, 0.1)",
                        "0 8px 15px -3px rgba(239, 68, 68, 0.15), 0 4px 6px -2px rgba(239, 68, 68, 0.1)",
                    ),
                ),
            },
            transition="all 0.2s ease-in-out",
        ),
        href=f"/{route_prefix}/{type_data['type']}",
        style={"text_decoration": "none", "color": "inherit"},
    )


def status_overview_section(
    get_police_type_status,
    route_prefix="police-type",
    section_title="Service Status by Police Type",
) -> rx.Component:
    """Service status overview section component."""
    return rx.vstack(
        rx.hstack(
            rx.heading(section_title, size="5", color="gray.800"),
            rx.badge(
                rx.icon("activity", size=16),
                "Live Status",
                size="2",
                variant="surface",
                color_scheme="blue",
            ),
            justify="between",
            align="center",
            width="100%",
            margin_bottom="1rem",
        ),
        rx.grid(
            rx.foreach(
                get_police_type_status,
                lambda type_data: status_card(type_data, route_prefix),
            ),
            columns=rx.breakpoints(initial="1", sm="2", lg="4"),
            spacing="4",
            width="100%",
        ),
        spacing="3",
        align="start",
        width="100%",
        margin_bottom="2rem",
    )
