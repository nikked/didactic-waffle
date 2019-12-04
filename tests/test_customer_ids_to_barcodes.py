import os
import json
from time import time
import pandas as pd

from customer_ids_to_barcodes import (
    create_customer_to_tickets_csv,
    _remove_duplicate_barcodes,
    _make_customers_to_barcodes_series,
    _validate_orders,
)


class TestCreateCustomerToTicketsCsv:  # pylint: disable=too-few-public-methods
    def test_create_customer_to_tickets_csv(self) -> None:

        test_filename = f"test_file_{time()}.csv"
        test_filepath = os.path.join("tests", test_filename)

        create_customer_to_tickets_csv(test_filepath)
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


class TestValidateBarcodes:
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


class TestValidateOrders:  # pylint: disable=too-few-public-methods
    def test_validate_orders_removes_rows_without_barcodes(self) -> None:
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

        output_df = _validate_orders(mock_combined_df)
        assert len(output_df) == 4
        assert output_df.iloc[1].values[0] == 11_111_111_318
        assert output_df.iloc[2].values[0] == 11_111_111_429


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
