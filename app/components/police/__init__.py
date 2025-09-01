"""Dashboard components module."""

from .police_header import dashboard_header
from .charts import pie_chart_card, charts_section
from .police_type_detail import police_type_detail_page
from .police_dashboard import police_dashboard_page

__all__ = [
    "dashboard_header",
    "pie_chart_card",
    "charts_section",
    "police_type_detail_page",
    "police_dashboard_page",
]
