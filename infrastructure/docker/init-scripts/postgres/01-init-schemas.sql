-- PostgreSQL init: run DDL on first container start
\i /docker-entrypoint-initdb.d/001_create_schemas.sql
