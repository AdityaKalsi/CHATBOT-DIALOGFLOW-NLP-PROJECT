from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper

app = FastAPI()

@app.post('/')
async def handle_request(request:Request):

    payload = await request.json()

    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    if 'queryResult' in payload and 'output_Contexts' in payload['queryResult']:
        output_contexts = payload['queryResult']['output_Contexts']
    else:
        output_contexts = None  # or handle the absence of 'output_Contexts' as needed


    if intent == 'track.order - context: ongoing-tracking':
        response = await track_order(parameters)

    else:
        intent_handler_dict = {
        'order.add - context: ongoing-order': add_to_order,
        #'order.remove - context: ongoing-order': remove_from_order,
        #'order.complete - context: ongoing-order': complete_order,
        'track.order - context: ongoing-tracking': track_order
        }
        try:
            intent_handler = intent_handler_dict[intent]
            response = await intent_handler(parameters)
        except KeyError:
            response = JSONResponse(content={'error': f'Intent {intent} not found'}, status_code=404)

    return response


def add_to_order(parameters: dict):
    food_items = parameters["food-item"]
    quantities = parameters["number"]

    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I didn't understand. Can you please specify food items and quantities clearly?"
    else:
        fulfillment_text = f'Recieved'

    return JSONResponse(content={
        'fulfillmentText': fulfillmentText })
    


def track_order(parameters: dict):
    order_id = parameters.get('order_id')  # Retrieve the order_id from parameters

    if order_id:
        order_status = db_helper.get_order_status(order_id)

        if order_status:
            fulfillmentText = f'order status for order_id {order_id} is {order_status}'
        else:
            fulfillmentText = 'No order found'
    else:
        fulfillmentText = 'Invalid request: order_id is missing'

    return JSONResponse(content={
        'fulfillmentText': fulfillmentText })