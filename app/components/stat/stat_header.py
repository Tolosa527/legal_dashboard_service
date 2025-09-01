import reflex as rx
from datetime import datetime

def dashboard_header() -> rx.Component:
    """Enhanced header component with modern styling and real-time indicators."""
    return rx.box(
        # Main header content
        rx.container(
            rx.vstack(
                # Top row with logo and status indicators
                rx.hstack(
                    # Logo and title section
                    rx.hstack(
                        rx.box(
                            rx.icon(
                                "shield-check",
                                size=36,
                                color="white",
                            ),
                            padding="12px",
                            background="rgba(255, 255, 255, 0.15)",
                            border_radius="12px",
                            backdrop_filter="blur(10px)",
                            border="1px solid rgba(255, 255, 255, 0.2)",
                            class_name="glass-effect smooth-transition",
                        ),
                        rx.vstack(
                            rx.heading(
                                "Statatistic Data Dashboard",
                                size="7",
                                color="white",
                                font_weight="700",
                                letter_spacing="-0.025em",
                                class_name="header-title",
                            ),
                            rx.text(
                                "Legal Services Command Center",
                                size="3",
                                color="rgba(255, 255, 255, 0.85)",
                                font_weight="500",
                            ),
                            spacing="1",
                            align="start",
                        ),
                        spacing="4",
                        align="center",
                    ),
                    # Status indicators and time
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.hstack(
                                    rx.box(
                                        width="8px",
                                        height="8px",
                                        background="var(--green-9)",
                                        border_radius="50%",
                                        style={"animation": "pulse 2s infinite"},
                                    ),
                                    rx.text(
                                        "Live",
                                        size="2",
                                        color="white",
                                        font_weight="600",
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                                padding="8px 12px",
                                background="rgba(34, 197, 94, 0.2)",
                                border_radius="20px",
                                border="1px solid rgba(34, 197, 94, 0.3)",
                                class_name="status-badge smooth-transition",
                                _hover={
                                    "transform": "translateY(-1px)",
                                    "box_shadow": "0 4px 12px rgba(34, 197, 94, 0.3)",
                                },
                            ),
                            rx.box(
                                rx.hstack(
                                    rx.icon("database", size=16, color="white"),
                                    rx.text(
                                        "Connected",
                                        size="2",
                                        color="white",
                                        font_weight="600",
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                                padding="8px 12px",
                                background="rgba(59, 130, 246, 0.2)",
                                border_radius="20px",
                                border="1px solid rgba(59, 130, 246, 0.3)",
                                class_name="status-badge smooth-transition",
                                _hover={
                                    "transform": "translateY(-1px)",
                                    "box_shadow": "0 4px 12px rgba(59, 130, 246, 0.3)",
                                },
                            ),
                            spacing="3",
                            class_name="header-badges",
                        ),
                        rx.hstack(
                            rx.icon("clock", size=14, color="rgba(255, 255, 255, 0.7)"),
                            rx.text(
                                f"Updated: {datetime.now().strftime('%H:%M')}",
                                size="1",
                                color="rgba(255, 255, 255, 0.7)",
                                font_weight="500",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        spacing="2",
                        align="end",
                    ),
                    justify="between",
                    align="start",
                    width="100%",
                    class_name="header-content",
                ),
                # Subtitle and description
                rx.vstack(
                    rx.text(
                        "Real-time analytics and monitoring for statistic data services",
                        size="4",
                        color="rgba(255, 255, 255, 0.9)",
                        text_align="center",
                        font_weight="500",
                        line_height="1.6",
                        max_width="600px",
                    ),
                    rx.hstack(
                        rx.badge(
                            rx.icon("trending-up", size=12),
                            "Active Monitoring",
                            size="2",
                            variant="surface",
                            color_scheme="blue",
                            class_name="smooth-transition",
                            _hover={"transform": "scale(1.05)"},
                        ),
                        rx.badge(
                            rx.icon("shield", size=12),
                            "Secure Access",
                            size="2",
                            variant="surface",
                            color_scheme="green",
                            class_name="smooth-transition",
                            _hover={"transform": "scale(1.05)"},
                        ),
                        rx.badge(
                            rx.icon("activity", size=12),
                            "Real-time Data",
                            size="2",
                            variant="surface",
                            color_scheme="purple",
                            class_name="smooth-transition",
                            _hover={"transform": "scale(1.05)"},
                        ),
                        spacing="3",
                        justify="center",
                        wrap="wrap",
                        class_name="header-badges",
                    ),
                    spacing="3",
                    align="center",
                    width="100%",
                ),
                spacing="6",
                align="center",
                width="100%",
                padding_y="2.5rem",
                class_name="header-content",
            ),
            max_width="1200px",
            margin_x="auto",
            padding_x="2rem",
        ),
        # Enhanced background with multiple layers
        background="linear-gradient(135deg, var(--blue-10) 0%, var(--purple-10) 50%, var(--violet-10) 100%)",
        position="relative",
        width="100%",
        overflow="hidden",
        class_name="header-pattern enhanced-shadow",
        # Box shadow for depth
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        border_bottom="1px solid rgba(255, 255, 255, 0.1)",
        # Subtle background pattern
        style={
            "background_image": "radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.1) 0%, transparent 50%), radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.05) 0%, transparent 50%)"
        },
    )
