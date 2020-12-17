CREATE OR REPLACE FUNCTION setOrderAmount() RETURNS void AS $$
BEGIN
    -- Creamos una view para obtener la suma de los precios de la
    -- película del pedido
    CREATE OR REPLACE VIEW OrderPrice AS
    SELECT
        orderid, SUM(price * quantity) as finalprice
    FROM
        public.orderdetail
    GROUP BY
        orderid
    ;

    -- Procedimiento que completa las columnas netamount y totalamount
    -- de la tabla orders
	UPDATE public.orders
	SET netamount = oprice.finalprice, totalamount = ROUND (oprice.finalprice + (oprice.finalprice * (tax/100)), 2)
    FROM OrderPrice oprice
    WHERE orders.orderid = oprice.orderid;

END;
$$ LANGUAGE plpgsql;

-- Invocación al procedimiento
SELECT setOrderAmount();
