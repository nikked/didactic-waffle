import os
import logging
from typing import Sequence

import pandas as pd  # type: ignore
from pandas import DataFrame, Series

DATA_DIRECTORY = "./assignment_data"


def create_customer_to_tickets_csv(
    output_filepath: str = "./customer_ids_to_barcodes.csv",
) -> None:
    """
    This function combines barcodes.csv and orders.csv into a new csv file that maps
    customer_ids to barcodes. As a result, we can see how many individual tickets
    a customer has across order_id's.

    Args:
        output_filepath (str): The filepath where the result csv file is stored
    """
    barcodes_df = _get_csv_as_dataframe(
        filepath=os.path.join(DATA_DIRECTORY, "barcodes.csv"), index="order_id"
    )
    validated_barcodes_df = _remove_duplicate_barcodes(barcodes_df)

    orders_df = _get_csv_as_dataframe(
        filepath=os.path.join(DATA_DIRECTORY, "orders.csv"),
        index="order_id",
        drop_index_col=False,
    )

    output_df = _make_output_dataframe(validated_barcodes_df, orders_df)
    _write_output_df_as_csv(output_df, output_filepath)


def _get_csv_as_dataframe(
    filepath: str, index: str, drop_index_col: bool = True
) -> DataFrame:
    df = pd.read_csv(filepath)
    return df.set_index(index, drop=drop_index_col)


def _remove_duplicate_barcodes(barcodes_df: DataFrame) -> DataFrame:

    if any(barcodes_df.duplicated(subset=["barcode"])):
        logging.error("Found duplicated barcodes:")

        for index, duplicate in enumerate(barcodes_df.duplicated(subset=["barcode"])):
            if duplicate:
                logging.error("Barcode: %i", int(barcodes_df.iloc[index]["barcode"]))

    # Sorting the DataFrame ensures that the rows
    # with customer_id's are prioritized
    sorted_barcodes_df = barcodes_df.sort_values("order_id", ascending=True)
    validated_df = sorted_barcodes_df.drop_duplicates(keep="first", subset=["barcode"])
    return validated_df.reset_index(drop=True)


def _make_output_dataframe(
    validated_barcodes_df: DataFrame, orders_df: DataFrame
) -> DataFrame:
    def _barcode_series_to_int_list(barcode_series: Series) -> Sequence[int]:
        return [int(barcode) for barcode in barcode_series]

    combined_df = orders_df.join(validated_barcodes_df)
    combined_df.set_index(["customer_id", "order_id"], inplace=True)

    validated_df = _validate_orders(combined_df)

    return validated_df.groupby(["customer_id", "order_id"])["barcode"].apply(
        _barcode_series_to_int_list
    )


def _validate_orders(combined_df: DataFrame) -> DataFrame:

    orders_without_barcodes = combined_df[combined_df.isnull().any(axis=1)]

    if not orders_without_barcodes.empty:
        logging.error("Found orders without barcodes:")
        for customer_id, order_id in orders_without_barcodes.index:
            logging.error("Customer id: %s, Order id: %s", customer_id, order_id)

    return combined_df.dropna()


def _write_output_df_as_csv(output_df: DataFrame, output_filepath: str) -> None:
    output_df.to_csv(output_filepath, header=["barcodes"])


if __name__ == "__main__":
    create_customer_to_tickets_csv(output_filepath="./customer_ids_to_barcodes.csv")
