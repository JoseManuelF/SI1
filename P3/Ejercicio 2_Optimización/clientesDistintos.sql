CREATE INDEX myIndex ON public.orders (orderdate);

EXPLAIN SELECT
	COUNT(CustomerAmount.customerid)
FROM
	(
	SELECT
		orders.customerid,
		SUM(orders.totalamount) AS amount
	FROM
		public.orders
	WHERE
		EXTRACT(year FROM orders.orderdate) = 2019 AND
		EXTRACT(month FROM orders.orderdate) = 11
	GROUP BY orders.customerid
	) AS CustomerAmount
WHERE
	CustomerAmount.amount >= 2
;

DROP INDEX myIndex;