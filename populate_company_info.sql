/*

For this script, it is necessary to get the data processed by sócios-brasil
in this branch https://github.com/turicas/socios-brasil/tree/novo-formato

Before running this script, make sure to save the acquired files 'empresa.csv',
'socio.csv' and 'establishment.csv' in the 'data/' folder.

*/

-- ------------------------
-- START DATA IMPORTATION
-- ------------------------

DROP TABLE IF EXISTS empresa_temp;
CREATE TABLE "empresa_temp" (
    "cnpj_raiz" CHAR(8),
    "razao_social" TEXT,
    "codigo_natureza_juridica" INTEGER,
    "codigo_qualificacao_responsavel" INTEGER,
    "capital_social" TEXT,
    "codigo_porte" CHAR(7),
    "ente_federativo" TEXT
);
COPY empresa_temp FROM '/mnt/data/empresa.csv' DELIMITER ',' CSV HEADER;

DROP TABLE IF EXISTS estabelecimento_temp;
CREATE TABLE "estabelecimento_temp" (
    "cnpj_raiz" CHAR(8),
    "cnpj_ordem" CHAR(4),
    "cnpj_dv" CHAR(2),
    "matriz_filial" INTEGER,
    "nome_fantasia" TEXT,
    "codigo_situacao_cadastral" INTEGER,
    "data_situacao_cadastral" CHAR(8),
    "codigo_motivo_situacao_cadastral" INTEGER,
    "cidade_exterior" TEXT,
    "codigo_pais" CHAR(4),
    "data_inicio_atividade" CHAR(8),
    "cnae_principal" INTEGER,
    "cnae_secundaria" TEXT,
    "tipo_logradouro" TEXT,
    "logradouro" TEXT,
    "numero" TEXT,
    "complemento" TEXT,
    "bairro" TEXT,
    "cep" TEXT,
    "uf" TEXT,
    "codigo_municipio" INTEGER,
    "ddd_1" CHAR(4),
    "telefone_1" TEXT,
    "ddd_2" CHAR(4),
    "telefone_2" TEXT,
    "ddd_do_fax" CHAR(4),
    "fax" TEXT,
    "correio_eletronico" TEXT,
    "situacao_especial" TEXT,
    "data_situacao_especial" CHAR(8)
);
COPY estabelecimento_temp FROM '/mnt/data/estabelecimento.csv' DELIMITER ',' CSV HEADER;

DROP TABLE IF EXISTS socio_temp;
CREATE TABLE "socio_temp" (
    "cnpj_raiz" CHAR(8),
    "codigo_identificador" INTEGER,
    "nome" TEXT,
    "cpf_cnpj" CHAR(16),
    "codigo_qualificacao" INTEGER,
    "data_entrada_sociedade" CHAR(8),
    "codigo_pais" CHAR(4),
    "representante_cpf_cnpj" CHAR(16),
    "representante" TEXT,
    "representante_codigo_qualificacao" INTEGER,
    "codigo_faixa_etaria" INTEGER
);
COPY socio_temp FROM '/mnt/data/socio.csv' DELIMITER ',' CSV HEADER;

-- -----------------------------------
-- START DATA CLEANING AND FORMATTING
-- -----------------------------------

-- HELPER METHODS

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "unaccent";

CREATE OR REPLACE FUNCTION clean_text(text) RETURNS text
    AS $$ select trim(upper(unaccent($1))); $$
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;

CREATE OR REPLACE FUNCTION format_date(text) RETURNS date
    AS $$
      BEGIN
        RETURN TO_DATE($1,'YYYYMMDD');
      EXCEPTION
        WHEN others THEN RETURN NULL;
      END;
    $$
    LANGUAGE plpgsql
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;

CREATE OR REPLACE FUNCTION generate_uuid(nome text, cpf text) RETURNS uuid
    AS $$
        declare
            cpf_six_digits text;
            formatted_name text;
            resp text;
        begin
            SELECT substring(cpf, 4, 6) INTO cpf_six_digits;
            SELECT REPLACE(clean_text(nome), ' ', '-') INTO formatted_name;
            SELECT
                uuid_generate_v5(uuid_ns_url(), 'https://id.brasil.io/v1/person/' || cpf_six_digits || '-' || formatted_name)
                INTO resp;
            return resp;
        end
    $$
    LANGUAGE plpgsql
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;

-- AUXILIARY TABLE WITH CLEANED DATA

DROP TABLE IF EXISTS empresas_socios_temp;
CREATE TABLE "empresas_socios_temp" (
    "cnpj_raiz" CHAR(8),
    "cnpj_ordem" CHAR(4),
    "cnpj_dv" CHAR(2),
    "nome_empresa" TEXT,
    "cnae_principal" INTEGER,
    "cnae_secundaria" TEXT,
    "data_inicio_atividade" DATE,
    "uf" CHAR(4),
    "nome_socio" TEXT,
    "cpf_socio" TEXT,
    "data_entrada_sociedade" DATE,
    "socio_merge_uuid" uuid
);
CREATE INDEX temp_idx_cnpj_raiz ON empresas_socios_temp(cnpj_raiz);
CREATE INDEX temp_idx_cpf_socio ON empresas_socios_temp(cpf_socio);
CREATE INDEX temp_idx_socio_merge_uuid ON empresas_socios_temp(socio_merge_uuid NULLS LAST);

INSERT INTO empresas_socios_temp
SELECT
    etabelecimento.cnpj_raiz,
    etabelecimento.cnpj_ordem,
    etabelecimento.cnpj_dv,
    etabelecimento.nome_fantasia as nome_empresa,
    etabelecimento.cnae_principal,
    etabelecimento.cnae_secundaria,
    format_date(etabelecimento.data_inicio_atividade) as data_inicio_atividade,
    etabelecimento.uf,
    associados.nome_socio,
    associados.cpf_socio,
    COALESCE(associados.data_entrada_sociedade, format_date(etabelecimento.data_inicio_atividade)) as data_entrada_sociedade,
    generate_uuid(associados.nome_socio, associados.cpf_socio) as socio_merge_uuid
FROM estabelecimento_temp as etabelecimento
LEFT JOIN (
    SELECT
        socio.cnpj_raiz,
        socio.nome as nome_socio,
        socio.cpf_cnpj as cpf_socio,
        format_date(socio.data_entrada_sociedade) as data_entrada_sociedade
    FROM socio_temp as socio WHERE socio.codigo_identificador = 2 AND socio.cpf_cnpj != '***000000**'
    UNION
    select
        empresa.cnpj_raiz,
        empresa.nome_socio,
        empresa.cpf as cpf_socio,
        null as data_entrada_sociedade
    FROM
        (select
             substring(empresa_temp.razao_social from '[0-9]*$') as cpf,
             substring(empresa_temp.razao_social from '\D*') as nome_socio,
             *
         FROM empresa_temp) as empresa
    WHERE (empresa.cpf = '') IS NOT TRUE
) as associados ON associados.cnpj_raiz = etabelecimento.cnpj_raiz;

-- -----------------------
-- POPULATING MAIN TABLES
-- -----------------------

-- ENRICHING CANDIDATES (owned_companies)
UPDATE core_candidate
SET owned_companies = candidates_companies.companies
FROM (
    select candidate_id,
    json_agg(companies_owned_by_candidates) as companies
    from (
        -- search from companies when we have the full cpf of the associate
         select core_candidate.id as candidate_id,
                cnpj_raiz,
                cnpj_ordem,
                cnpj_dv,
                nome_empresa,
                cnae_principal,
                cnae_secundaria,
                data_inicio_atividade,
                uf,
                data_entrada_sociedade
         from empresas_socios_temp
            inner join core_candidate
                ON empresas_socios_temp.cpf_socio = core_candidate.taxpayer_id
         where (empresas_socios_temp.cpf_socio not like '*%')
           and (core_candidate.taxpayer_id = '') IS NOT TRUE
         union
         -- search from companies when we don't have the full cpf of the associate
         -- and need to search by name + cpf (socio_merge_uuid)
         select core_candidate.id as candidate_id,
                cnpj_raiz,
                cnpj_ordem,
                cnpj_dv,
                nome_empresa,
                cnae_principal,
                cnae_secundaria,
                data_inicio_atividade,
                uf,
                data_entrada_sociedade
         from empresas_socios_temp
            inner join core_candidate
                ON empresas_socios_temp.socio_merge_uuid = generate_uuid(core_candidate.name, core_candidate.taxpayer_id)
         where (empresas_socios_temp.cpf_socio like '*%')
           and (core_candidate.taxpayer_id = '') IS NOT TRUE
     ) as companies_owned_by_candidates
    group by companies_owned_by_candidates.candidate_id
) as candidates_companies
where core_candidate.id = candidates_companies.candidate_id;

-- ENRICHING ELECTION INCOME STATEMENT (donor_company_information)
UPDATE core_election_income_statement
-- if a person has more than 1 company only one will be saved :(
SET donor_company_information = to_json(result)
FROM (
    -- search data when donor has cnpj
     select core_election_income_statement.id as income_id,
            cnpj_raiz,
            cnpj_ordem,
            cnpj_dv,
            nome_empresa,
            cnae_principal,
            cnae_secundaria,
            data_inicio_atividade,
            uf
     from empresas_socios_temp
      inner join core_election_income_statement
         ON empresas_socios_temp.cnpj_raiz = substring(core_election_income_statement.donor_taxpayer_id, 1, 8)
     where LENGTH(core_election_income_statement.donor_taxpayer_id) > 11
    union
     -- search data when donor has cpf and companies don't have the full cpf of the associate
     select core_election_income_statement.id as income_id,
            cnpj_raiz,
            cnpj_ordem,
            cnpj_dv,
            nome_empresa,
            cnae_principal,
            cnae_secundaria,
            data_inicio_atividade,
            uf
     from empresas_socios_temp
      inner join core_election_income_statement
        ON empresas_socios_temp.socio_merge_uuid = generate_uuid(core_election_income_statement.donor_name, core_election_income_statement.donor_taxpayer_id)
     where (empresas_socios_temp.cpf_socio like '*%') and LENGTH(core_election_income_statement.donor_taxpayer_id) = 11
     union
       -- search data when donor has cpf and companies don't have the full cpf of
       -- the associate and we need to search by name + cpf (socio_merge_uuid)
         select core_election_income_statement.id as income_id,
         cnpj_raiz,
         cnpj_ordem,
         cnpj_dv,
         nome_empresa,
         cnae_principal,
         cnae_secundaria,
         data_inicio_atividade,
         uf
     from empresas_socios_temp
         inner join core_election_income_statement
     ON empresas_socios_temp.cpf_socio = core_election_income_statement.donor_taxpayer_id
     where (empresas_socios_temp.cpf_socio not like '*%') and LENGTH(core_election_income_statement.donor_taxpayer_id) = 11
) as result
where core_election_income_statement.id = result.income_id;

-- --------------------
-- CLEANING THINGS UP
-- --------------------

DROP TABLE IF EXISTS empresa_temp, estabelecimento_temp, socio_temp, empresas_socios_temp;
DROP FUNCTION IF EXISTS clean_text, format_date, generate_uuid;
