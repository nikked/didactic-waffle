

# Tiqets programming assignment (Backend developer)

This repository contains my solution for the Tiqets programming assignment. The assignment is related to the `Backend developer` job opening.

## Installation
This project is developed with Python 3.7, but it most likely also works with older Python 3 versions. Please install dependencies with `pip install -r requirements.txt`.

## Usage
This project exposes a single CLI: `customer_ids_to_barcodes.py`. Running it:
```
python customer_ids_to_barcodes.py
```
creates a output `.csv` file on the root of the repository:
```
customer_ids_to_barcodes.csv
```
The process prints the following lines using the [Python standard logging API:](https://docs.python.org/3/library/logging.html)

```
ERROR:root:Found 5 duplicated barcodes:
ERROR:root:Duplicate barcode: 11111111649
ERROR:root:Duplicate barcode: 11111111665
ERROR:root:Duplicate barcode: 11111111674
ERROR:root:Duplicate barcode: 11111111595
ERROR:root:Duplicate barcode: 11111111700
INFO:root:Amount of unused barcodes: 98
ERROR:root:Found 3 orders without barcodes:
ERROR:root:Customer id: 72, Order id: 75
ERROR:root:Customer id: 20, Order id: 108
ERROR:root:Customer id: 12, Order id: 201
INFO:root:Top 5 customers with most tickets bought:
INFO:root:Customer id: 10, Amount of tickets: 23
INFO:root:Customer id: 56, Amount of tickets: 20
INFO:root:Customer id: 60, Amount of tickets: 17
INFO:root:Customer id: 29, Amount of tickets: 16
INFO:root:Customer id: 59, Amount of tickets: 15
INFO:root:Writing output to filepath: ./customer_ids_to_barcodes.csv
```


### Optional arguments
Please run `python customer_ids_to_barcodes.py -h` to see a full list of accepted arguments.

#### --pb, --prioritize_barcodes_without_order_ids
> Default: False

There are some duplicates in the provided `barcodes.csv`. The process removes these duplicates. Nevertheless, we need to consider should we prioritize removing barcodes with an order_id or the ones without an order_id.

By default, the process removes duplicate barcodes without an order_id. The process assumes that a duplicate barcode has already been sold, and the empty duplicate is erroneous. This assumption will prevent erroneously associating a single barcode to multiple order_ids.

This behavior can be overridden with the following argument:
```
python customer_ids_to_barcodes.py --prioritize_barcodes_without_order_ids
```

It creates a slightly different output (only changed lines printed):
```
INFO:root:Amount of unused barcodes: 103
INFO:root:Customer id: 60, Amount of tickets: 16
```
The amount of unused barcodes increases by five units (`98->103`). It makes sense. There are in total five duplicate barcodes. Each one of the duplicates has one associated with an `order_id` and another one without an `order_id`. One top customer,  `customer_id=60`, was affected by this: the barcode `11111111674` is allocated to one of her `order_id`'s.

#### -o, --output_filepath

> Default: `customer_ids_to_barcodes.csv`

The filepath where the generated output `.csv` is stored.

#### -n, --no_of_top_customers

> Default: 5

The number of top customers logged.

## Run unittests

```python
python -m pytest .
```

## SQL data model
By combining the relationships between the input files, we arrive at a simple data model:

![SQL data model](https://github.com/nikked/didactic-waffle/blob/master/images/db_model.png)

* A customer can have 0+ order_ids
* There cannot exist an order without a customer. Therefore the foreign key `customer_id` is non-nullable (NN).
* An order must have 1+ barcodes

### About indexes
Indexes can significantly decrease the amount of time required to find a database row based on some column names. However, they incur a computational cost in write time since the index itself needs to be updated. Moreover, the index itself consumes memory. Therefore only columns that are frequently searched should be indexed.

Primary keys are always indexed automatically in most database implementations. Therefore we only have two columns left (FK `customer_id` and FK `order_id`) where we could consider creating an index.

I would suggest creating an index for both of these foreign keys. This would enable a fast query for the following questions:
* Which barcodes are associated with a particular order_id?
* Which orders are associated with a specific customer_id?

The computational cost of updating the index is negligible since the update is only done once. (The customer_id of an order will most likely not change, and the same applies for the order_id of a barcode). Furthermore, the memory cost is likely to be way smaller than the advantage of fast queries.


## Githook
I like to use a pre-commit githook that automatically runs unittests, pylint, mypy (type checker) and black (code formatter). The githook ensures that each commit made to the repo will meet quality requirements. To enable my githook please use the following commands:
```bash
chmod 777 .githooks/pre-commit
git config core.hooksPath .githooks
```
