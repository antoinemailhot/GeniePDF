from utils.schemas import base_schema, facture_schema, plan_schema, requisition_schema

SCHEMA_MAP = {
    "facture": facture_schema.schema,
    "plan": plan_schema.schema,
    "requisition": requisition_schema.schema,
    "default": base_schema.schema
}
