import reflex as rx
from app.components.police.police_dashboard import police_dashboard_page
from app.components.police.statistics_dashboard import statistics_dashboard_page
from app.components.police.police_type_detail import police_type_detail_page
from app.states.police.police_data_state import PoliceDataState
from app.states.police.navigation_state import NavigationState


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
    return rx.box(
        police_type_detail_page(),
        on_mount=[
            PoliceDataState.fetch_dashboard_stats,
            PoliceDataState.set_selected_police_type(police_type),
            NavigationState.set_current_route("/police"),
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
