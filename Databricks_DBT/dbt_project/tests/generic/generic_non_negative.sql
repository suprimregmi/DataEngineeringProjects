
{% test generic_non_negative(model, column_name) %}
select * from {{model}} 
 where {{column}} < 0

 {% endtest %}
