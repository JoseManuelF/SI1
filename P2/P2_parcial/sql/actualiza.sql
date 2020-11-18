-- Creamos una nueva tabla languages
CREATE TABLE languages (
	language character varying(32) NOT NULL,
    languageid integer NOT NULL,

    CONSTRAINT languages_pkey PRIMARY KEY (languageid)
);

-- Creamos una secuencia para los id de language
CREATE SEQUENCE languages_languageid_seq
increment 1 START 1 NO minvalue NO maxvalue cache 1;

-- Añadimos la secuencia a la primary key de la tabla languages
ALTER TABLE only languages
ALTER COLUMN languageid SET default nextval('languages_languageid_seq'::regclass);

-- Añadimos los nombres de los idiomas a la tabla
INSERT INTO languages
SELECT DISTINCT language
FROM imdb_movielanguages;

-- Actualizamos la tabla imdb_movielanguages. Ahora tendrá una foreign key
-- a la nueva tabla languages
UPDATE imdb_movielanguages
SET language = languages.languageid
FROM languages WHERE imdb_movielanguages.language = languages.language;

ALTER TABLE imdb_movielanguages
    ALTER COLUMN language TYPE integer USING(language::integer),
    ADD CONSTRAINT imdb_movielanguages_movieid_fkey2 foreign key (language)
        REFERENCES languages(languageid)
;

-- Creamos una nueva tabla genres
CREATE TABLE genres (
	genre character varying(32) NOT NULL,
    genreid integer NOT NULL,

    CONSTRAINT genres_pkey PRIMARY KEY (genreid)
);

-- Creamos una secuencia para los id de genre
CREATE SEQUENCE genres_genreid_seq
increment 1 START 1 NO minvalue NO maxvalue cache 1;

-- Añadimos la secuencia a la primary key de la tabla genres
ALTER TABLE only genres
ALTER COLUMN genreid SET default nextval('genres_genreid_seq'::regclass);

-- Añadimos los nombres de los géneros a la tabla
INSERT INTO genres
SELECT DISTINCT genre
FROM imdb_moviegenres;

-- Actualizamos la tabla imdb_movielgenres. Ahora tendrá una foreign key
-- a la nueva tabla genres
UPDATE imdb_moviegenres
SET genre = genres.genreid
FROM genres WHERE imdb_moviegenres.genre = genres.genre;

ALTER TABLE imdb_moviegenres
    ALTER COLUMN genre TYPE integer USING(genre::integer),
    ADD CONSTRAINT imdb_moviegenres_genreid_fkey2 foreign key (genre)
        REFERENCES genres(genreid)
;

-- Añadir foreign keys que faltan a las tablas orderdetail, imdb_actormovies, inventory y orders
ALTER TABLE orderdetail
    ADD CONSTRAINT orderdetail_orderid_fkey foreign key (orderid)
        REFERENCES orders(orderid),
    ADD CONSTRAINT orderdetail_prod_id_fkey2 foreign key (prod_id)
        REFERENCES products(prod_id)
;

ALTER TABLE imdb_actormovies
    ADD CONSTRAINT imdb_actormovies_actorid_fkey foreign key (actorid)
        REFERENCES imdb_actors(actorid),
    ADD CONSTRAINT imdb_actormovies_movieid_fkey2 foreign key (movieid)
        REFERENCES imdb_movies(movieid)
;

ALTER TABLE inventory
    ADD CONSTRAINT inventory_prod_id_fkey foreign key (prod_id)
        REFERENCES products(prod_id)
;

ALTER TABLE orders
    ADD CONSTRAINT orders_orderid_fkey foreign key (customerid)
        REFERENCES customers(customerid)
;

-- Quitamos del título de las película el año, ya que tenemos un campo separado para éste
UPDATE imdb_movies
SET movietitle=substring(movietitle FROM 0 for LENGTH(movietitle) - 6);

-- Creamos una nueva tabla countries
CREATE TABLE countries (
    country character varying(32) NOT NULL,
    countryid integer NOT NULL,

    CONSTRAINT countries_pkey PRIMARY KEY (countryid)
);

-- Creamos una secuencia para los id de countries
CREATE SEQUENCE countries_countryid_seq
increment 1 START 1 NO minvalue NO maxvalue cache 1;

-- Añadimos la secuencia a la primary key de la tabla countries
ALTER TABLE only countries
ALTER COLUMN countryid SET default nextval('countries_countryid_seq'::regclass);

-- Añadimos los nombres de los países a la tabla
INSERT INTO countries
SELECT DISTINCT country
FROM imdb_moviecountries;

-- Añadir a movies una foreign key al id del país
ALTER TABLE imdb_movies
    ADD countryid integer,

    ADD CONSTRAINT imdb_movies_countryid_fkey FOREIGN KEY (countryid)
        REFERENCES countries(countryid)
;

-- Añadir a customers una foreign key al id del país
ALTER TABLE customers
    ADD countryid integer,

    ADD CONSTRAINT customers_countryid_fkey FOREIGN KEY (countryid)
        REFERENCES countries(countryid)
;

-- Cambiar la id del país para que sea el país que ponía en imdb_moviecountries
UPDATE imdb_movies
SET countryid = c.countryid
FROM countries c, imdb_moviecountries mc
WHERE
    imdb_movies.movieid = mc.movieid AND
    mc.country = c.country
;

-- Cambiar la id del país para que sea el país que ponía en customer.country
UPDATE customers
SET countryid = c.countryid
FROM countries c
WHERE
    customers.country = c.country
;

-- Borramos la columna country, que sería redundante ahora que tenemos country id
ALTER TABLE customers
    DROP COLUMN country
;

-- Borramos la tabla moviecountry que ya no necesitamos
DROP TABLE imdb_moviecountries;

-- Creamos una nueva tabla alertas que requiere el trigger updInventory para indicar
-- si no hay stock de una película que se quiere comprar
CREATE TABLE alertas (
    prod_id integer NOT NULL,
    alertadate date NOT NULL,

    CONSTRAINT alertas_prod_id_fkey foreign key (prod_id)
    REFERENCES products(prod_id)
);
