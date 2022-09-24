

  create or replace table `musify-354416`.`musify_prod`.`dim_location`
  
  
  OPTIONS()
  as (
    

SELECT to_hex(md5(cast(coalesce(cast(latitude as 
    string
), '') || '-' || coalesce(cast(longitude as 
    string
), '') || '-' || coalesce(cast(city as 
    string
), '') || '-' || coalesce(cast(stateName as 
    string
), '') as 
    string
))) as locationKey,
*
FROM
    (
        SELECT 
            distinct city,
            COALESCE(state_codes.stateCode, 'NA') as stateCode,
            COALESCE(state_codes.stateName, 'NA') as stateName,
            lat as latitude,
            lon as longitude
        FROM `musify-354416`.`musify_stg`.`listen_events`
        LEFT JOIN `musify-354416`.`musify_prod`.`state_codes` on listen_events.state = state_codes.stateCode

        UNION ALL

        SELECT 
            'NA',
            'NA',
            'NA',
            0.0,
            0.0
    )
  );
  