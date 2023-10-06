from fhirpathpy import evaluate

QR = {
    "resourceType": "QuestionnaireResponse",
    "status": "completed",
    "item": [
        {
            "linkId": "name",
            "item": [
                {"linkId": "last-name", "answer": [{"valueString": "Beda"}]},
                {"linkId": "first-name", "answer": [{"valueString": "Ilya"}]},
                {"linkId": "middle-name", "answer": [{"valueString": "Alekseevich"}]},
            ],
        },
        {"linkId": "birth-date", "answer": [{"valueDate": "2023-05-01"}]},
        {"linkId": "gender", "answer": [{"valueCoding": {"code": "male"}}]},
        {"linkId": "ssn", "answer": [{"valueString": "123"}]},
        {"linkId": "mobile", "answer": [{"valueString": "11231231231"}]},
    ],
}


def test_if_item_in_context_can_be_referenced():
    context = {
        "item": [
            {"linkId": "last-name", "answer": [{"valueString": "Beda"}]},
            {"linkId": "first-name", "answer": [{"valueString": "Ilya"}]},
            {"linkId": "middle-name", "answer": [{"valueString": "Alekseevich"}]},
        ],
    }
    expr = "%item.where(linkId='first-name').answer.valueString"

    result = evaluate(QR, expr, context)
    assert result == ["Ilya"]
