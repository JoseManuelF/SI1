-- Procedimiento que es llamado por el trigger
CREATE OR REPLACE FUNCTION updOrders() RETURNS TRIGGER AS $$
BEGIN
    setOrderAmount();
END;
$$ LANGUAGE plpgsql;

-- Creamos el trigger que actualiza la información de la tabla orders
-- cuando se añade o elimina un artículo al carrito
CREATE TRIGGER updOrders
AFTER INSERT OR DELETE OR UPDATE ON orderdetail
FOR EACH ROW
    EXECUTE PROCEDURE updOrders();
