-- Creamos una view con las ventas totales, ganancias,
-- mes y año.
CREATE OR REPLACE VIEW FullTable AS
    SELECT
        extract(month FROM orders.orderdate) AS month_,
        extract(year FROM orders.orderdate) AS year_,
        SUM(orderdetail.price * orderdetail.quantity) AS price_,
        SUM(orderdetail.quantity) AS sold_
    FROM
        public.orders,
        public.orderdetail
    WHERE
        orderdetail.orderid = orders.orderid
    GROUP BY
        extract(month FROM orders.orderdate),
        extract(year FROM orders.orderdate)
;

-- Procedimiento que separa de la tabla anterior los meses que cumplen la condición.
-- Devuelve el mes, el año, el dinero y las ventas.
CREATE OR REPLACE FUNCTION getTopMonths(products INTEGER, money NUMERIC)
RETURNS TABLE(year_ DOUBLE PRECISION, month_ DOUBLE PRECISION, import_ NUMERIC, products_ BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM
        FullTable
    WHERE
        price_ >= money OR
        sold_ >= products;
END;
$$ LANGUAGE plpgsql;

-- Invocación al procedimiento
SELECT * FROM getTopMonths(19000, 320000);
