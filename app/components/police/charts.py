import reflex as rx


def pie_chart_card(
    title: str, icon: str, icon_color: str, chart_data, cell_colors: list
) -> rx.Component:
    """Clean and readable pie chart card component."""
    return rx.card(
        rx.vstack(
            # Simple, clean header
            rx.hstack(
                rx.icon(icon, size=24, color=icon_color),
                rx.heading(
                    title,
                    size="4",
                    color="gray.800",
                    font_weight="600",
                ),
                justify="start",
                align="center",
                spacing="3",
                margin_bottom="1.5rem",
            ),
            # Clean pie chart with optimal sizing
            rx.recharts.pie_chart(
                rx.recharts.pie(
                    *[
                        rx.recharts.cell(
                            fill=color,
                            stroke="white",
                            stroke_width=2,
                        )
                        for color in cell_colors
                    ],
                    data=chart_data,
                    data_key="value",
                    name_key="name",
                    cx="50%",
                    cy="50%",
                    outer_radius="100",
                    label=True,
                    label_line=True,
                ),
                rx.recharts.legend(
                    vertical_align="bottom",
                    height=50,
                ),
                rx.recharts.graphing_tooltip(
                    separator=": ",
                    content_style={
                        "background": "white",
                        "border": "1px solid #e2e8f0",
                        "border_radius": "6px",
                        "box_shadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                    },
                ),
                width="100%",
                height=400,
            ),
            spacing="6",
            align="center",
            width="100%",
        ),
        padding="3rem",
        background="white",
        border="1px solid var(--gray-200)",
        border_radius="lg",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1)",
    )


def charts_section(
    get_police_state_chart_data, get_police_type_chart_data
) -> rx.Component:
    """Clean charts section with improved state and type distributions."""
    # Professional color scheme for states
    state_colors = [
        "#16A34A",  # Green for SUCCESS
        "#DC2626",  # Red for ERROR
        "#2563EB",  # Blue for NEW
        "#D97706",  # Amber for COMPLETE
        "#7C3AED",  # Purple for CANCELED
        "#64748B",  # Gray for INVALID
        "#EC4899",  # Pink for other states
        "#0891B2",  # Teal
        "#65A30D",  # Lime
        "#EA580C",  # Orange
    ]

    # Professional color scheme for types
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
        "#14B8A6",  # Teal
        "#F43F5E",  # Rose
    ]

    return rx.vstack(
        # Section header
        rx.text(
            "Data Analytics Overview",
            size="6",
            weight="bold",
            color="gray.800",
            margin_bottom="2rem",
        ),
        # Chart grid with increased spacing
        rx.grid(
            pie_chart_card(
                "State Distribution",
                "pie-chart",
                "blue",
                get_police_state_chart_data,
                state_colors,
            ),
            pie_chart_card(
                "Police Type Distribution",
                "users",
                "green",
                get_police_type_chart_data,
                type_colors,
            ),
            columns="2",
            spacing="9",
            width="100%",
        ),
        spacing="6",
        align="start",
        width="100%",
        padding="3rem",
    )
