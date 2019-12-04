import os
import json
from time import time
import pandas as pd  # type: ignore

from customer_ids_to_barcodes import (
    create_customer_to_tickets_csv,
    _remove_duplicate_barcodes,
    _make_output_dataframe,
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
            11111111297,
            11111111380,
            11111111614,
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
                [11111111111, 10],
                [11111111111, 11],
                [11111111116, 14],
                [11111111116, 15],
            ],
            columns=["barcode", "order_id"],
        )

        mock_bardcodes.set_index("order_id", drop=True)

        output_df = _remove_duplicate_barcodes(mock_bardcodes)

        assert len(output_df) == 2
        assert output_df.iloc[1].values[0] == 11111111116
        assert output_df.iloc[1].values[1] == 14

    def test_empty_duplicate_removed(self) -> None:
        mock_bardcodes_1 = pd.DataFrame(
            [[11111111111, 10], [11111111111,],], columns=["barcode", "order_id"],
        ).set_index("order_id")
        mock_bardcodes_2 = pd.DataFrame(
            [[11111111111,], [11111111111, 10],], columns=["barcode", "order_id"],
        ).set_index("order_id")

        output_df_1 = _remove_duplicate_barcodes(mock_bardcodes_1)
        output_df_2 = _remove_duplicate_barcodes(mock_bardcodes_2)

        assert output_df_1.equals(output_df_2)


class TestValidateOrders:  # pylint: disable=too-few-public-methods
    def test_validate_orders_removes_rows_without_barcodes(self) -> None:
        mock_combined_df = pd.DataFrame(
            [
                [10, 1, 11111111428],
                [11, 2, 11111111318],
                [12, 3,],
                [13, 4, 11111111429],
                [14, 5, 11111111319],
            ],
            columns=["customer_id", "order_id", "barcode"],
        )

        mock_combined_df.set_index(["customer_id", "order_id"], inplace=True)

        output_df = _validate_orders(mock_combined_df)
        assert len(output_df) == 4
        assert output_df.iloc[1].values[0] == 11111111318
        assert output_df.iloc[2].values[0] == 11111111429


class TestMakeOutputDataframe:  # pylint: disable=too-few-public-methods
    def test_make_output_dataframe(self) -> None:
        mock_bardcodes = pd.DataFrame(
            [
                [11111111111, 10],
                [11111111112, 10],
                [11111111113, 10],
                [11111111114, 10],
                [11111111116, 14],
                [11111111117, 15],
            ],
            columns=["barcode", "order_id"],
        )

        mock_bardcodes.set_index("order_id", inplace=True)

        mock_orders = pd.DataFrame(
            [[10, 1], [11, 1], [14, 1], [15, 3],], columns=["order_id", "customer_id"],
        )

        mock_orders.set_index("order_id", drop=False, inplace=True)

        output_df = _make_output_dataframe(mock_bardcodes, mock_orders)
        assert len(output_df) == 3
        assert output_df.loc[1, 10] == [
            11111111111,
            11111111112,
            11111111113,
            11111111114,
        ]
        assert output_df.loc[3, 15] == [11111111117]
