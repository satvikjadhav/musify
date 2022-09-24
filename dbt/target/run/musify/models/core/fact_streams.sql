

  create or replace table `musify-354416`.`musify_prod`.`fact_streams`
  partition by timestamp_trunc(ts, hour)
  
  OPTIONS()
  as (
    

SELECT 
    dim_users.userKey AS userKey,
    dim_artists.artistKey AS artistKey,
    dim_songs.songKey AS songKey ,
    dim_datetime.dateKey AS dateKey,
    dim_location.locationKey AS locationKey,
    listen_events.ts AS ts
FROM `musify-354416`.`musify_stg`.`listen_events`
    LEFT JOIN `musify-354416`.`musify_prod`.`dim_users` 
        ON listen_events.userId = dim_users.userId AND CAST(listen_events.ts AS DATE) >= dim_users.rowActivationDate AND CAST(listen_events.ts AS DATE) < dim_users.RowExpirationDate
    LEFT JOIN `musify-354416`.`musify_prod`.`dim_artists` 
        ON REPLACE(REPLACE(listen_events.artist, '"', ''), '\\', '') = dim_artists.name
    LEFT JOIN `musify-354416`.`musify_prod`.`dim_songs` 
        ON REPLACE(REPLACE(listen_events.artist, '"', ''), '\\', '') = dim_songs.artistName AND listen_events.song = dim_songs.title
    LEFT JOIN `musify-354416`.`musify_prod`.`dim_location` 
        ON listen_events.city = dim_location.city AND listen_events.state = dim_location.stateCode AND listen_events.lat = dim_location.latitude AND listen_events.lon = dim_location.longitude 
    LEFT JOIN `musify-354416`.`musify_prod`.`dim_datetime` 
        ON dim_datetime.date = date_trunc(listen_events.ts, HOUR)
  );
  