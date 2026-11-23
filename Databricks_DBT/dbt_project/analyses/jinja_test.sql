{%- set apples = ["Gala", "Fuji", "Honeycrisp", "Red Delicious"] -%}
{% for i in apples %}
    {% if i != "Fuji" %}
        {{ i }}
    {% else %}
        {{ i }} is not a good apple
    {% endif %}
{% endfor %}