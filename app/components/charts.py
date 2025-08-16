import reflex as rx


def pie_chart_card(title: str, icon: str, icon_color: str, chart_data, cell_colors: list) -> rx.Component:
    """Reusable pie chart card component."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=24, color=icon_color),
                rx.heading(title, size="4", color="gray.800"),
                justify="start",
                align="center",
                spacing="2",
                margin_bottom="1rem",
            ),
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    *[rx.recharts.cell(fill=color) for color in cell_colors],
                    data=chart_data,
                    data_key="value",
                    name_key="name",
                    cx="50%",
                    cy="50%",
                    outer_radius="90",
                    label=True,
                ),
                rx.recharts.legend(),
                rx.recharts.graphing_tooltip(),
                width="100%",
                height=350,
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        padding="2rem",
        box_shadow="lg",
        border_radius="lg",
    )


def charts_section(get_police_state_chart_data, get_police_type_chart_data) -> rx.Component:
    """Charts section component with state and type distribution."""
    state_colors = [
        "#10B981",  # Green for SUCCESS
        "#EF4444",  # Red for ERROR
        "#3B82F6",  # Blue for NEW
        "#F59E0B",  # Amber for COMPLETE
        "#8B5CF6",  # Purple for CANCELED
        "#6B7280",  # Gray for INVALID
        "#EC4899",  # Pink for other states
    ]
    
    type_colors = [
        "#3B82F6",  # Blue
        "#10B981",  # Green
        "#F59E0B",  # Amber
        "#EF4444",  # Red
        "#8B5CF6",  # Purple
        "#EC4899",  # Pink
        "#06B6D4",  # Cyan
        "#84CC16",  # Lime
        "#F97316",  # Orange
        "#6366F1",  # Indigo
    ]
    
    return rx.vstack(
        rx.text(
            "Data Overview", 
            size="6", 
            weight="bold",
            color="gray.800",
            margin_bottom="1rem",
        ),
        rx.grid(
            pie_chart_card(
                "Police Data by State",
                "pie-chart",
                "blue",
                get_police_state_chart_data,
                state_colors
            ),
            pie_chart_card(
                "Police Data by Type",
                "users",
                "green",
                get_police_type_chart_data,
                type_colors
            ),
            columns="2",
            spacing="6",
            width="100%",
        ),
        spacing="3",
        align="start",
        width="100%",
    )
