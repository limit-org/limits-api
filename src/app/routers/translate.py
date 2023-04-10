from fastapi import APIRouter


from functions.translation.translate import translate
from functions.translation.guessLang import guessLang


router = APIRouter()


@router.get('/translate/text/', tags=["translate"], status_code=200)
async def translateText(text, toLang):
    return await translate(text, toLang)


@router.get('/translate/detect/', tags=["translate"], status_code=200)
async def detectTextLang(text):
    return await guessLang(text)
