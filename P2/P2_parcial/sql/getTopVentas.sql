CREATE OR REPLACE FUNCTION getTopVentas(year1 INTEGER, year2 INTEGER)
RETURNS TABLE(year_ DOUBLE PRECISION, movie_ CHARACTER VARYING(255), top_ BIGINT) AS $$
BEGIN
    -- Creamos una view para obtener todas las películas vendidas y el
    -- año en el que se vendieron
    CREATE OR REPLACE VIEW MoviesYear AS
        SELECT 
            extract(year FROM orders.orderdate) as year_, 
            imdb_movies.movietitle as movie_
        FROM 
            public.products, 
            public.orders, 
            public.orderdetail, 
            public.imdb_movies
        WHERE 
            products.prod_id = orderdetail.prod_id AND
            products.movieid = imdb_movies.movieid AND
            orderdetail.orderid = orders.orderid
    ;

    -- Creamos una view que cuenta cuántas veces una película fue
    -- vendida cada año
    CREATE OR REPLACE VIEW CountYear AS
        SELECT
            year_, movie_, count(movie_) as frequency_
        FROM
            MoviesYear
        GROUP BY
            year_, movie_
    ;

    -- Creamos una view para obtener el número de veces que ha sido vendida
    -- la película más vendida de cada año
    CREATE OR REPLACE VIEW CountTop AS
        SELECT
            year_, max(frequency_) AS top_
        FROM
            CountYear
        GROUP BY
            year_
    ;

    -- Procedimiento que consigue las películas más vendidas de cada año
    -- y varias en caso de empate
    RETURN QUERY
	SELECT
        CountYear.year_, CountYear.movie_,
        CountTop.top_
    FROM
        CountTop, CountYear
    WHERE
        CountTop.year_ = CountYear.year_ AND
        CountTop.top_ = CountYear.frequency_ AND
        CountTop.year_ >= year1 AND
        CountTop.year_ <= year2;

END;
$$ LANGUAGE plpgsql;

-- Invocación al procedimiento
SELECT * FROM getTopVentas(2016, 2019);
