-- View 1
CREATE OR REPLACE VIEW v_assets_trend AS
SELECT period, grand_total_assets, local_assets_total, foreign_assets_total
FROM sama_data
ORDER BY period;

-- View 2
CREATE OR REPLACE VIEW v_yoy_growth AS
SELECT EXTRACT(YEAR FROM period) AS year,
       ROUND(AVG(grand_total_assets)::numeric, 2) AS avg_assets
FROM sama_data
GROUP BY year
ORDER BY year;

-- View 3
CREATE VIEW v_asset_composition AS
SELECT period, local_shares, local_bonds, local_funds, local_real_estate, local_other,
       foreign_shares, foreign_bonds, foreign_funds, foreign_other
FROM sama_data
ORDER BY period DESC
LIMIT 1;

-- View 4
CREATE OR REPLACE VIEW v_funds_subscribers AS
SELECT period, active_funds_count, subscribers_count
FROM sama_data
ORDER BY period;