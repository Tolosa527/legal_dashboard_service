import reflex as rx
from app.components import (
    sidebar,
    dashboard_header,
    loading_component,
    error_component,
    status_overview_section,
    stats_cards_section,
    charts_section,
)
from app.states.police_data_state import PoliceDataState

def index() -> rx.Component:
    """Main page component with enhanced design cohesion."""
    return rx.box(
        rx.hstack(
            sidebar(),
            rx.cond(
                PoliceDataState.loading,
                loading_component(),
                rx.cond(
                    PoliceDataState.error_message != "",
                    error_component(PoliceDataState.error_message),
                    rx.box(
                        dashboard_header(),
                        # Main content area with enhanced background
                        rx.container(
                            rx.vstack(
                                stats_cards_section(
                                    PoliceDataState.get_total_records,
                                    PoliceDataState.get_success_rate,
                                    PoliceDataState.get_error_count,
                                    PoliceDataState.get_active_types,
                                ),
                                status_overview_section(PoliceDataState.get_police_type_status),
                                # charts_section(
                                #     PoliceDataState.get_police_state_chart_data,
                                #     PoliceDataState.get_police_type_chart_data,
                                # ),
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
                        # Enhanced gradient background that flows from header
                        background="linear-gradient(180deg, rgba(241, 245, 249, 0.8) 0%, rgba(248, 250, 252, 0.95) 20%, rgba(255, 255, 255, 0.98) 100%)",
                        position="relative",
                        # Subtle pattern overlay
                        style={
                            "background_image": "radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.03) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.05) 0%, transparent 50%), radial-gradient(circle at 40% 40%, rgba(59, 130, 246, 0.02) 0%, transparent 50%)"
                        },
                    )
                )
            ),
            spacing="0",
            width="100%",
        ),
        on_mount=PoliceDataState.fetch_police_data,
        width="100%",
        # Overall app background with subtle texture
        background="linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
    )

app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ]
)
app.add_page(index)