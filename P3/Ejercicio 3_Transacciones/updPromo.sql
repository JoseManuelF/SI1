-- Añadimos una columna promo a la tabla customers que contendrá
-- un descuento promocional
ALTER TABLE customers
    ADD promo numeric
;

UPDATE orders SET status = 'null' WHERE customerid = '305';

-- Procedimiento que es llamado por el trigger
CREATE OR REPLACE FUNCTION updPromo() RETURNS TRIGGER AS $$
BEGIN
    UPDATE orderdetail
    SET
        price = (products.price - (products.price * (NEW.promo/100))) * quantity --NEW.promo
    FROM
        orders,
        products
    WHERE
        NEW.customerid = orders.customerid and --NEW.customerid
        orders.status = 'null' and
        orders.orderid = orderdetail.orderid and
        orderdetail.prod_id = products.prod_id;

    PERFORM pg_sleep(5);

    UPDATE orders
    SET
        netamount = totalSum.sumValue
    FROM
        (
	    SELECT orders.orderid, SUM(orderdetail.price) AS sumValue
	    FROM orderdetail, orders
	    WHERE 
		orderdetail.orderid = orders.orderid and
	        NEW.customerid = orders.customerid
	    GROUP BY orders.orderid
        ) AS totalSum
     WHERE totalSum.orderid = orders.orderid;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Creamos el trigger que al alterar la columna promo de un cliente, haga un
-- descuento en los artículos de su cesta o carrito del porcentaje indicado
-- en la columna promo sobre el precio de la tabla products
CREATE TRIGGER updPromo
AFTER UPDATE OF promo ON customers
FOR EACH ROW
    EXECUTE PROCEDURE updPromo();

UPDATE customers SET promo = 50 WHERE customerid = '305';
