# CSV transformer


## Input
#### orders.csv:
*order_id, customer_id*

This contains a list of orders. order_id is unique.


#### barcodes.csv
*barcode, order_id*
The barcodes in our system. If a barcode has been sold, it’s assigned to an order using order_id, otherwise order_id is empty.


## Output
**output.csv:** customer_id, order_id1, [barcode1, barcode2, ...]



## Validation
> Items which failed the validation should be logged (e.g. stderr) and ignored for the output.

* No duplicate barcodes
* No orders without barcodes

### Run unittests

```python
python -m pytest .
```


### Enable githook
```bash
chmod 750 .githooks/pre-commit
git config core.hooksPath .githooks
```