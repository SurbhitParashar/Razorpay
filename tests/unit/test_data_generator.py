from recoverai.data.generator import GenerationConfig, generate_dataset


def test_generation_is_deterministic() -> None:
    config = GenerationConfig(seed=42, n_events=100)

    first = generate_dataset(config)
    second = generate_dataset(config)

    assert first.equals(second)


def test_generation_has_expected_size() -> None:
    dataframe = generate_dataset(
        GenerationConfig(
            seed=42,
            n_events=250,
        )
    )

    assert len(dataframe) == 250
    assert dataframe["payment_id"].is_unique


def test_recovered_amount_never_exceeds_payment() -> None:
    dataframe = generate_dataset(
        GenerationConfig(
            seed=42,
            n_events=500,
        )
    )

    assert (dataframe["recovered_amount_inr"] <= dataframe["amount_inr"]).all()
