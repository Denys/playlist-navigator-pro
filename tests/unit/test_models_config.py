import importlib
import warnings

import execution.models as models


def test_execution_models_import_has_no_class_config_deprecation_warning():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.reload(models)

    assert not any(
        "Support for class-based `config` is deprecated" in str(item.message)
        for item in caught
    )


def test_video_data_instantiation_has_no_datetime_utcnow_deprecation_warning():
    payload = {
        "video_id": "v1",
        "title": "Test Video",
        "url": "https://youtu.be/v1",
        "channel": "Test Channel",
        "metadata": {
            "thematic": {"primary": "unknown", "secondary": [], "confidence": 0.0},
            "genre": {"primary": "Unknown", "all": []},
            "author_type": "Unknown",
            "length_category": "unknown",
            "content_type": "video",
            "difficulty_level": "intermediate",
        },
        "tags": {
            "youtube_tags": [],
            "auto_generated": [],
            "user_defined": [],
            "combined": [],
        },
        "sync_status": {"exists_at_source": True},
    }

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        models.VideoData(**payload)

    assert not any(
        "datetime.datetime.utcnow() is deprecated" in str(item.message)
        for item in caught
    )
