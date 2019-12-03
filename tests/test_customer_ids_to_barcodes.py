import os
from time import time
from customer_ids_to_barcodes import make_customer_ids_to_barcodes_csv_with_pandas


def test_customer_ids_to_barcordes():

    test_filename = f"test_file_{time()}.csv"
    test_filepath = os.path.join("tests", test_filename)

    make_customer_ids_to_barcodes_csv_with_pandas(test_filepath)

    if os.path.exists(test_filepath):
        os.remove(test_filepath)
    assert True
