import reflex as rx
from .police_header import dashboard_header

from app.components.status_cards import status_overview_section
from app.components.stats_cards import stats_cards_section
from app.components.sidebar import sidebar
from .charts import charts_section
from app.components.loading_error import loading_component, error_component
from app.states.police.police_data_state import PoliceDataState


def police_dashboard_page() -> rx.Component:
    """Police data dashboard page component."""
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
                                status_overview_section(
                                    PoliceDataState.get_police_type_status
                                ),
                                charts_section(
                                    PoliceDataState.get_police_state_chart_data,
                                    PoliceDataState.get_police_type_chart_data,
                                ),
                                spacing="8",
                                align="center",
                                width="100%",
                                padding="3rem",
                            ),
                            max_width="1400px",
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
                    ),
                ),
            ),
            spacing="0",
            width="100%",
        ),
        on_mount=PoliceDataState.fetch_police_data,
        width="100%",
        # Overall app background with subtle texture
        background="linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
    )
