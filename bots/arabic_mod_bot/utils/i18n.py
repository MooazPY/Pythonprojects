"""
Multi-Language (i18n) translation resolver for Haris Pro.
Supports Arabic (ar) and English (en) locale strings with template formatting.
"""

from __future__ import annotations
from typing import Dict, Any

MESSAGES: Dict[str, Dict[str, str]] = {
    "ar": {
        "permission_error": "❌ **خطأ:** ليس لديك الصلاحية الكافية لاستخدام هذا الأمر.",
        "role_error": "❌ **خطأ:** تحتاج إلى رتبة `{role}` لاستخدام هذا الأمر.",
        "cooldown_error": "⏳ **الأمر قيد الانتظار:** برجاء الانتظار `{seconds}` ثانية قبل إعادة الاستخدام.",
        "unexpected_error": "❌ **خطأ غير متوقع:** حدث خطأ أثناء تنفيذ الأمر.",
        "lang_changed": "✅ تم تغيير لغة السيرفر إلى: **العربية**",
        "appeal_title": "📝 تقديم طلب اعتراض على الإجراء الإداري",
        "appeal_submitted": "✅ **تم إرسال طلب الاعتراض بنجاح.** سيتم مراجعته من قبل إدارة السيرفر.",
        "appeal_accepted": "✅ **تم قبول الاعتراض:** تم إلغاء العقوبة بنجاح.",
        "appeal_rejected": "❌ **تم رفض الاعتراض:** رفضت الإدارة طلب الاعتراض المكتوب.",
    },
    "en": {
        "permission_error": "❌ **Error:** You do not have sufficient permissions to run this command.",
        "role_error": "❌ **Error:** You need the `{role}` role to run this command.",
        "cooldown_error": "⏳ **Cooldown:** Please wait `{seconds}`s before trying again.",
        "unexpected_error": "❌ **Unexpected Error:** An error occurred while processing the command.",
        "lang_changed": "✅ Server language updated to: **English**",
        "appeal_title": "📝 Submit Moderation Appeal",
        "appeal_submitted": "✅ **Appeal submitted successfully.** Server moderators will review your request.",
        "appeal_accepted": "✅ **Appeal Approved:** Penalty has been successfully lifted.",
        "appeal_rejected": "❌ **Appeal Rejected:** Moderation team declined the appeal request.",
    }
}


def t(key: str, lang: str = "ar", **kwargs: Any) -> str:
    """Translates a message key for the given language ('ar' or 'en')."""
    locale = lang.lower() if lang in MESSAGES else "ar"
    msg_template = MESSAGES.get(locale, {}).get(key) or MESSAGES["ar"].get(key) or key
    try:
        return msg_template.format(**kwargs)
    except Exception:
        return msg_template

