import reflex as rx
from app.components.sidebar import sidebar


def statistics_dashboard_header() -> rx.Component:
    """Header component for the statistics dashboard page."""
    return rx.box(
        rx.container(
            rx.vstack(
                # Page title
                rx.hstack(
                    rx.heading(
                        "Statistics Data Dashboard",
                        size="7",
                        color="gray.800",
                        weight="bold",
                    ),
                    rx.badge(
                        "Under Construction",
                        size="2",
                        variant="surface",
                        color_scheme="orange",
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                ),
                rx.text(
                    "Advanced statistical analysis and reporting dashboard",
                    size="3",
                    color="gray.600",
                    margin_top="0.5rem",
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
        background="linear-gradient(135deg, rgba(251, 146, 60, 0.1) 0%, rgba(245, 158, 11, 0.1) 100%)",
        border_bottom="1px solid var(--gray-200)",
    )


def construction_placeholder() -> rx.Component:
    """Construction placeholder component."""
    return rx.card(
        rx.vstack(
            rx.icon("construction", size=64, color="orange.500"),
            rx.heading(
                "Dashboard Under Construction",
                size="6",
                color="gray.800",
                text_align="center",
            ),
            rx.text(
                "We're working hard to bring you an amazing statistics dashboard experience.",
                size="3",
                color="gray.600",
                text_align="center",
                max_width="500px",
            ),
            rx.text(
                "This dashboard will include:",
                size="2",
                color="gray.700",
                weight="medium",
                margin_top="1.5rem",
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon("check", size=16, color="green.600"),
                    rx.text(
                        "Advanced statistical analysis", size="2", color="gray.600"
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("check", size=16, color="green.600"),
                    rx.text("Data trend visualization", size="2", color="gray.600"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("check", size=16, color="green.600"),
                    rx.text("Predictive analytics", size="2", color="gray.600"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("check", size=16, color="green.600"),
                    rx.text("Custom reporting tools", size="2", color="gray.600"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.icon("check", size=16, color="green.600"),
                    rx.text(
                        "Export and sharing capabilities", size="2", color="gray.600"
                    ),
                    spacing="2",
                    align="center",
                ),
                spacing="3",
                align="start",
                margin_top="1rem",
            ),
            rx.button(
                rx.icon("arrow-left", size=16),
                "Back to Police Dashboard",
                color_scheme="blue",
                variant="surface",
                size="3",
                margin_top="2rem",
                on_click=rx.redirect("/police"),
            ),
            spacing="4",
            align="center",
            padding="3rem",
        ),
        padding="2rem",
        background="white",
        border="2px dashed var(--orange-300)",
        border_radius="xl",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        min_height="500px",
        max_width="600px",
        margin="auto",
    )


def statistics_dashboard_page() -> rx.Component:
    """Main component for the statistics dashboard page."""
    return rx.box(
        rx.hstack(
            sidebar(),
            rx.box(
                statistics_dashboard_header(),
                rx.container(
                    rx.vstack(
                        construction_placeholder(),
                        spacing="6",
                        align="center",
                        width="100%",
                        padding="2rem",
                    ),
                    max_width="1200px",
                    margin_x="auto",
                ),
                width="100%",
                min_height="100vh",
                background="linear-gradient(180deg, rgba(251, 191, 36, 0.05) 0%, rgba(245, 158, 11, 0.05) 20%, rgba(255, 255, 255, 0.98) 100%)",
            ),
            spacing="0",
            width="100%",
        ),
        width="100%",
        background="linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
    )
