age_distribution_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "minAge": {
                "type": "integer",
                "minimum": 0
            },
            "maxAge": {
                "type": "integer",
                "minimum": 0
            },
            "value": {
                "type": "number"
            }
        },
        "required": [
            "minAge",
            "value"
        ],
        "additionalProperties": False,
        "anyOf": [
            {
                "required": ["maxAge"]
            },
            {
                "not": {
                    "required": ["maxAge"]
                }
            }
        ]
    }
}

top_countries_traffic_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "countryAlpha2Code": {
                "type": "string",
                "pattern": "^[A-Z]{2}$"
            },
            "countryUrlCode": {
                "type": "string",
                "pattern": "^[a-z\\-]+$"
            },
            "visitsShare": {
                "type": "number"
            },
            "visitsShareChange": {
                "type": "number"
            }
        },
        "required": [
            "countryAlpha2Code",
            "countryUrlCode",
            "visitsShare",
            "visitsShareChange"
        ],
        "additionalProperties": False
    }
}

visits_history_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "patternProperties": {
        "^\\d{4}-\\d{2}-\\d{2}$": {
            "type": "integer",
            "minimum": 0
        }
    },
    "additionalProperties": False
}
