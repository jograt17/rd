from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class CustomError(Exception):
    def __init__(self, code, name, message, payload=None):
        super().__init__(message)
        self.code = code
        self.name = name
        self.message = message
        self.payload = payload


class DatabaseError(CustomError):
    def __init__(
        self,
        payload=None,
    ):
        super().__init__(
            500,
            "DatabaseError",
            "Database Error Occured",
            payload,
        )


class ServiceError(CustomError):
    def __init__(
        self,
        message,
        payload=None,
    ):
        super().__init__(
            500,
            "ServiceError",
            message,
            payload,
        )
        self.name = "ServiceError"


class CustomValidationError(CustomError):
    def __init__(
        self,
        message,
        payload=None,
    ):
        super().__init__(
            422,
            "RequestValidationError",
            message,
            payload,
        )


class NotFoundError(CustomError):
    def __init__(
        self,
        message,
        payload=None,
    ):
        super().__init__(
            404,
            "NotFound",
            message,
            payload,
        )


class RouterError(CustomError):
    def __init__(
        self,
        message,
        payload=None,
    ):
        super().__init__(
            500,
            "RouterError",
            message,
            payload,
        )


def custom_error_response(error_code: int, error_name: str, message: str, details: any = None):
    error_content = {"error": error_name, "message": message, "details": details}
    return JSONResponse(status_code=error_code, content=jsonable_encoder(error_content))
