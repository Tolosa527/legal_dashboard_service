import reflex as rx


import reflex as rx


def sidebar_link(text: str, url: str, is_active: bool, icon: str) -> rx.Component:
    """Enhanced sidebar link component with modern styling."""
    return rx.link(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text, size="2", weight="medium"),
            spacing="3",
            align="center",
            padding="0.75rem 1rem",
            border_radius="lg",
            background=rx.cond(
                is_active,
                "linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(147, 51, 234, 0.1) 100%)",
                "transparent",
            ),
            color=rx.cond(
                is_active,
                "blue.700",
                "gray.700",
            ),
            border=rx.cond(
                is_active,
                "1px solid rgba(59, 130, 246, 0.2)",
                "1px solid transparent",
            ),
            _hover={
                "background": rx.cond(
                    is_active,
                    "linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(147, 51, 234, 0.15) 100%)",
                    "linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 51, 234, 0.03) 100%)",
                ),
                "transform": "translateX(4px)",
                "transition": "all 0.2s ease",
                "box_shadow": "0 2px 8px rgba(59, 130, 246, 0.1)",
            },
            width="100%",
            transition="all 0.2s ease",
            position="relative",
        ),
        href=url,
        text_decoration="none",
        width="100%",
    )


def sidebar() -> rx.Component:
    """Enhanced sidebar component with modern cohesive styling."""
    return rx.box(
        # Header section with enhanced styling
        rx.vstack(
            rx.hstack(
                rx.box(
                    rx.icon("shield", size=24, color="white"),
                    padding="8px",
                    background="linear-gradient(135deg, var(--blue-9) 0%, var(--purple-9) 100%)",
                    border_radius="10px",
                    box_shadow="0 2px 8px rgba(59, 130, 246, 0.3)",
                ),
                rx.vstack(
                    rx.text("Legal Dashboard", size="3", weight="bold", color="gray.800"),
                    rx.text("Command Center", size="1", color="gray.600"),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="center",
            ),
            spacing="2",
            align="start",
            padding="1.5rem 1rem",
            # Enhanced header background
            background="linear-gradient(135deg, rgba(248, 250, 252, 0.8) 0%, rgba(241, 245, 249, 0.9) 100%)",
            border_bottom="1px solid rgba(59, 130, 246, 0.1)",
            position="relative",
            # Subtle pattern
            style={
                "background_image": "radial-gradient(circle at 70% 30%, rgba(59, 130, 246, 0.05) 0%, transparent 50%)"
            },
        ),
        
        # Navigation section with enhanced styling
        rx.vstack(
            rx.text("Analytics", size="2", weight="bold", color="gray.500", margin_bottom="0.5rem"),
            sidebar_link("Police Services Report", "#", True, "bar-chart-3"),
            sidebar_link("Statistics Report", "#", False, "pie-chart"),
            sidebar_link("Data Insights", "#", False, "trending-up"),
            sidebar_link("Export Data", "#", False, "download"),
            spacing="1",
            align="start",
            padding="1rem",
            width="100%",
        ),
        
        # Footer section with enhanced styling
        rx.box(
            rx.vstack(
                rx.divider(color_scheme="gray", opacity="0.3"),
                rx.hstack(
                    rx.icon("settings", size=16, color="gray.600"),
                    rx.text("Settings", size="2", color="gray.600", weight="medium"),
                    spacing="2",
                    align="center",
                    padding="0.75rem",
                    border_radius="lg",
                    _hover={
                        "background": "linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(147, 51, 234, 0.05) 100%)",
                        "transform": "translateX(2px)",
                        "transition": "all 0.2s ease",
                    },
                    cursor="pointer",
                    transition="all 0.2s ease",
                ),
                spacing="3",
                width="100%",
            ),
            position="absolute",
            bottom="1rem",
            left="1rem",
            right="1rem",
        ),
        
        width="280px",
        height="100vh",
        # Enhanced gradient background that complements the header
        background="linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 250, 252, 0.98) 50%, rgba(241, 245, 249, 0.95) 100%)",
        border_right="1px solid rgba(59, 130, 246, 0.15)",
        position="sticky",
        top="0",
        left="0",
        # Enhanced shadow with color
        box_shadow="4px 0 15px -3px rgba(0, 0, 0, 0.1), 2px 0 6px -2px rgba(59, 130, 246, 0.05)",
        class_name="max-lg:hidden",
        # Subtle backdrop filter
        backdrop_filter="blur(10px)",
        # Pattern overlay
        style={
            "background_image": "radial-gradient(circle at 90% 10%, rgba(59, 130, 246, 0.03) 0%, transparent 50%), radial-gradient(circle at 10% 90%, rgba(147, 51, 234, 0.02) 0%, transparent 50%)"
        },
    )
