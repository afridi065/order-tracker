import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    for record in event["Records"]:
        order = json.loads(record["body"])
        order_id = order.get("order_id")
        logger.info("Processing order %s", order_id)

        # Deliberate failure so we can test the DLQ
        if order.get("customer") == "poison":
            raise ValueError(f"Cannot process order {order_id}")

        logger.info(
            "Order %s processed: %s x%s for %s",
            order_id, order["item"], order["quantity"], order["customer"],
        )

    return {"processed": len(event["Records"])}
