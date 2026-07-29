"""Configuration defaults and validation for course generation counts."""

from dataclasses import dataclass

from app.schemas import AppConfigSchema


DEFAULT_COURSE_GENERATION_CONFIG = AppConfigSchema()


@dataclass(frozen=True)
class CourseGenerationCountRange:
    field_name: str
    min_value: int
    default_value: int
    max_value: int


_COUNT_CONFIG_FIELDS = {
    "qa_count": (
        "course_generator_qa_count_min",
        "course_generator_qa_count_default",
        "course_generator_qa_count_max",
    ),
    "quiz_question_count": (
        "course_generator_quiz_question_count_min",
        "course_generator_quiz_question_count_default",
        "course_generator_quiz_question_count_max",
    ),
    "quiz_option_count": (
        "course_generator_quiz_option_count_min",
        "course_generator_quiz_option_count_default",
        "course_generator_quiz_option_count_max",
    ),
    "misconception_count": (
        "course_generator_misconception_count_min",
        "course_generator_misconception_count_default",
        "course_generator_misconception_count_max",
    ),
}


def _app_config(config: AppConfigSchema | None = None) -> AppConfigSchema:
    return config or DEFAULT_COURSE_GENERATION_CONFIG


def get_course_generation_count_range(
    field_name: str,
    config: AppConfigSchema | None = None,
) -> CourseGenerationCountRange:
    if field_name not in _COUNT_CONFIG_FIELDS:
        raise KeyError(f"Unknown course generation count field: {field_name}")

    app_config = _app_config(config)
    min_key, default_key, max_key = _COUNT_CONFIG_FIELDS[field_name]
    min_value = int(getattr(app_config, min_key))
    max_value = max(min_value, int(getattr(app_config, max_key)))
    default_value = min(
        max(int(getattr(app_config, default_key)), min_value),
        max_value,
    )

    return CourseGenerationCountRange(
        field_name=field_name,
        min_value=min_value,
        default_value=default_value,
        max_value=max_value,
    )


def get_course_generation_count_defaults(
    config: AppConfigSchema | None = None,
) -> dict[str, int]:
    return {
        field_name: get_course_generation_count_range(
            field_name,
            config=config,
        ).default_value
        for field_name in _COUNT_CONFIG_FIELDS
    }


def validate_course_generation_count(
    field_name: str,
    value: int,
    config: AppConfigSchema | None = None,
) -> int:
    count_range = get_course_generation_count_range(field_name, config=config)
    count = int(value)
    if count < count_range.min_value or count > count_range.max_value:
        raise ValueError(
            f"{field_name} must be between "
            f"{count_range.min_value} and {count_range.max_value}"
        )
    return count


def validate_course_generation_counts(
    *,
    qa_count: int,
    quiz_question_count: int,
    quiz_option_count: int,
    misconception_count: int,
    config: AppConfigSchema | None = None,
) -> dict[str, int]:
    """Validate counts supplied by name to avoid swapping similar integer values."""

    return {
        "qa_count": validate_course_generation_count(
            "qa_count",
            qa_count,
            config=config,
        ),
        "quiz_question_count": validate_course_generation_count(
            "quiz_question_count",
            quiz_question_count,
            config=config,
        ),
        "quiz_option_count": validate_course_generation_count(
            "quiz_option_count",
            quiz_option_count,
            config=config,
        ),
        "misconception_count": validate_course_generation_count(
            "misconception_count",
            misconception_count,
            config=config,
        ),
    }
