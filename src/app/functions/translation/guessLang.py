import psycopg2
from ..dbconfig import config
from functions.log import logErrorToDB
from fastapi import HTTPException, Response
import traceback
from googletrans import Translator


async def guessLang(text):
    if text in ["", None]:
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": 1,
                "error": "'text' variable empty or not provided.",
            }
        )
    try:
        translator = Translator()
        detected = translator.detect(text)
        print(detected)

        return {
            "detail": {
                "text": text,
                "language": detected.lang,
                "confidence": detected.confidence
            },
            "error_code": 0
        }

    except (Exception, psycopg2.DatabaseError):
        await logErrorToDB(str(traceback.format_exc()))
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": 1,
                "http_code": "500",
                "error": "Translation API error.",
            }
        )
