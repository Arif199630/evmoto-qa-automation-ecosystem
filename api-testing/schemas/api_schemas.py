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

# ==============================================================================
# 5. NEW FEATURES SCHEMAS (FITUR 2, 3, & 5)
# ==============================================================================

FREE_SWAP_DAILY_PAYOUT_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "integer", "enum": [200]},
        "msg": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["date", "allocatedCount", "eligibleDrivers"],
            "properties": {
                "date": {"type": "string"},
                "totalEvaluated": {"type": "integer", "minimum": 0},
                "allocatedCount": {"type": "integer", "minimum": 0},
                "quotaRemaining": {"type": "integer", "minimum": 0},
                "redisLockKey": {"type": "string"},
                "eligibleDrivers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["driverId", "onlineMinutesWindow", "linkedAt", "couponStatus"],
                        "properties": {
                            "driverId": {"type": "integer"},
                            "onlineMinutesWindow": {"type": "integer"},
                            "linkedAt": {"type": "string"},
                            "couponStatus": {"type": "string", "enum": ["RESERVED", "ISSUED", "REJECTED_UNLINKED", "QUOTA_EXCEEDED"]},
                            "ecgoCouponId": {"type": ["string", "integer", "null"]}
                        }
                    }
                }
            }
        }
    }
}

USER_ONBOARDING_VOUCHER_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "integer", "enum": [200]},
        "msg": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["userId", "companyId", "vouchersIssued", "totalDiscountValue"],
            "properties": {
                "userId": {"type": "integer"},
                "companyId": {"type": "integer"},
                "packageId": {"type": "integer"},
                "vouchersIssued": {"type": "integer", "minimum": 0},
                "totalDiscountValue": {"type": "number", "minimum": 0},
                "budgetDeducted": {"type": "number", "minimum": 0},
                "vouchers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["couponId", "amount", "expireTime"],
                        "properties": {
                            "couponId": {"type": "integer"},
                            "amount": {"type": "number"},
                            "expireTime": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
}

RUSH_HOUR_SUBSIDY_SCHEMA = {
    "type": "object",
    "required": ["code", "msg", "data"],
    "properties": {
        "code": {"type": "integer", "enum": [200]},
        "msg": {"type": "string"},
        "data": {
            "type": "object",
            "required": ["orderId", "driverId", "subsidyAmount", "tierApplied", "windowMatched", "isGuaranteedIncomeExempt"],
            "properties": {
                "orderId": {"type": "string"},
                "driverId": {"type": "integer"},
                "vehicleType": {"type": "integer"},
                "orderMoneyRaw": {"type": "number"},
                "orderMoneyRounded": {"type": "integer"},
                "evaluatedTime": {"type": "string"},
                "windowMatched": {"type": "string"},
                "tierApplied": {"type": "integer", "enum": [0, 1, 2, 3]},
                "subsidyAmount": {"type": "integer", "enum": [0, 3000, 4000, 5000]},
                "balanceChangeType": {"type": "integer", "enum": [23]},
                "incomeType": {"type": "integer", "enum": [1]},
                "isGuaranteedIncomeExempt": {"type": "boolean"}
            }
        }
    }
}


