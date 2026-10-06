-- =====================================================================
-- Projeto de Recuperação - Módulo 1 (SCTEC / SENAI-SC)
-- Visualização de Dados e Business Intelligence
-- Aluno: Jandir Medeiros dos Reis
-- Banco: Oracle FreeSQL (https://freesql.com) - esquema HR (Human Resources)
-- =====================================================================


-- ---------------------------------------------------------------------
-- QUERY 1 - Comparação de salários por departamento e cargo
-- Tabelas: EMPLOYEES (base) + LEFT JOIN DEPARTMENTS + LEFT JOIN JOBS
-- Filtro: WHERE e.salary IS NOT NULL (somente funcionários com salário)
-- O LEFT JOIN mantém funcionários mesmo sem departamento cadastrado.
-- Resultado exportado para: data/query_01.csv (107 linhas)
-- ---------------------------------------------------------------------
SELECT
    e.employee_id,
    e.first_name,
    e.last_name,
    e.department_id,
    d.department_name,
    e.job_id,
    j.job_title,
    e.salary,
    j.min_salary,
    j.max_salary
FROM hr.employees e
LEFT JOIN hr.departments d
       ON e.department_id = d.department_id
LEFT JOIN hr.jobs j
       ON e.job_id = j.job_id
WHERE e.salary IS NOT NULL
ORDER BY e.salary DESC;


-- ---------------------------------------------------------------------
-- QUERY 2 - Distribuição dos funcionários por cidade, país e região
-- Tabelas: EMPLOYEES (base) + LEFT JOIN DEPARTMENTS + LEFT JOIN LOCATIONS
--          + LEFT JOIN COUNTRIES + LEFT JOIN REGIONS
-- Filtro: WHERE r.region_name IS NOT NULL (remove quem não tem local definido)
-- Resultado exportado para: data/query_02.csv (106 linhas)
-- ---------------------------------------------------------------------
SELECT
    e.employee_id,
    e.first_name,
    e.last_name,
    d.department_name,
    l.city,
    l.state_province,
    c.country_id,
    c.country_name,
    r.region_name
FROM hr.employees e
LEFT JOIN hr.departments d
       ON e.department_id = d.department_id
LEFT JOIN hr.locations l
       ON d.location_id = l.location_id
LEFT JOIN hr.countries c
       ON l.country_id = c.country_id
LEFT JOIN hr.regions r
       ON c.region_id = r.region_id
WHERE r.region_name IS NOT NULL
ORDER BY r.region_name, c.country_name, l.city, e.employee_id;
