-- Procedimiento que es llamado por el trigger
CREATE OR REPLACE FUNCTION updOrders() RETURNS TRIGGER AS $$
BEGIN
    PERFORM setOrderAmount();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Creamos el trigger que actualiza la información de la tabla orders
-- cuando se modifica, añade o elimina un artículo en el carrito (tabla orderdetail)
CREATE TRIGGER updOrders
AFTER INSERT OR DELETE OR UPDATE ON orderdetail
FOR EACH ROW
    EXECUTE PROCEDURE updOrders();
