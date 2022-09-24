

  create or replace view `musify-354416`.`musify_prod`.`my_second_dbt_model`
  OPTIONS()
  as -- Use the `ref` function to select from other models

select *
from `musify-354416`.`musify_prod`.`my_first_dbt_model`
where id = 1;

