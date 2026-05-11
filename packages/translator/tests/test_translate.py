def test_translate():
    """Test the TranslateEnToMirad class."""
    from mirad_translator.translate import TranslateEnToMirad
    
    translator = TranslateEnToMirad()
    result = translator.translate("Hello")
    assert result == "Translated text"
