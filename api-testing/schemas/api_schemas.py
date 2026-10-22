"""
================================================================================
EVMOTO & ECGO API CONTRACT SCHEMAS (JSON SCHEMA SPECIFICATION)
================================================================================
Mendefinisikan skema JSON untuk validasi kontrak data respons API.
Digunakan oleh jsonschema.validate() pada automated test suite.
================================================================================
"""

# ==============================================================================
# 1. AUTH SCHEMAS
# ==============================================================================
DRIVER_LOGIN_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "integer", "enum": [200]},
        "msg": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["id", "token"],
            "properties": {
                "id": {"type": "integer"},
                "token": {"type": "string", "minLength": 10},
                "status": {"type": "integer"},
                "isBind": {"type": "integer"}
            }
        }
    }
}

DRIVER_LOGIN_ERROR_SCHEMA = {
    "type": "object",
    "required": ["code", "msg"],
    "properties": {
        "code": {"type": "integer", "not": {"enum": [200]}},
        "msg": {"type": "string"}
    }
}

ECGO_GENERATE_OTP_SCHEMA = {
    "type": "object",
    "required": ["message", "otp"],
    "properties": {
        "message": {"type": "string"},
        "otp": {
            "type": "object",
            "required": ["id", "code", "userPhoneNumber"],
            "properties": {
                "id": {"type": "integer"},
                "code": {"type": "integer"},
                "userPhoneNumber": {"type": "string"}
            }
        }
    }
}

ECGO_VERIFY_OTP_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["message", "token", "status"],
    "properties": {
        "message": {"type": "string"},
        "token": {"type": "string", "minLength": 10},
        "status": {"type": "string", "enum": ["verified", "success"]}
    }
}

# ==============================================================================
# 2. DRIVER DATA & WALLET SCHEMAS (GOLANG BACKEND)
# ==============================================================================
DRIVER_HOME_DATA_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "integer", "enum": [200]},
        "msg": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["licensePlate", "brand"],
            "properties": {
                "licensePlate": {"type": "string"},
                "brand": {"type": "string"},
                "score": {"type": "number"},
                "activity": {"type": "integer"},
                "work": {"type": "integer"}
            }
        }
    }
}

DRIVER_WALLET_STATUS_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "integer", "enum": [200]},
        "msg": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["status", "linked"],
            "properties": {
                "status": {"type": "string"},
                "linked": {"type": "boolean"},
                "phoneMasked": {"type": "string"}
            }
        }
    }
}

# ==============================================================================
# 3. ECGO CONNECT & COUPON DISCOUNTS SCHEMAS (SUPERAPPS BACKEND)
# ==============================================================================
ECGO_CONNECT_STATUS_SCHEMA = {
    "type": "object",
    "required": ["success", "status", "linked"],
    "properties": {
        "success": {"type": "boolean"},
        "status": {"type": "string"},
        "linked": {"type": "boolean"},
        "couponGranted": {"type": "boolean"},
        "hasVehicle": {"type": "boolean"}
    }
}

ECGO_DISCOUNTS_SCHEMA = {
    "type": "object",
    "required": ["message", "data"],
    "properties": {
        "message": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["count", "rows"],
            "properties": {
                "count": {"type": "integer", "minimum": 0},
                "rows": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["id", "name", "status", "amount"],
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "status": {"type": "string"},
                            "amount": {"type": "integer", "minimum": 1, "maximum": 100},
                            "type": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
}

# ==============================================================================
# 4. PASSENGER / USER SCHEMAS (USER MOBILE BACKEND)
# ==============================================================================
USER_LOGIN_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "integer", "enum": [200]},
        "msg": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["id", "token"],
            "properties": {
                "id": {"type": "integer"},
                "token": {"type": "string", "minLength": 10},
                "status": {"type": "integer"}
            }
        }
    }
}

USER_ESTIMATE_FARE_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "integer", "enum": [200]},
        "msg": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["distanceKm", "totalFare", "currency"],
            "properties": {
                "distanceKm": {"type": "number", "minimum": 0},
                "totalFare": {"type": "integer", "minimum": 0},
                "baseFare": {"type": "integer"},
                "pricePerKm": {"type": "integer"},
                "currency": {"type": "string", "enum": ["IDR"]}
            }
        }
    }
}

USER_CREATE_ORDER_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "integer", "enum": [200]},
        "msg": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["orderId", "status"],
            "properties": {
                "orderId": {"type": "string"},
                "status": {"type": "string"},
                "totalFare": {"type": "integer"}
            }
        }
    }
}

