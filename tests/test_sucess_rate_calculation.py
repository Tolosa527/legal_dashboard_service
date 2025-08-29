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


def test_police_success_rate_calculation():
    from app.states.success_rate_utils import calculate_police_success_rate

    success_states = ["SUCCESS"]
    error_states = ["ERROR", "INVALID"]

    expected_results = {
        "SPAIN_HOS": 100.0,  # 2 success / (2 success + 0 error) * 100 (error is expected)
    }

    for doc in documents:
        police_type = doc["_id"]
        states = {state_info["state"]: state_info["count"] for state_info in doc["states"]}
        docs = doc["docs"]

        success_rate = calculate_police_success_rate(
            success_count=sum(
                count for state, count
                in states.items() if state in success_states
            ),
            error_states=error_states,
            docs=docs,
            police_type=police_type
        )

        assert round(success_rate, 2) == expected_results[police_type], f"Failed for {police_type}"


stat_documents = [
    {
        "_id": "ITLA",
        "status_check_in": [
            {"state": "COMPLETE", "count": 1},
            {"state": "ERROR", "count": 1},
            {"state": "COMPLETE", "count": 1},
        ],
        "status_check_out": [
            {"state": "COMPLETE", "count": 1},
            {"state": "ERROR", "count": 1},
            {"state": "COMPLETE", "count": 1},
        ],
        "docs": [
            {
                "status_check_in": "COMPLETE",
                "status_check_out": "COMPLETE",
                "status_check_in_details": "Reservation(3b58258d980040709a57959dd0ee0153) check-in: status - COMPLETE, response - <soap:Envelope ...>",
                "status_check_out_details": "Reservation(3b58258d980040709a57959dd0ee0153) check-out: status - COMPLETE, response - <soap:Envelope ...>"
            },
            {
                "status_check_in": "ERROR",
                "status_check_out": "COMPLETE",
                "status_check_in_details": "Reservation(57304ddceba5492e9a01981eddaa9095) check-in: status - ERROR, response - <soap:Envelope ...>",
                "status_check_out_details": "Reservation(57304ddceba5492e9a01981eddaa9095) check-out: status - COMPLETE, response - <soap:Envelope ...>"
            },
        ],
        "total": 66
    }
]


def test_stat_success_rate_calculation():
    from app.states.success_rate_utils import calculate_stat_success_rate

    error_states = ["ERROR", "INVALID"]
    expected_success_rate = 50.0

    for doc in stat_documents:
        stat_type = doc["_id"]

        success_rate = calculate_stat_success_rate(
            success_count=1,
            error_states=error_states,
            docs=doc["docs"],
            stat_type=stat_type,
        )

        assert round(success_rate, 2) == expected_success_rate, f"Failed for {stat_type}"
