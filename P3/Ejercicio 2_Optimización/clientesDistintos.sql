--DROP INDEX myIndex;
--CREATE INDEX myIndex ON public.orders (orderdate);
--;

SELECT
    tablename,
    indexname,
    indexdef
FROM
    pg_indexes
WHERE
    schemaname = 'public'
ORDER BY
    tablename,
    indexname;

---------------------------------------------------------

ALTER TABLE orders DROP CONSTRAINT orders_pkey CASCADE;

----------------------------------------------------------

SELECT
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

------------------------------------------------------------

--DROP INDEX orders_pkey;
--CREATE UNIQUE INDEX orders_pkey ON public.orders USING btree (orderid);

--DROP INDEX myIndex;
--CREATE INDEX myIndex ON public.orders USING btree (totalamount);