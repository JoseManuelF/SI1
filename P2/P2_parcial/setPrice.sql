DROP VIEW IF EXISTS UpdatedPrice;
DROP VIEW IF EXISTS YearVsPrice;

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

CREATE OR REPLACE VIEW UpdatedPrice AS
SELECT oid, pid, (price - (0.02 * price * yearsago)) as newprice
FROM YearVsPrice
;

UPDATE public.orderdetail
SET price = up.newprice
FROM UpdatedPrice up
WHERE orderId = up.oid and prod_id = up.pid;