import logging
import reflex as rx
from app.components.police.police_dashboard import police_dashboard_page
from app.components.stat.statistics_dashboard import statistics_dashboard_page
from app.components.stat.statistics_type_detail import statistics_type_detail_page
from app.components.police.police_type_detail import police_type_detail_page
from app.states.police.police_data_state import PoliceDataState
from app.states.statistics.statistics_data_state import StatisticsDataState
from app.states.police.navigation_state import NavigationState

logger = logging.getLogger(__name__)


def index() -> rx.Component:
    """Redirect to police dashboard by default."""
    return rx.fragment(
        rx.script("window.location.href = '/police'"),
    )


def police_dashboard() -> rx.Component:
    """Police data dashboard page."""
    return rx.box(
        police_dashboard_page(),
        on_mount=[
            PoliceDataState.fetch_dashboard_stats,
            NavigationState.set_current_route("/police"),
        ],
    )


def statistics_dashboard() -> rx.Component:
    """Statistics dashboard page."""
    return rx.box(
        statistics_dashboard_page(),
        on_mount=NavigationState.set_current_route("/statistics"),
    )


def police_type_detail(police_type: str = "") -> rx.Component:
    """Police type detail page."""
    logger.debug(f"Rendering police_type_detail for police_type: {police_type}")
    return rx.box(
        police_type_detail_page(),
        on_mount=[
            PoliceDataState.fetch_dashboard_stats,
        ],
        width="100%",
        background="linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
    )


def statistics_type_detail(statistics_type: str = "") -> rx.Component:
    """Statistics type detail page."""
    logger.debug(
        f"Rendering statistics_type_detail for " f"statistics_type: {statistics_type}"
    )
    return rx.box(
        statistics_type_detail_page(),
        on_mount=[
            StatisticsDataState.fetch_dashboard_stats,
        ],
        width="100%",
        background="linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)",
    )


app = rx.App(
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ]
)
app.add_page(index)
app.add_page(police_dashboard, route="/police")
app.add_page(statistics_dashboard, route="/statistics")
app.add_page(police_type_detail, route="/police-type/[police_type]")
app.add_page(statistics_type_detail, route="/statistics-type/[statistics_type]")
