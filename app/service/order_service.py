import logging
from sqlalchemy import Engine

from app.repository.order_repository import OrderRepository
from app.repository.product_repository import ProductRepository
from app.model.order_model import CreateOrderModel, OrderItem
from app.errors.generic_error import CustomError

LOGGER = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self, engine: Engine, order_repo: OrderRepository, product_repo: ProductRepository
    ):
        self.engine = engine
        self.order_repo = order_repo
        self.product_repo = product_repo

    def create_product(self, order_data: CreateOrderModel):
        return self._check_product_stocks(order_items=order_data.items)
        # TODO: -Calculate subtotal
        #       -Reduce stock
        #

    def _check_product_stocks(self, order_items: list[OrderItem]):
        try:
            # double check if there are same ids, combine if there is
            combined_items = {}
            for item in order_items:
                if item.product_id not in combined_items:
                    combined_items.update({item.product_id: item.quantity})
                else:
                    combined_items[item.product_id] += item.quantity
            order_item_ids = list(combined_items.keys())
            stock_items = self.product_repo.get_products_by_ids(order_item_ids)
            # check if there are non existing ids
            result_item_ids = [item.get("id") for item in stock_items]
            inexisting_ids = [id for id in order_item_ids if id not in result_item_ids]
            if inexisting_ids:
                raise CustomError(
                    404, "NotFound", f"Product id(s) {inexisting_ids} not found", order_items
                )
            # check if stocks are available
            inssufficient_items = []
            for stock_item in stock_items:
                stock_item_id = stock_item.get("id")
                stock_item_qty = stock_item.get("stock_quantity")
                order_item_quantity = combined_items.get(stock_item.get("id"))
                if order_item_quantity > stock_item_qty:
                    inssufficient_items.append(stock_item_id)
            if inssufficient_items:
                # TODO: Update return ids to SKU
                raise CustomError(
                    422,
                    "ValidationError",
                    f"Insufficient stock for product(s) {', '.join(map(str, inssufficient_items))}",
                    order_items,
                )
                # combined_items.get(stock_item)
            return result_item_ids
        except CustomError as e:
            LOGGER.exception(e)
            raise e
        except Exception as e:
            LOGGER.exception(e)
            raise e
        finally:
            LOGGER.info("get_products end")

    # def _list_of_items_to_dict(my_list):
