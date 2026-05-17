import logging
from sqlalchemy import Engine
from sqlalchemy.orm import Session
from decimal import Decimal

from app.repository.order_repository import OrderRepository
from app.repository.product_repository import ProductRepository
from app.repository.order_item_repository import OrderItemRepository
from app.repository.discount_repository import DiscountRepository
from app.model.order_model import CreateOrderModel, Items, OrderInfoModel
from app.model.order_item_model import OrderItemCreateModel, OrderItemsSubtotal
from app.model.product_model import ProductModel, ProductPatchModel
from app.model.discount_model import DiscountModel
from app.errors.generic_error import (
    DatabaseError,
    NotFoundError,
    CustomValidationError,
    ServiceError,
    CustomError,
)

LOGGER = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        engine: Engine,
        order_repo: OrderRepository,
        product_repo: ProductRepository,
        order_item_repo: OrderItemRepository,
        discount_repo: DiscountRepository,
    ):
        self.engine = engine
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.order_item_repo = order_item_repo
        self.discount_repo = discount_repo

    def get_orders(self):
        try:
            LOGGER.info("get_orders service end")
            orders = self.order_repo.get_orders()
            return orders
        except DatabaseError as e:
            raise e
        except Exception as e:
            LOGGER.exception(e)
            raise ServiceError("Service Error") from e
        finally:
            LOGGER.info("get_orders service end")

    def create_order(self, order_data: CreateOrderModel):

        try:
            # check if there are repeating ids, combine if there are
            itm_id_and_qty_agg = {}
            for item in order_data.items:
                if item.product_id not in itm_id_and_qty_agg:
                    itm_id_and_qty_agg.update({item.product_id: item.quantity})
                else:
                    itm_id_and_qty_agg[item.product_id] += item.quantity

            stock_items = self._verify_products_and_stocks(order_data.items, itm_id_and_qty_agg)
            items_subtotal = self._calculate_sub_total(stock_items, itm_id_and_qty_agg)
            total_amnt = sum(item.subtotal for item in items_subtotal)
            discount = (
                self._get_and_validate_discount_code(order_data)
                if order_data.discount_code
                else None
            )
            order_info = self._apply_discount(total_amnt, order_data, discount)
            LOGGER.info("order_info: %s", order_info)

            # start session for mulitple repositories
            with Session(self.engine) as session:
                # single transaction
                with session.begin():
                    created_order_id = self.order_repo.create_order(session, order_info)
                    order_item_ids = []
                    updated_product_ids = []
                    # create order items
                    for item in items_subtotal:
                        order_item_create_model = OrderItemCreateModel(
                            order_id=created_order_id,
                            product_id=item.product_id,
                            quantity=item.quantity,
                            unit_price=item.unit_price,
                            subtotal=item.subtotal,
                        )
                        # create order_item record
                        order_item_id = self.order_item_repo.create_order_item(
                            session, order_item_create_model
                        )
                        order_item_ids.append(order_item_id)
                        product_patch_model = ProductPatchModel(
                            stock_quantity=item.projected_quantity
                        )
                        # update product stocks
                        updated_product_id = self.product_repo.update_product(
                            item.product_id, product_patch_model, session=session
                        )
                        updated_product_ids.append(updated_product_id.get("updated_id"))

            return {
                "order_id": created_order_id,
                "order_item_ids": order_item_ids,
                "updated_product_ids": updated_product_ids,
            }
        except DatabaseError as e:
            raise e
        except CustomError as e:
            LOGGER.warning(e)
            raise e
        except Exception as e:
            LOGGER.exception(e)
            raise ServiceError("Service Error", order_data.model_dump(mode="json")) from e
        finally:
            LOGGER.info("get_products end")

    def get_order_and_items(self, order_id: int):
        try:
            LOGGER.info("get_order_and_items service start")
            result = self.order_repo.get_order_and_items(order_id)
            if not result:
                raise NotFoundError("Order not found.", {"order_id": order_id})
            return result
        except DatabaseError as e:
            raise e
        except CustomError as e:
            LOGGER.warning(e)
            raise e
        except Exception as e:
            LOGGER.exception(e)
            raise ServiceError("Service Error", {"order_id": order_id}) from e
        finally:
            LOGGER.info("get_order_and_items service end")

    def _verify_products_and_stocks(self, order_items: list[Items], combined_items: list[Items]):
        order_item_ids = list(combined_items.keys())
        stock_items = self.product_repo.get_products_by_ids(order_item_ids)
        # check if there are non existing ids
        stock_items_ids = [item.id for item in stock_items]
        inexisting_ids = [id for id in order_item_ids if id not in stock_items_ids]
        if inexisting_ids:
            raise NotFoundError(f"Product id(s) {inexisting_ids} not found.", order_items)
        # check if stocks are available
        insufficient_items = []
        for stock_item in stock_items:
            order_item_quantity = combined_items.get(stock_item.id)
            if order_item_quantity > stock_item.stock_quantity:
                insufficient_items.append(stock_item.id)
        if insufficient_items:
            # TODO: Update return SKU instead of ids
            raise CustomValidationError(
                f"Insufficient stock for product(s) {', '.join(map(str, insufficient_items))}.",
                order_items,
            )
            # combined_items.get(stock_item)
        return stock_items

    def _calculate_sub_total(
        self, products: list[ProductModel], combined_order_items: dict
    ) -> list[OrderItemsSubtotal]:
        items_subtotal = []
        for product in products:
            # build subtotal
            subtotal: Decimal = product.price * combined_order_items.get(product.id)
            item_subtotal = OrderItemsSubtotal(
                product_id=product.id,
                unit_price=product.price,
                quantity=combined_order_items.get(product.id),
                subtotal=subtotal,
                projected_quantity=product.stock_quantity - combined_order_items.get(product.id),
            )

            items_subtotal.append(item_subtotal)
        return items_subtotal

    def _get_and_validate_discount_code(self, order_data: CreateOrderModel):
        discount = self.discount_repo.get_discount(order_data.discount_code)
        if not discount:
            raise NotFoundError("Discount code not found.", order_data)
        return discount

    def _apply_discount(
        self, total_amount, order_data: CreateOrderModel, discount: DiscountModel
    ) -> OrderInfoModel:
        if not discount:
            return OrderInfoModel(
                customer_name=order_data.customer_name,
                customer_email=order_data.customer_email,
                total_amount=total_amount,
                final_amount=total_amount,
            )
        match discount.unit:
            case "fixed":
                discount_amount = discount.value
                LOGGER.info("FIXED DISCOUNT AMOUNT: %s", discount_amount)
                final_amount = total_amount - discount_amount
            case "percentage":
                discount_amount = total_amount * (Decimal(discount.value) / 100)
                LOGGER.info("PERCENTAGE DISCOUNT AMOUNT: %s", discount_amount)
                final_amount = Decimal(total_amount - discount_amount)

        order_info = OrderInfoModel(
            customer_name=order_data.customer_name,
            customer_email=order_data.customer_email,
            total_amount=total_amount,
            discount_code=discount.discount_code,
            discount_amount=discount_amount,
            final_amount=final_amount,
            discount_id=discount.id,
        )
        return order_info
