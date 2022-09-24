

SELECT to_hex(md5(cast(coalesce(cast(songId as 
    string
), '') as 
    string
))) AS songKey,
       *
FROM (

        (
            SELECT song_id as songId,
                REPLACE(REPLACE(artist_name, '"', ''), '\\', '') as artistName,
                duration,
                key,
                key_confidence as keyConfidence,
                loudness,
                song_hotttnesss as songHotness,
                tempo,
                title,
                year
            FROM `musify-354416`.`musify_stg`.`songs`
        )

        UNION ALL

        (
            SELECT 'NNNNNNNNNNNNNNNNNNN',
                'NA',
                0,
                -1,
                -1,
                -1,
                -1,
                -1,
                'NA',
                0
        )
    )