languages = {
  'en': ['English'],
  'uk': ['Ukrainian', 'Українська'],
  'ru': ['Russian', 'Русский'],
  'pl': ['Polish', 'Polski'],
  'de': ['German', 'Deutsch'],
  'nl': ['Nederlands', 'Dutch'],
  'sv': ['Swedish', 'Svenska'],
  'es': ['Spanish', 'Español'],
  'fr': ['French', 'Français'],
  'it': ['Italian', 'Italiano'],
  'ja': ['Japanese'],
  'zh': ['Chainese'],
  'ceb': ['Cebuano', 'Bisaya'],
}

linguist = lambda lang: lang if (lang := lang.lower()) in languages else list(
    languages.keys())[list(languages.values()).index(value[0])] if (value := [
    value for value in languages.values() if lang.title() in value]) else 'en'