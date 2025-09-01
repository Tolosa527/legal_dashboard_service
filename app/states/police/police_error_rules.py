class PoliceErrorRules:
    def is_expected_error(self, error_reason: str, state: str) -> bool:
        """Override in subclasses to define expected errors for each police type."""
        return False


class SpainHosErrorRules(PoliceErrorRules):
    # Example: treat INVALID with specific reason as expected
    EXPECTED_INVALID_REASONS = [
        (
            "Fields 'leader guest phone' and 'invite email': one of these is "
            "required for booking registration."
        ),
        "Field 'leader guest name' is required for booking registration.",
        "Invalid name format. Name and first surname are required.",
        "El nombre contiene caracteres no permitidos.",
        "The credentials are invalid.",
        # Add more as needed from new validation errors
    ]

    def is_expected_error(self, error_reason: str, state: str) -> bool:
        if state == "INVALID" and any(
            msg in error_reason for msg in self.EXPECTED_INVALID_REASONS
        ):
            return True
        return False


class SpainMosErrorRules(PoliceErrorRules):
    EXPECTED_INVALID_REASONS = [
        "Validation error",
        "Postal code does not match expected format",
        "Contains non-printable characters",
        "Field length incorrect",
        "Conté caracters no imprimibles",
        # Add more as needed from new validation errors
    ]

    def is_expected_error(self, error_reason: str, state: str) -> bool:
        if state in ["ERROR", "INVALID"] and any(
            msg in error_reason for msg in self.EXPECTED_INVALID_REASONS
        ):
            return True
        return False


class ItalyIspErrorRules(PoliceErrorRules):
    EXPECTED_INVALID_REASONS = [
        "Wrong credentials",
        "Data di Arrivo Errata",
        # Add more as needed from new validation errors
    ]

    def is_expected_error(self, error_reason: str, state: str) -> bool:
        if state in ["ERROR", "INVALID"] and any(
            msg in error_reason for msg in self.EXPECTED_INVALID_REASONS
        ):
            return True
        return False


class NatErrorRules(PoliceErrorRules):
    EXPECTED_INVALID_REASONS = [
        "exp_date field is required!",
    ]

    def is_expected_error(self, error_reason: str, state: str) -> bool:
        if state in ["ERROR", "INVALID"] and any(
            msg in error_reason for msg in self.EXPECTED_INVALID_REASONS
        ):
            return True
        return False


class PortugalSEFErrorRules(PoliceErrorRules):
    EXPECTED_INVALID_REASONS = [
        "validation errors",
    ]

    def is_expected_error(self, error_reason: str, state: str) -> bool:
        if state in ["ERROR", "INVALID", "CANCELED"] and any(
            msg in error_reason for msg in self.EXPECTED_INVALID_REASONS
        ):
            return True
        return False


class DubaiDTCMErrorRules(PoliceErrorRules):
    EXPECTED_INVALID_REASONS = [
        "not active in DTCM",
    ]

    def is_expected_error(self, error_reason: str, state: str) -> bool:
        if state in ["ERROR", "INVALID"] and any(
            msg in error_reason for msg in self.EXPECTED_INVALID_REASONS
        ):
            return True
        return False
