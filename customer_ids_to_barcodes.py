import os
import logging
from typing import Sequence

import pandas as pd  # type: ignore
from pandas import DataFrame, Series

DATA_DIRECTORY = "./assignment_data"


def make_customer_ids_to_barcodes_csv_with_pandas():

    barcodes_df = _get_csv_as_dataframe(os.path.join(DATA_DIRECTORY, "barcodes.csv"))
    barcodes_df = _validate_barcodes(barcodes_df)
    barcodes_df = barcodes_df.set_index("order_id")

    orders_df = _get_csv_as_dataframe(os.path.join(DATA_DIRECTORY, "orders.csv"))
    orders_df = orders_df.set_index("order_id", drop=False)

    output_df = orders_df.join(barcodes_df)
    output_df = output_df.set_index(["customer_id", "order_id"])
    output_df = _validate_orders(output_df)
    output_df = output_df.groupby(["customer_id", "order_id"])["barcode"].apply(
        _series_to_int_list
    )
    output_df.to_csv("./customer_ids_to_barcodes.csv", header=["barcodes"])


def _get_csv_as_dataframe(filepath: str) -> DataFrame:
    return pd.read_csv(filepath)


def _validate_barcodes(barcodes_df: DataFrame) -> DataFrame:
    duplicate_in_barcodes = barcodes_df.duplicated(subset=["barcode"])

    if any(duplicate_in_barcodes):
        logging.error("Found duplicate barcodes")
        for index, duplicate in enumerate(duplicate_in_barcodes):
            if duplicate:
                logging.error("Barcode: %i", int(barcodes_df.loc[index]["barcode"]))

    return barcodes_df.drop_duplicates(subset=["barcode"])


def _validate_orders(output_df: DataFrame) -> DataFrame:
    orders_without_barcodes = output_df[output_df.isnull().any(axis=1)]

    if not orders_without_barcodes.empty:
        logging.error("Found orders without barcodes:")
        for customer_id, order_id in orders_without_barcodes.index:
            logging.error("Customer id: %s, Order id: %s", customer_id, order_id)

    return output_df.dropna()


def _series_to_int_list(barcode_series: Series) -> Sequence[int]:
    return [int(barcode) for barcode in barcode_series]


if __name__ == "__main__":
    make_customer_ids_to_barcodes_csv_with_pandas()
