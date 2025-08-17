"""Dashboard components module."""

from .sidebar import sidebar, sidebar_link
from .header import dashboard_header
from .loading_error import loading_component, error_component
from .status_cards import status_card, status_overview_section
from .stats_cards import metric_card, stats_cards_section
from .charts import pie_chart_card, charts_section
from .police_type_detail import police_type_detail_page
from .police_dashboard import police_dashboard_page
from .statistics_dashboard import statistics_dashboard_page

__all__ = [
    "sidebar",
    "sidebar_link",
    "dashboard_header",
    "loading_component",
    "error_component",
    "status_card",
    "status_overview_section",
    "metric_card",
    "stats_cards_section",
    "pie_chart_card",
    "charts_section",
    "police_type_detail_page",
    "police_dashboard_page",
    "statistics_dashboard_page",
]