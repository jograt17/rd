from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


class CustomError(Exception):
    def __init__(self, code, name, message, payload=None):
        super().__init__(name, message, payload)
        self.code = code
        self.name = name
        self.message = message
        self.payload = payload


def custom_error_response(
    error_code: int, error_name: str, message: str, details: any = None
):
    error_content = {"error": error_name, "message": message, "details": details}
    return JSONResponse(status_code=error_code, content=jsonable_encoder(error_content))
