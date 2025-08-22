from django.core.exceptions import ValidationError

BANNED_WORDS = {"spam", "fake", "scam", "дурь", "запрещенка"}

def validate_no_banned_words(value: str):
    low = (value or "").lower()
    for w in BANNED_WORDS:
        if w in low:
            raise ValidationError("Текст содержит запрещенные слова.")
