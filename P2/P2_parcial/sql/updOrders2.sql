-- Procedimiento que es llamado por el trigger
CREATE OR REPLACE FUNCTION updOrders() RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        -- Actualizamos el precio al insertarse un order
        UPDATE orders
        SET netamount = netamount + (NEW.price * NEW.quantity);
        setOrderAmount();
    ELSIF (TG_OP = 'DELETE') THEN
        -- Actualizamos el precio al eliminar un order
        UPDATE orders
        SET netamount = netamount - (OLD.price * OLD.quantity);
        setOrderAmount();
    ELSIF (TG_OP = 'UPDATE') THEN
        -- Actualizamos el precio al incrementar la cantidad de un order
        UPDATE orders
        SET netamount = netamount - (NEW.price * NEW.quantity);
        setOrderAmount();
    ELSE
        RAISE EXCEPTION "Invalid action on updOrders";
    ENDIF;
END;
$$ LANGUAGE plpgsql;

-- Creamos el trigger que actualiza la información de la tabla orders
-- cuando se añade o elimina un artículo al carrito
CREATE TRIGGER tr
AFTER INSERT OR DELETE OR UPDATE ON orderdetail
FOR EACH ROW
    EXECUTE PROCEDURE updOrders();
