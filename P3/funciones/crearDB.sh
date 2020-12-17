export PGUSER=alumnodb
export PGPASSWORD=alumnodb
export PGDATABASE=si1

dropdb si1
createdb -U alumnodb si1
cat sql/dump_v1.2-P3.sql | psql -U alumnodb si1
