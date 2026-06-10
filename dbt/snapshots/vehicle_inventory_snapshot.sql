{% snapshot vehicle_inventory_snapshot %}

{{
    config(
      target_schema='snapshots',
      unique_key='vin',
      strategy='timestamp',
      updated_at='_loaded_at',
    )
}}

-- TODO: Implement SCD Type 2 snapshot
select 1 as placeholder

{% endsnapshot %}
