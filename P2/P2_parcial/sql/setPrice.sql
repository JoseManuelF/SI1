-- Creamos una view para obtener una tabla con el precio y año
-- de cada producto de todos los pedidos
CREATE OR REPLACE VIEW YearVsPrice AS
SELECT
	products.price as price,
  	orderdetail.orderid as oid,
  	orderdetail.prod_id as pid,
  	2020 - extract(year from orders.orderdate) as yearsago
FROM
  	public.products,
  	public.orders,
  	public.orderdetail
WHERE
  	products.prod_id = orderdetail.prod_id AND
  	orderdetail.orderid = orders.orderid;
;

-- Creamos una view para obtener el precio de las películas reducidas
-- un 2% anual
CREATE OR REPLACE VIEW UpdatedPrice AS
SELECT oid, pid, ROUND (cast(POWER ( 0.98 , yearsago) * price as numeric), 2) as newprice
FROM YearVsPrice
;

-- Completar la columna price de la tabla orderdetail
UPDATE public.orderdetail
SET price = up.newprice
FROM UpdatedPrice up
WHERE orderId = up.oid and prod_id = up.pid;
