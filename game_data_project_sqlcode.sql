WITH base AS (
    SELECT
        g."Game"  AS game,
        g."Price" AS price,
        g."Release date" AS release_date,
        g."Owners" AS owners,                    -- cleaned like 0-20000
        g."Playtime (Median)" AS playtime_median,
        g."Developer(s)" AS developers,
        g."Publisher(s)" AS publishers
    FROM main.sample_game_data_rpgs_csv g
),
ea_norm AS (
    SELECT LOWER(TRIM(ea."Game")) AS game_key
    FROM main.early_access ea
),
joined AS (
    SELECT
        b.*,
        CASE WHEN ea.game_key IS NOT NULL THEN 1 ELSE 0 END AS is_early_access
    FROM base b
    LEFT JOIN ea_norm ea
      ON LOWER(TRIM(b.game)) = ea.game_key
),
enriched AS (
    SELECT
        j.*,
        -- numeric price + finer buckets with explicit "At $60"
        CAST(j.price AS DOUBLE) AS numeric_price,
        CASE
            WHEN CAST(j.price AS DOUBLE) = 0  THEN 'Free'
            WHEN CAST(j.price AS DOUBLE) < 5  THEN 'Below $5'
            WHEN CAST(j.price AS DOUBLE) < 10 THEN 'Below $10'
            WHEN CAST(j.price AS DOUBLE) < 20 THEN 'Below $20'
            WHEN CAST(j.price AS DOUBLE) < 30 THEN 'Below $30'
            WHEN CAST(j.price AS DOUBLE) < 60 THEN 'Below $60'
            WHEN CAST(j.price AS DOUBLE) = 60 THEN 'At $60'
            ELSE 'Above $60'
        END AS price_range,

        -- owners split (owners is like 0-20000)
        TRY_CAST(SPLIT_PART(j.owners, '-', 1) AS DOUBLE) AS owners_min,
        TRY_CAST(SPLIT_PART(j.owners, '-', 2) AS DOUBLE) AS owners_max,
        (TRY_CAST(SPLIT_PART(j.owners, '-', 1) AS DOUBLE)
       + TRY_CAST(SPLIT_PART(j.owners, '-', 2) AS DOUBLE)) / 2.0 AS owners_estimate,
        (TRY_CAST(SPLIT_PART(j.owners, '-', 2) AS DOUBLE)
       - TRY_CAST(SPLIT_PART(j.owners, '-', 1) AS DOUBLE)) AS owners_range,

        -- parse release date
        COALESCE(
            TRY_STRPTIME(j.release_date, '%Y-%m-%d'),
            TRY_STRPTIME(j.release_date, '%b %d, %Y'),
            TRY_STRPTIME(j.release_date, '%d %b %Y')
        ) AS release_dt
    FROM joined j
),
final_rows AS (
    SELECT
        e.*,
        CASE WHEN e.is_early_access = 1 THEN 'Early Access' ELSE 'Full Release' END AS release_type,
        EXTRACT(YEAR FROM e.release_dt)    AS release_year,
        EXTRACT(QUARTER FROM e.release_dt) AS release_quarter
    FROM enriched e
)
SELECT
    -- Overall rank
    ROW_NUMBER() OVER (
        ORDER BY owners_estimate DESC NULLS LAST
    ) AS popularity_rank_overall,

    -- Rank within release type
    ROW_NUMBER() OVER (
        PARTITION BY release_type
        ORDER BY owners_estimate DESC NULLS LAST
    ) AS popularity_rank_in_type,

    -- Rank within price bucket
    ROW_NUMBER() OVER (
        PARTITION BY price_range
        ORDER BY owners_estimate DESC NULLS LAST
    ) AS rank_in_price_range,

    -- Rank within release year
    ROW_NUMBER() OVER (
        PARTITION BY release_year
        ORDER BY owners_estimate DESC NULLS LAST
    ) AS rank_in_release_year,

    final_rows.*
FROM final_rows
ORDER BY owners_estimate DESC NULLS LAST;