from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

from retailpulse.data_generation.config import (
    CUSTOMER_COUNT,
    CUSTOMERS_SOURCE_DIR,
    RANDOM_SEED,
)


def generate_customers(
    count: int = CUSTOMER_COUNT,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """
    Generate a clean synthetic customer dataset.

    Grain:
        One row represents one customer.
    """

    fake = Faker("en_IN")
    Faker.seed(seed)
    np.random.seed(seed)

    customers = []

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2026, 8, 31)

    for index in range(1, count + 1):
        customer_id = f"C{index:06d}"

        signup_date = fake.date_between(
            start_date=start_date,
            end_date=end_date,
        )

        created_at = datetime.combine(
            signup_date,
            datetime.min.time(),
        ) + timedelta(
            seconds=int(np.random.randint(0, 86400))
        )

        customers.append(
            {
                "customer_id": customer_id,
                "customer_name": fake.name(),
                "email": fake.email(),
                "phone": fake.msisdn(),
                "city": fake.city(),
                "state": fake.state(),
                "country": "India",
                "signup_date": signup_date,
                "customer_status": np.random.choice(
                    ["ACTIVE", "INACTIVE"],
                    p=[0.85, 0.15],
                ),
                "created_at": created_at,
                "updated_at": created_at,
            }
        )

    return pd.DataFrame(customers)


def save_customers(df: pd.DataFrame) -> None:
    """Save the customer dataset to the source directory."""

    CUSTOMERS_SOURCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = CUSTOMERS_SOURCE_DIR / "customers.csv"

    df.to_csv(
        output_path,
        index=False,
    )

    print(f"Generated {len(df):,} customers")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    customers_df = generate_customers()
    save_customers(customers_df)