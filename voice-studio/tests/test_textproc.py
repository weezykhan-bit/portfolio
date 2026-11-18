from app.textproc import chunk_text, chunk_with_pauses


def test_short_text_is_one_chunk():
    assert chunk_text("Hello there. How are you?") == ["Hello there. How are you?"]


def test_respects_max_chars():
    text = " ".join(["This is a fairly ordinary sentence."] * 40)
    chunks = chunk_text(text, max_chars=120)
    assert len(chunks) > 5
    assert all(len(c) <= 120 for c in chunks)
    assert " ".join(chunks) == text


def test_long_sentence_without_punctuation_is_split():
    text = "word " * 300
    assert all(len(c) <= 100 for c in chunk_text(text, max_chars=100))


def test_paragraphs_get_longer_pause():
    pairs = chunk_with_pauses("First para.\n\nSecond para. Still second.", max_chars=12)
    assert pairs[0][1] > pairs[1][1] or pairs[0][1] == 0.55
    assert pairs[-1][0].endswith("second.")


def test_hindi_danda_splits():
    chunks = chunk_text("यह पहला वाक्य है। यह दूसरा वाक्य है।", max_chars=20)
    assert len(chunks) == 2
