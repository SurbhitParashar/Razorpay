from pathlib import Path

from recoverai.data.generator import GenerationConfig, generate_dataset, save_dataset


def main() -> None:
    config = GenerationConfig()

    dataframe = generate_dataset(config)

    output_path = Path("data/raw/payments.csv")

    save_dataset(dataframe, output_path)

    print(f"Generated {len(dataframe):,} payment events")
    print(f"Recovered events: {dataframe['recovered'].mean():.2%}")
    print(f"Recovered revenue: ₹{dataframe['recovered_amount_inr'].sum():,.2f}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
