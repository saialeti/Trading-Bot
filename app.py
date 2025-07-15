from flask import Flask, request, jsonify
from flask_cors import CORS
from tradelocker import TLAPI
import time

app = Flask(__name__)
CORS(app)

# Initialize TradeLocker API
tl = TLAPI(
    environment="https://demo.tradelocker.com",
    username="sai49577@gmail.com",
    password="t5$FoHrm",
    server="KOT-DEMO"
)

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "🟢 Server is running"}), 200

@app.route('/trade', methods=['POST'])
def place_trade():
    data = request.json
    print("📥 Received trade data:", data)

    try:
        embed = data["embeds"][0]
        symbol_name = embed["title"]
        description = embed["description"].lower()
        signal = "buy" if "buy" in description else "sell"

        fields = {f["name"]: f["value"] for f in embed["fields"]}

        lot_size = float(fields.get("Lot Size", 1.0))
        entry_price = float(fields.get("Entry Price", 0))
        sl_price = float(fields.get("SL Price", 0))
        tp_price = float(fields.get("TP Price", 0))
        breakeven_price = float(fields.get("Breakeven Price", 0))  # optional

        if not symbol_name or not entry_price or lot_size <= 0:
            return jsonify({"error": "Missing required trade parameters"}), 400

        instrument_id = tl.get_instrument_id_from_symbol_name(symbol_name)

        # Option 1: Remove position_netting for limit orders
        order_id = tl.create_order(
            instrument_id=instrument_id,
            quantity=lot_size,
            side=signal,
            price=entry_price,
            type_="limit",
            validity="GTC",
            take_profit=tp_price,
            take_profit_type="absolute",
            stop_loss=sl_price,
            stop_loss_type="absolute"
        )

        
        if order_id:
            print(f"✅ Limit Order Placed: {order_id}")
            return jsonify({
                "status": "Limit order placed",
                "order_id": order_id,
                "symbol": symbol_name,
                "signal": signal,
                "lot_size": lot_size,
                "entry_price": entry_price,
                "sl_price": sl_price,
                "tp_price": tp_price
            }), 200
        else:
            return jsonify({"error": "Order placement failed"}), 500

    except Exception as e:
        print("❌ Error placing trade:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=3000, debug=True)
