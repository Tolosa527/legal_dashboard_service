import reflex as rx


def loading_component() -> rx.Component:
    """Enhanced loading spinner component with modern styling."""
    return rx.center(
        rx.vstack(
            # Enhanced spinner container with backdrop
            rx.box(
                rx.vstack(
                    # Larger, more prominent spinner
                    rx.spinner(
                        size="3",
                        color="blue.600",
                    ),
                    # Animated dots for additional visual feedback
                    rx.hstack(
                        rx.box(
                            width="8px",
                            height="8px",
                            background="blue.500",
                            border_radius="50%",
                            animation="pulse 1.5s ease-in-out 0s infinite",
                        ),
                        rx.box(
                            width="8px",
                            height="8px",
                            background="blue.400",
                            border_radius="50%",
                            animation="pulse 1.5s ease-in-out 0.3s infinite",
                        ),
                        rx.box(
                            width="8px",
                            height="8px",
                            background="blue.300",
                            border_radius="50%",
                            animation="pulse 1.5s ease-in-out 0.6s infinite",
                        ),
                        spacing="2",
                        justify="center",
                        margin_top="1rem",
                    ),
                    spacing="4",
                    align="center",
                ),
                padding="2rem",
                background="rgba(255, 255, 255, 0.95)",
                border="1px solid rgba(59, 130, 246, 0.2)",
                border_radius="xl",
                box_shadow="0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                backdrop_filter="blur(10px)",
            ),
            # Enhanced loading text with subtle animation
            rx.vstack(
                rx.text(
                    "Loading Police Data",
                    size="4",
                    weight="bold",
                    color="gray.800",
                    text_align="center",
                ),
                rx.text(
                    "Please wait while we fetch the latest information...",
                    size="2",
                    color="gray.600",
                    text_align="center",
                    opacity="0.8",
                ),
                spacing="2",
                align="center",
                margin_top="1.5rem",
            ),
            spacing="5",
            align="center",
        ),
        width="100%",
        height="100vh",
        background="linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
    )


def error_component(error_message: str) -> rx.Component:
    """Error display component."""
    return rx.center(
        rx.callout(
            rx.text(f"Error: {error_message}"),
            icon="alert-triangle",
            color_scheme="red",
            size="3",
        ),
        width="100%",
        height="100vh",
    )
