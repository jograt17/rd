import logging
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from decimal import Decimal

from app.repository.order_repository import OrderRepository
from app.repository.product_repository import ProductRepository
from app.repository.order_item_repository import OrderItemRepository
from app.model.order_model import CreateOrderModel, Items
from app.model.order_item_model import OrderItemCreateModel
from app.model.product_model import ProductModel, ProductPatchModel
from app.errors.generic_error import CustomError

LOGGER = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        engine: Engine,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        order_item_repo: OrderItemRepository,
    ):
        self.engine = engine
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.order_item_repo = order_item_repo

    def create_order(self, order_data: CreateOrderModel):

        # double check if there are same ids, combine if there is
        combined_order_items = {}
        for item in order_data.items:
            if item.product_id not in combined_order_items:
                combined_order_items.update({item.product_id: item.quantity})
            else:
                combined_order_items[item.product_id] += item.quantity

        stock_items = self._verify_products_and_stocks(order_data.items, combined_order_items)
        items_subtotal = self._calculate_sub_total(stock_items, combined_order_items)
        total_amnt = sum(item.get("subtotal") for item in items_subtotal)
        with Session(self.engine) as session:
            with session.begin():
                created_order_id = self.order_repo.create_order(
                    session, order_data.customer_name, order_data.customer_email, total_amnt
                )
                order_item_ids = []
                updated_product_ids = []
                # create order item

                for item in items_subtotal:
                    order_item_creeate_model = OrderItemCreateModel(
                        order_id=created_order_id,
                        product_id=item.get("product_id"),
                        quantity=item.get("quantity"),
                        unit_price=item.get("unit_price"),
                        subtotal=item.get("subtotal"),
                    )
                    order_item_id = self.order_item_repo.create_order_item(
                        session, order_item_creeate_model
                    )
                    order_item_ids.append(order_item_id)
                    product_patch_model = ProductPatchModel(
                        stock_quantity=item.get("projected_quantity")
                    )
                    updated_product_id = self.product_repo.update_product(
                        item.get("product_id"), product_patch_model, session=session
                    )
                    updated_product_ids.append(updated_product_id.get("updated_id"))

        # update stocks

        return {"order_item_ids": order_item_ids, "updated_product_ids": updated_product_ids}

        # get ids - verify if exist
        # TODO: -Calculate subtotal
        #       -Create Order
        #       -reduce stock atomically

    def get_order_and_items(self, order_id: int):
        try:
            LOGGER.info("get_order_and_items service start")
            LOGGER.info("order_id: %s", order_id)
            result = self.order_repo.get_order_and_items(order_id)
            return result
        except CustomError as e:
            LOGGER.exception(e)
            raise e
        except Exception as e:
            LOGGER.exception(e)
            raise e
        finally:
            LOGGER.info("get_order_and_items service end")

    def _verify_products_and_stocks(self, order_items: list[Items], combined_items: list[Items]):
        try:
            order_item_ids = list(combined_items.keys())
            stock_items = self.product_repo.get_products_by_ids(order_item_ids)
            # check if there are non existing ids
            stock_items_ids = [item.id for item in stock_items]
            inexisting_ids = [id for id in order_item_ids if id not in stock_items_ids]
            if inexisting_ids:
                raise CustomError(
                    404, "NotFound", f"Product id(s) {inexisting_ids} not found", order_items
                )
            # check if stocks are available
            insufficient_items = []
            for stock_item in stock_items:
                order_item_quantity = combined_items.get(stock_item.id)
                if order_item_quantity > stock_item.stock_quantity:
                    insufficient_items.append(stock_item.id)
            if insufficient_items:
                # TODO: Update return ids to SKU
                raise CustomError(
                    422,
                    "ValidationError",
                    f"Insufficient stock for product(s) {', '.join(map(str, insufficient_items))}",
                    order_items,
                )
                # combined_items.get(stock_item)
            return stock_items
        except CustomError as e:
            LOGGER.exception(e)
            raise e
        except Exception as e:
            LOGGER.exception(e)
            raise e
        finally:
            LOGGER.info("get_products end")

    def _calculate_sub_total(self, products: list[ProductModel], combined_order_items: dict):
        items_subtotal = []
        for product in products:
            # build subtotal
            subtotal: Decimal = product.price * combined_order_items.get(product.id)
            item_subtotal = {
                "product_id": product.id,
                "unit_price": product.price,
                "quantity": combined_order_items.get(product.id),
                "subtotal": subtotal,
                "projected_quantity": product.stock_quantity - combined_order_items.get(product.id),
            }
            items_subtotal.append(item_subtotal)
        return items_subtotal

    # def _list_of_items_to_dict(my_list):
