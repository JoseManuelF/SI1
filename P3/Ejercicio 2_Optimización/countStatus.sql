CREATE INDEX myIndex ON orders (status)

explain analyze select count(*)
from orders
where status is null;

explain analyze select count(*)
from orders
where status ='Shipped';

explain analyze select count(*)
from orders
where status ='Paid';

explain analyze select count(*)
from orders
where status ='Processed';

DROP INDEX myIndex
