import os
import json
from time import time
import numpy as np
import pandas as pd
from pandas import DataFrame

from customer_ids_to_barcodes import (
    create_customer_to_tickets_csv,
    _remove_duplicate_barcodes,
    _make_customers_to_barcodes_series,
    _remove_orders_without_barcodes,
    _log_the_amount_of_unused_barcodes,
    _log_customers_that_bought_most_tickets,
)


class TestCreateCustomerToTicketsCsv:  # pylint: disable=too-few-public-methods
    def test_create_customer_to_tickets_csv(self) -> None:

        test_filename = f"test_file_{time()}.csv"
        test_filepath = os.path.join("tests", test_filename)

        create_customer_to_tickets_csv(
            output_filepath=test_filepath,
            keep_barcodes_with_order_ids=True,
            no_of_top_customers=5,
        )
        output_df = pd.read_csv(test_filepath)
        output_df.set_index("order_id", inplace=True)

        assert len(output_df) == 204
        assert output_df.loc[193][0] == 4
        assert set(json.loads(output_df.loc[193][1])) == {
            11_111_111_297,
            11_111_111_380,
            11_111_111_614,
        }

        if os.path.exists(test_filepath):
            os.remove(test_filepath)
            assert True

        else:
            assert False


class TestRemoveDuplicateBarcodes:
    def test_duplicates_removed(self) -> None:
        mock_bardcodes = pd.DataFrame(
            [
                [11_111_111_111, 10],
                [11_111_111_111, 11],
                [11_111_111_116, 14],
                [11_111_111_116, 15],
            ],
            columns=["barcode", "order_id"],
        )

        mock_bardcodes.set_index("order_id", drop=True, inplace=True)

        output_df = _remove_duplicate_barcodes(mock_bardcodes)

        assert len(output_df) == 2
        assert output_df.index[0] == 10
        assert output_df.index[1] == 14
        assert output_df.iloc[0].values[0] == 11_111_111_111
        assert output_df.iloc[1].values[0] == 11_111_111_116

    def test_empty_duplicate_removed(self) -> None:
        mock_bardcodes_1 = pd.DataFrame(
            [[11_111_111_111, 10], [11_111_111_111]], columns=["barcode", "order_id"]
        ).set_index("order_id")
        mock_bardcodes_2 = pd.DataFrame(
            [[11_111_111_111], [11_111_111_111, 10]], columns=["barcode", "order_id"]
        ).set_index("order_id")

        output_df_1 = _remove_duplicate_barcodes(mock_bardcodes_1)
        output_df_2 = _remove_duplicate_barcodes(mock_bardcodes_2)

        assert output_df_1.equals(output_df_2)


class TestLogTheAmountOfUnusedBarcodes:
    def test_barcodes_without_order_ids_returned(self) -> None:
        mock_bardcodes = pd.DataFrame(
            [
                [11_111_111_111, 10],
                [11_111_111_111, 11],
                [11_111_111_116, 14],
                [11_111_111_116,],
            ],
            columns=["barcode", "order_id"],
        )
        mock_bardcodes.set_index("order_id", drop=True, inplace=True)

        response = _log_the_amount_of_unused_barcodes(mock_bardcodes)

        assert isinstance(response, DataFrame)
        assert len(response) == 1
        assert response.iloc[0][np.nan] == 11_111_111_116

    def test_type_error_raised_if_fully_int_index(self) -> None:
        mock_bardcodes = pd.DataFrame(
            [
                [11_111_111_111, 10],
                [11_111_111_111, 11],
                [11_111_111_116, 14],
                [11_111_111_116, 15],
            ],
            columns=["barcode", "order_id"],
        )

        mock_bardcodes.set_index("order_id", drop=True, inplace=True)

        response = _log_the_amount_of_unused_barcodes(mock_bardcodes)

        assert isinstance(response, TypeError)

    def test_key_error_raised_if_no_nans(self) -> None:
        mock_bardcodes = pd.DataFrame(
            [
                [11_111_111_111, 10],
                [11_111_111_111, 11],
                [11_111_111_116, 14],
                [11_111_111_116, 15.0],
            ],
            columns=["barcode", "order_id"],
        )

        mock_bardcodes.set_index("order_id", drop=True, inplace=True)

        response = _log_the_amount_of_unused_barcodes(mock_bardcodes)

        assert isinstance(response, KeyError)


class TestRemoveOrdersWithoutBarcodes:
    def test_remove_orders_without_barcodes_removes_rows_without_barcodes(self) -> None:
        mock_combined_df = pd.DataFrame(
            [
                [10, 1, 11_111_111_428],
                [11, 2, 11_111_111_318],
                [12, 3],
                [13, 4, 11_111_111_429],
                [14, 5, 11_111_111_319],
            ],
            columns=["customer_id", "order_id", "barcode"],
        )

        mock_combined_df.set_index(["customer_id", "order_id"], inplace=True)

        output_df = _remove_orders_without_barcodes(mock_combined_df)
        assert len(output_df) == 4
        assert output_df.iloc[1].values[0] == 11_111_111_318
        assert output_df.iloc[2].values[0] == 11_111_111_429

    def test_nothing_removed_if_all_orders_have_barcodes(self) -> None:
        mock_combined_df = pd.DataFrame(
            [
                [10, 1, 11_111_111_428],
                [11, 2, 11_111_111_318],
                [13, 4, 11_111_111_429],
                [14, 5, 11_111_111_319],
            ],
            columns=["customer_id", "order_id", "barcode"],
        )

        mock_combined_df.set_index(["customer_id", "order_id"], inplace=True)

        output_df = _remove_orders_without_barcodes(mock_combined_df)

        assert output_df.equals(mock_combined_df)


class TestMakeCustomersToBarcodesSeries:  # pylint: disable=too-few-public-methods
    def test_make_customers_to_barcodes_series(self) -> None:
        mock_bardcodes = pd.DataFrame(
            [
                [11_111_111_111, 10],
                [11_111_111_112, 10],
                [11_111_111_113, 10],
                [11_111_111_114, 10],
                [11_111_111_116, 14],
                [11_111_111_117, 15],
            ],
            columns=["barcode", "order_id"],
        )

        mock_bardcodes.set_index("order_id", inplace=True)

        mock_orders = pd.DataFrame(
            [[10, 1], [11, 1], [14, 1], [15, 3]], columns=["order_id", "customer_id"]
        )

        mock_orders.set_index("order_id", drop=False, inplace=True)

        output_df = _make_customers_to_barcodes_series(mock_bardcodes, mock_orders)
        assert len(output_df) == 3
        assert output_df.loc[1, 10] == [
            11_111_111_111,
            11_111_111_112,
            11_111_111_113,
            11_111_111_114,
        ]
        assert output_df.loc[3, 15] == [11_111_111_117]


class TestLogCustomersThatBoughtMostTickets:  # pylint: disable=too-few-public-methods
    def test_log_customers_that_bought_most_tickets(self) -> None:

        mock_index = pd.MultiIndex.from_tuples(
            [(4, 193), (4, 203), (5, 194), (6, 195), (5, 204),],
            names=["customer_id", "order_id"],
        )

        mock_series = pd.Series(
            [
                [11_111_111_380, 11_111_111_297, 11_111_111_614, 11_111_111_623],
                [11_111_111_624, 11_111_111_307, 11_111_111_390],
                [11_111_111_381, 11_111_111_298],
                [11_111_111_308, 11_111_111_625, 11_111_111_391],
                [11_111_111_382, 11_111_111_299, 11_111_111_616],
            ],
            index=mock_index,
            name="barcode",
        )

        customer_to_barcodes_df = _log_customers_that_bought_most_tickets(mock_series)

        assert isinstance(customer_to_barcodes_df, DataFrame)
        assert customer_to_barcodes_df.loc[4][0] == 7
        assert customer_to_barcodes_df.loc[5][0] == 5
        assert customer_to_barcodes_df.loc[6][0] == 3
