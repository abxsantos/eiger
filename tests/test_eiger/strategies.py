from hypothesis.strategies import characters, integers, none, one_of

positive_small_integer_nullable_strategy = one_of(
    none(), integers(min_value=0, max_value=32767)
)

postgres_allowed_characters = characters(
    blacklist_characters=('\x00',),
    blacklist_categories=(
        'Cn',
        'Cs',
    ),
)
