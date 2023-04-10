import psycopg2
from ..dbconfig import config
from functions.log import logErrorToDB
from fastapi import HTTPException, Response
import traceback
from googletrans import Translator


async def translate(text, toLang):
    if [toLang, text] in ["", None]:
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": 1,
                "error": "'toLang' or 'text' variable is empty or not provided.",
            }
        )
    try:
        translator = Translator()
        print(translator.translate(text, dest=toLang))
        translated = translator.translate(text, dest=toLang)
        print(translated)

        return {
            "detail": {
                "untranslated": text,
                "translated": translated.text
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
