from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=64))
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)

class RecommendationHistorySchema(Schema):
    id = fields.Int(dump_only=True)
    planner_type = fields.Str(required=True)
    budget = fields.Float(required=True)
    input_data = fields.Str()
    recommendation_data = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)

user_schema = UserSchema()
recommendation_schema = RecommendationHistorySchema()
recommendations_schema = RecommendationHistorySchema(many=True)
