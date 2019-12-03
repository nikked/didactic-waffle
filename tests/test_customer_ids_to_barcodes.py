import os
from time import time
import pandas as pd  # type: ignore

from customer_ids_to_barcodes import (
    create_customer_to_tickets_csv,
    _remove_duplicate_barcodes,
    # _make_output_dataframe,
    _validate_orders,
)


class TestCreateCustomerToTicketsCsv:  # pylint: disable=too-few-public-methods
    def test_create_customer_to_tickets_csv(self) -> None:

        test_filename = f"test_file_{time()}.csv"
        test_filepath = os.path.join("tests", test_filename)

        create_customer_to_tickets_csv(test_filepath)

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

        output_df = _remove_duplicate_barcodes(mock_bardcodes)

        assert output_df.equals(
            pd.DataFrame(
                [[11111111111, 10], [11111111116, 14],],
                columns=["barcode", "order_id"],
            )
        )

    def test_empty_duplicate_removed(self) -> None:
        mock_bardcodes_1 = pd.DataFrame(
            [[11111111111, 10], [11111111111,],], columns=["barcode", "order_id"],
        )
        mock_bardcodes_2 = pd.DataFrame(
            [[11111111111,], [11111111111, 10],], columns=["barcode", "order_id"],
        )

        output_df_1 = _remove_duplicate_barcodes(mock_bardcodes_1)
        output_df_2 = _remove_duplicate_barcodes(mock_bardcodes_2)

        assert output_df_1.equals(output_df_2)
        assert len(output_df_1) == 1
        assert output_df_1.iloc[0].values[0] == 11111111111
        assert output_df_1.iloc[0].values[1] == 10


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
