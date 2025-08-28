import reflex as rx


class NavigationState(rx.State):
    """State to manage navigation and sidebar active states."""

    current_route: str = "/police"

    @rx.event
    def set_current_route(self, route: str):
        """Set the current route."""
        self.current_route = route

    @rx.var
    def is_police_active(self) -> bool:
        """Check if police dashboard is active."""
        return self.current_route in ["/", "/police"]

    @rx.var
    def is_statistics_active(self) -> bool:
        """Check if statistics dashboard is active."""
        return self.current_route == "/statistics"
