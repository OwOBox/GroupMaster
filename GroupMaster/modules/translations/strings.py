from GroupMaster.modules.sql.translation import prev_locale
from GroupMaster.modules.translations.English import EnglishStrings
from GroupMaster.modules.translations.Vietnamese import VietnameseStrings


def tld(chat_id, t, show_none=True):
    LANGUAGE = prev_locale(chat_id)
    print(chat_id, t)
    if LANGUAGE:
        LOCALE = LANGUAGE.locale_name
        if LOCALE in ('vi') and t in VietnameseStrings:
           return VietnameseStrings[t]
#        elif LOCALE in ('ua') and t in UkrainianStrings:
#            return UkrainianStrings[t]
#        elif LOCALE in ('es') and t in SpanishStrings:
#            return SpanishStrings[t]
#        elif LOCALE in ('tr') and t in TurkishStrings:
 #           return TurkishStrings[t]
#        elif LOCALE in ('id') and t in IndonesianStrings:
#            return IndonesianStrings[t]
        else:
            if t in EnglishStrings:
                return EnglishStrings[t]
            else:
                return t
    elif show_none:
        if t in EnglishStrings:
            return EnglishStrings[t]
        else:
            return t



def tld_help(chat_id, t):
    LANGUAGE = prev_locale(chat_id)
    print("tld_help ", chat_id, t)
    if LANGUAGE:
        LOCALE = LANGUAGE.locale_name

        t = t + "_help"

        print("Test2", t)

        if LOCALE in ('vi') and t in VietnameseStrings:
            return VietnameseStrings[t]
  #      elif LOCALE in ('ua') and t in UkrainianStrings:
  #          return UkrainianStrings[t]
  #      elif LOCALE in ('es') and t in SpanishStrings:
  #          return SpanishStrings[t]
  #      elif LOCALE in ('tr') and t in TurkishStrings:
  #          return TurkishStrings[t]
  #      elif LOCALE in ('id') and t in IndonesianStrings:
  #          return IndonesianStrings[t]
        else:
            return False
    else:
        return False
