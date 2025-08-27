documents = [
    {
        "_id": "SPAIN_HOS",
        "states": [
            {"state": "SUCCESS", "count": 2},
            {"state": "ERROR", "count": 1}
        ],
        "total": 3,
        "docs": [
            {"state": "SUCCESS", "reason": "Confirmed"},
            {"state": "SUCCESS", "reason": "Confirmed"},
            {"state": "INVALID", "reason": "Invalid name format. Name and first surname are required."}
        ]
    },
]


def test_success_rate_calculation():
    from app.states.success_rate_calculator import calculate_success_rate

    success_states = ["SUCCESS"]
    error_states = ["ERROR", "INVALID"]

    expected_results = {
        "SPAIN_HOS": 100.0,  # 2 success / (2 success + 0 error) * 100 (error is expected)
    }

    for doc in documents:
        police_type = doc["_id"]
        states = {state_info["state"]: state_info["count"] for state_info in doc["states"]}
        docs = doc["docs"]

        success_rate = calculate_success_rate(
            states=states,
            success_states=success_states,
            error_states=error_states,
            docs=docs,
            police_type=police_type
        )

        assert round(success_rate, 2) == expected_results[police_type], f"Failed for {police_type}"