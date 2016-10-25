from datetime import datetime
import argparse
import common.args
import v20.transaction


class OrderArguments(object):
    """
    OrderArguments is a wrapper that manages adding command line parameters 
    used to configure Order creation
    """

    def __init__(self, parser):
        # Store the argument parser to add arguments to
        self.parser = parser

        # The order_request contains all of the parameters parsed for order
        # creation
        self.order_request = {}

        # The list of param_parsers are used to automatically interpret
        # order arguments that have been added
        self.param_parsers = []

    def parse_arguments(self, args):
        """
        Call each param parser with the parsed arguments to extract the value
        into the order_request
        """
        for parser in self.param_parsers:
            parser(args)


    def add_trade_id(self):
        self.parser.add_argument(
            "--trade-id",
            required=True,
            help=(
                "The ID of the Trade to create an Order for. If prepended "
                "with an '@', this will be interpreted as a client Trade ID"
            )
        )

        self.param_parsers.append(
            lambda args: self.parse_trade_id(args)
        )


    def parse_trade_id(self, args):
        if args.trade_id is None:
            return

        if args.trade.id[0] == '@':
            self.order_request["clientTradeID"] = args.trade_id[1:]
        else:
            self.order_request["tradeID"] = args.trade_id


    def parse_trade_id(self, args):
        if args.trade_id is None:
            return

        self.order_request["tradeID"] = args.trade_id


    def add_instrument(self):
        self.parser.add_argument(
            "--instrument",
            type=common.args.instrument,
            required=True,
            help="The instrument to place the Order for"
        )

        self.param_parsers.append(
            lambda args: self.parse_instrument(args)
        )


    def parse_instrument(self, args):
        if args.instrument is None:
            return

        self.order_request["instrument"] = args.instrument


    def add_units(self):
        self.parser.add_argument(
            "--units",
            required=True,
            help=(
                "The number of units for the Order. "
                "Negative values indicate sell, Positive values indicate buy"
            )
        )

        self.param_parsers.append(
            lambda args: self.parse_units(args)
        )


    def parse_units(self, args):
        if args.units is None:
            return

        self.order_request["units"] = args.units


    def add_price(self):
        self.parser.add_argument(
            "--price",
            required=True,
            help="The price threshold for the Order"
        )

        self.param_parsers.append(
            lambda args: self.parse_price(args)
        )


    def parse_price(self, args):
        if args.price is None:
            return

        self.order_request["price"] = args.price


    def add_distance(self):
        self.parser.add_argument(
            "--distance",
            required=True,
            help="The price distance for the Order"
        )

        self.param_parsers.append(
            lambda args: self.parse_distance(args)
        )


    def parse_distance(self, args):
        if args.distance is None:
            return

        self.order_request["distance"] = args.distance


    def add_time_in_force(self, choices=["FOK", "IOC", "GTC", "GFD", "GTD"]):
        self.parser.add_argument(
            "--time-in-force",
            choices=choices,
            help="The time-in-force to use for the Order"
        )

        if "GTD" in choices:
            self.parser.add_argument(
                "--gtd-time",
                type=common.args.date_time(),
                help=(
                    "The date to use when the time-in-force is GTD. "
                    "Format is 'YYYY-MM-DD HH:MM:SS"
                )
            )

        self.param_parsers.append(
            lambda args: self.parse_time_in_force(args)
        )


    def parse_time_in_force(self, args):
        if args.time_in_force is None:
            return

        self.order_request["timeInForce"] = args.time_in_force

        if args.time_in_force != "GTD":
            return

        if args.gtd_time is None:
            self.parser.error(
                "must set --gtd-time \"YYYY-MM-DD HH:MM:SS\" when "
                "--time-in-force=GTD"
            )
            return
            
        self.order_request["gtdTime"] = \
            args.gtd_time.strftime("%Y-%m-%dT%H:%M:%S.000000000Z")
        

    def add_price_bound(self):
        self.parser.add_argument(
            "--price-bound",
            help="The worst price bound allowed for the Order"
        )

        self.param_parsers.append(
            lambda args: self.parse_price_bound(args)
        )
        

    def parse_price_bound(self, args):
        if args.price_bound is None:
            return

        self.order_request["priceBound"] = args.price_bound


    def add_position_fill(self):
        self.parser.add_argument(
            "--position-fill",
            choices=["DEFAULT", "OPEN_ONLY", "REDUCE_FIRST", "REDUCE_ONLY"],
            required=False,
            help="Specification of how the Order may affect open positions."
        )

        self.param_parsers.append(
            lambda args: self.parse_position_fill(args)
        )


    def parse_position_fill(self, args):
        if args.position_fill is None:
            return

        self.order_request["positionFill"] = args.position_fill


    def add_client_order_extensions(self):
        self.parser.add_argument(
            "--client-order-id",
            help="The client-provided ID to assign to the Order"
        )

        self.parser.add_argument(
            "--client-order-tag",
            help="The client-provided tag to assign to the Order"
        )

        self.parser.add_argument(
            "--client-order-comment",
            help="The client-provided comment to assign to the Order"
        )

        self.param_parsers.append(
            lambda args: self.parse_client_order_extensions(args)
        )


    def parse_client_order_extensions(self, args):
        if (args.client_order_id is None and
            args.client_order_tag is None and
            args.client_order_comment is None):
            return
        
        kwargs = {}

        if args.client_order_id is not None:
            kwargs["id"] = args.client_order_id

        if args.client_order_tag is not None:
            kwargs["tag"] = args.client_order_tag

        if args.client_order_comment is not None:
            kwargs["comment"] = args.client_order_comment

        self.order_request["clientExtensions"] = \
            v20.transaction.ClientExtensions(
                **kwargs
            )


    def add_client_trade_extensions(self):
        self.parser.add_argument(
            "--client-trade-id",
            help="The client-provided ID to assign a Trade opened by the Order"
        )

        self.parser.add_argument(
            "--client-trade-tag",
            help=(
                "The client-provided tag to assign to a Trade opened by the "
                "Order"
            )
        )

        self.parser.add_argument(
            "--client-trade-comment",
            help=(
                "The client-provided comment to assign to a Trade opened by "
                "the Order"
            )
        )

        self.param_parsers.append(
            lambda args: self.parse_client_trade_extensions(args)
        )


    def parse_client_trade_extensions(self, args):
        if (args.client_trade_id is None and
            args.client_trade_tag is None and
            args.client_trade_comment is None):
            return None
        
        kwargs = {}

        if args.client_trade_id is not None:
            kwargs["id"] = args.client_trade_id

        if args.client_trade_tag is not None:
            kwargs["tag"] = args.client_trade_tag

        if args.client_trade_comment is not None:
            kwargs["comment"] = args.client_trade_comment

        self.order_request["tradeClientExtensions"] = \
            v20.transaction.ClientExtensions(
                **kwargs
            )


    def add_take_profit_on_fill(self):
        self.parser.add_argument(
            "--take-profit-price",
            help=(
                "The price of the Take Profit to add to a Trade opened by this "
                "Order"
            )
        )

        self.param_parsers.append(
            lambda args: self.parse_take_profit_on_fill(args)
        )


    def parse_take_profit_on_fill(self, args):
        if args.take_profit_price is None:
            return
        
        kwargs = {}

        kwargs["price"] = args.take_profit_price

        self.order_request["takeProfitOnFill"] = \
            v20.transaction.TakeProfitDetails(**kwargs)


    def add_stop_loss_on_fill(self):
        self.parser.add_argument(
            "--stop-loss-price",
            help=(
                "The price of the Stop Loss to add to a Trade opened by this "
                "Order"
            )
        )

        self.param_parsers.append(
            lambda args: self.parse_stop_loss_on_fill(args)
        )


    def parse_stop_loss_on_fill(self, args):
        if args.stop_loss_price is None:
            return
        
        kwargs = {}

        kwargs["price"] = args.stop_loss_price

        self.order_request["stopLossOnFill"] = \
            v20.transaction.StopLossDetails(**kwargs)


    def add_trailing_stop_loss_on_fill(self):
        self.parser.add_argument(
            "--trailing-stop-loss-distance",
            help=(
                "The price distance for the Trailing Stop Loss to add to a "
                "Trade opened by this Order"
            )
        )

        self.param_parsers.append(
            lambda args: self.parse_trailing_stop_loss_on_fill(args)
        )


    def parse_trailing_stop_loss_on_fill(self, args):
        if args.trailing_stop_loss_distance is None:
            return
        
        kwargs = {}

        kwargs["distance"] = args.stop_loss_distance

        self.order_request["trailingStopLossOnFill"] = \
            v20.transaction.TrailingStopLossDetails(
                **kwargs
            )
