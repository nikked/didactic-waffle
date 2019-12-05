import os
import logging
from typing import Union

import numpy as np
import pandas as pd
from pandas import DataFrame, Series

DATA_DIRECTORY = "./assignment_data"


def create_customer_to_tickets_csv(
    output_filepath: str = "./customer_ids_to_barcodes.csv",
) -> None:
    """
    This function combines barcodes.csv and orders.csv into a new csv file that maps
    customer_ids to barcodes. As a result, we can see how many individual tickets
    a customer has across order_id's:

    customer_id,order_id,barcodes
    4,193,"[11111111380, 11111111297, 11111111614]"
    4,203,"[11111111624, 11111111307, 11111111390]"

    Args:
        output_filepath (str): The filepath where the output csv file is stored
    """
    barcodes_df = _get_csv_as_dataframe(
        filepath=os.path.join(DATA_DIRECTORY, "barcodes.csv"), index="order_id"
    )
    validated_barcodes_df = _remove_duplicate_barcodes(barcodes_df)

    _log_the_amount_of_unused_barcodes(validated_barcodes_df)

    orders_df = _get_csv_as_dataframe(
        filepath=os.path.join(DATA_DIRECTORY, "orders.csv"),
        index="order_id",
        drop_index_col=False,
    )

    customers_to_barcodes_series = _make_customers_to_barcodes_series(
        validated_barcodes_df, orders_df
    )

    _log_customers_that_bought_most_tickets(
        customers_to_barcodes_series, no_of_customers=5
    )

    _write_output_as_csv(customers_to_barcodes_series, output_filepath)


def _get_csv_as_dataframe(
    filepath: str, index: str, drop_index_col: bool = True
) -> DataFrame:
    df = pd.read_csv(filepath)
    return df.set_index(index, drop=drop_index_col)


def _remove_duplicate_barcodes(barcodes_df: DataFrame) -> DataFrame:

    duplicate_barcodes_series = barcodes_df.duplicated(subset=["barcode"])

    if any(duplicate_barcodes_series):
        logging.error(
            "Found %i duplicated barcodes. The barcodes without an associated order_id will be prioritized for deletion",
            len([barcode for barcode in duplicate_barcodes_series if barcode]),
        )

        for index, duplicate in enumerate(duplicate_barcodes_series):
            if duplicate:
                logging.error(
                    "Duplicate barcode: %i", int(barcodes_df.iloc[index]["barcode"])
                )

    # Sorting the DataFrame ensures that the rows without order_id's will be last.
    # Since we are keeping the first instance of a duplicate barcode, the kept barcode
    # is guaranteed to be the one with an order_id (if such an barcode exists)
    sorted_barcodes_df = barcodes_df.sort_values("order_id", ascending=True)
    validated_barcodes_df = sorted_barcodes_df.drop_duplicates(
        keep="first", subset=["barcode"]
    )

    return validated_barcodes_df


def _log_the_amount_of_unused_barcodes(
    validated_barcodes_df: DataFrame,
) -> Union[Series, Exception]:
    try:
        nan_indexes = validated_barcodes_df.loc[np.nan]
        logging.info("Amount of unused barcodes: %i", len(nan_indexes))
        return nan_indexes

    except (KeyError, TypeError) as exception:
        return exception


def _make_customers_to_barcodes_series(
    validated_barcodes_df: DataFrame, orders_df: DataFrame
) -> Series:
    combined_df = orders_df.join(validated_barcodes_df)
    combined_df.set_index(["customer_id", "order_id"], inplace=True)

    validated_df = _remove_orders_without_barcodes(combined_df)

    return validated_df.groupby(["customer_id", "order_id"])["barcode"].apply(
        lambda barcode_series: [int(barcode) for barcode in barcode_series]
    )


def _remove_orders_without_barcodes(combined_df: DataFrame) -> DataFrame:

    orders_without_barcodes = combined_df[combined_df.isnull().any(axis=1)]

    if not orders_without_barcodes.empty:
        logging.error("Found %i orders without barcodes:", len(orders_without_barcodes))
        for customer_id, order_id in orders_without_barcodes.index:
            logging.error("Customer id: %s, Order id: %s", customer_id, order_id)

    return combined_df.dropna()


def _log_customers_that_bought_most_tickets(
    customers_to_barcodes_series: Series, no_of_customers: int = 5
) -> DataFrame:

    customer_to_barcodes_df = pd.DataFrame(customers_to_barcodes_series)

    customer_to_barcodes_df["no_of_tickets"] = customer_to_barcodes_df["barcode"].apply(
        len
    )
    customer_to_barcodes_df = customer_to_barcodes_df.groupby(["customer_id"]).sum()
    customer_to_barcodes_df.sort_values(
        by="no_of_tickets", inplace=True, ascending=False
    )

    logging.info("Customers with most tickets bought:")
    for customer_id in customer_to_barcodes_df.index[:no_of_customers]:
        logging.info(
            "Customer id: %s, Amount of tickets: %s",
            customer_id,
            customer_to_barcodes_df.loc[customer_id][0],
        )

    return customer_to_barcodes_df


def _write_output_as_csv(output_series: DataFrame, output_filepath: str) -> None:
    logging.info("Writing output to filepath: %s", output_filepath)
    output_series.to_csv(output_filepath, header=["barcodes"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_customer_to_tickets_csv(output_filepath="./customer_ids_to_barcodes.csv")
