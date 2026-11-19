from app.compression.context_compressor import compress_context


def test_compression_limit_and_filter():
    docs = [{"id": "1", "text": "a" * 100}, {"id": "2", "text": "b" * 100}]
    result = compress_context(docs, max_chars=150)
    assert len(result) == 2
    assert len(result[0]["text"]) == 100
    assert len(result[1]["text"]) == 50
