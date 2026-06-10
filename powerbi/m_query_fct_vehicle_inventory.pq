let
    Source = Csv.Document(
        File.Contents("C:\Users\Ideapad Pro5i\Projects\vehicle-vin-analytics-platform\powerbi\data\fct_vehicle_inventory.csv"),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders,{
        {"picture_count", Int64.Type},
        {"stock_number", type text},
        {"model_year", Int64.Type},
        {"make", type text},
        {"model", type text},
        {"style", type text},
        {"exterior_color", type text},
        {"mileage", Int64.Type},
        {"has_condition_report", Int64.Type},
        {"grade", type number},
        {"primary_light", type text},
        {"mileage_bucket", type text},
        {"grade_tier", type text},
        {"vin", type text},
        {"vehicle_age", Int64.Type},
        {"is_as_is", Int64.Type},
        {"has_structural_damage", Int64.Type}
    })
in
    ChangedTypes
