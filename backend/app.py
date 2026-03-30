from flask import Flask, session, request, jsonify, render_template, make_response, send_from_directory
from datetime import datetime
import os
import json

from fpdf import FPDF

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("FLASK_SECRET") or "dev-secret-key"

# Simple in-memory store for invoices to support PDF download after checkout
invoice_store = {}

# Path to project root (parent of backend/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_tours():
    tours_path = os.path.join(PROJECT_ROOT, "tours.json")
    with open(tours_path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_cart():
    if "cart" not in session:
        session["cart"] = {}
    return session["cart"]

def cart_items():
    cart = ensure_cart()
    items = []
    for pid, data in cart.items():
        items.append({
            "id": pid,
            "name": data["name"],
            "price": float(data["price"]),
            "qty": int(data["qty"]),
            "total": float(data["price"]) * int(data["qty"])
        })
    return items

def cart_total():
    items = cart_items()
    return sum(i["total"] for i in items)

@app.route("/api/cart/add", methods=["POST"])
def api_cart_add():
    data = request.get_json(force=True) or {}
    pid = str(data.get("id"))
    name = data.get("name", "")
    price = float(data.get("price", 0.0))
    qty = int(data.get("qty", 1))
    if not pid:
        return jsonify({"ok": False, "error": "missing_id"}), 400
    cart = ensure_cart()
    if pid in cart:
        cart[pid]["qty"] = cart[pid]["qty"] + qty
    else:
        cart[pid] = {"name": name, "price": price, "qty": qty}
    session.modified = True
    return jsonify({"ok": True, "cart": cart})

@app.route("/api/cart/update", methods=["POST"])
def api_cart_update():
    data = request.get_json(force=True) or {}
    pid = str(data.get("id"))
    qty = int(data.get("qty", 1))
    cart = ensure_cart()
    if pid in cart:
        cart[pid]["qty"] = max(0, qty)
        if cart[pid]["qty"] == 0:
            del cart[pid]
    session.modified = True
    return jsonify({"ok": True, "cart": cart})

@app.route("/api/cart/remove", methods=["POST"])
def api_cart_remove():
    data = request.get_json(force=True) or {}
    pid = str(data.get("id"))
    cart = ensure_cart()
    if pid in cart:
        del cart[pid]
    session.modified = True
    return jsonify({"ok": True, "cart": cart})

@app.route("/api/cart", methods=["GET"])
def api_cart_get():
    items = cart_items()
    total = sum(i["total"] for i in items)
    return jsonify({"items": items, "total": total})

@app.route("/cart", methods=["GET"])
def cart_page():
    items = cart_items()
    total = sum(i["total"] for i in items)
    return render_template("cart.html", items=items, total=total)

@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.get_json(force=True) or {}
    customer_name = data.get("customer_name") or ""
    customer_email = data.get("customer_email") or ""

    items = cart_items()
    total = sum(i["total"] for i in items)
    order_id = datetime.now().strftime("%Y%m%d%H%M%S")

    invoice = {
        "order_id": order_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "items": items,
        "total": total,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Persist invoice for PDF generation
    invoice_store[order_id] = invoice

    # Clear cart after checkout
    session.pop("cart", None)
    session.modified = True

    return render_template("invoice.html", invoice=invoice)

@app.route("/invoice_html", methods=["GET"])
def invoice_html():
    order_id = request.args.get("order_id")
    invoice = invoice_store.get(order_id)
    if not invoice:
        return "Invoice not found", 404
    return render_template("invoice.html", invoice=invoice)

def generate_invoice_pdf(invoice):
    pdf = FPDF()
    pdf.add_page()
    # Use built-in font (no Unicode Vietnamese support, but avoids dependency issues)
    pdf.set_font("Helvetica", "B", 16)

    # Header
    pdf.cell(0, 10, "HÓA ĐƠN THANH TOÁN", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Ma don hang: {invoice['order_id']}", ln=True)
    pdf.cell(0, 6, f"Ngay: {invoice['date']}", ln=True)
    pdf.cell(0, 6, f"Khach hang: {invoice['customer_name']}", ln=True)
    pdf.cell(0, 6, f"Email: {invoice['customer_email']}", ln=True)
    pdf.ln(8)

    # Table header
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(80, 8, "San pham", border=1)
    pdf.cell(30, 8, "Don gia", border=1, align="R")
    pdf.cell(20, 8, "SL", border=1, align="C")
    pdf.cell(40, 8, "Thanh tien", border=1, align="R")
    pdf.ln()

    # Table rows
    pdf.set_font("Helvetica", "", 10)
    for item in invoice["items"]:
        # Truncate long names for PDF
        name = item["name"][:40]
        pdf.cell(80, 8, name, border=1)
        pdf.cell(30, 8, f"{item['price']:,.0f}", border=1, align="R")
        pdf.cell(20, 8, str(item["qty"]), border=1, align="C")
        pdf.cell(40, 8, f"{item['total']:,.0f}", border=1, align="R")
        pdf.ln()

    # Total
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(130, 10, "TONG CONG", border=1, align="R")
    pdf.cell(40, 10, f"{invoice['total']:,.0f} VND", border=1, align="R")
    pdf.ln()

    pdf.ln(10)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, "Cam on quy khach da su dung dich vu!", ln=True, align="C")

    return bytes(pdf.output(dest="S"))


@app.route("/api/tours", methods=["GET"])
def api_tours():
    tours = load_tours()
    return jsonify(tours)


@app.route("/api/tours/<tour_id>", methods=["GET"])
def api_tour_detail(tour_id):
    tours = load_tours()
    for t in tours:
        if t["id"] == tour_id:
            return jsonify(t)
    return jsonify({"error": "not_found"}), 404


@app.route("/invoice_pdf", methods=["GET"])
def invoice_pdf():
    order_id = request.args.get("order_id")
    invoice = invoice_store.get(order_id)
    if not invoice:
        return "Invoice not found", 404
    pdf_bytes = generate_invoice_pdf(invoice)
    response = make_response(pdf_bytes)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=invoice-{order_id}.pdf"
    return response


# ---- Serve static files from project root (HTML, CSS, JS, images) ----

@app.route("/scripts/<path:filename>")
def serve_script(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, "scripts"), filename)


@app.route("/<path:filename>")
def serve_static(filename):
    # Try exact file first
    exact = os.path.join(PROJECT_ROOT, filename)
    if os.path.isfile(exact):
        return send_from_directory(PROJECT_ROOT, filename)
    # Try appending .html
    html_path = os.path.join(PROJECT_ROOT, filename + ".html")
    if os.path.isfile(html_path):
        return send_from_directory(PROJECT_ROOT, filename + ".html")
    return "Not found", 404


@app.route("/")
def index():
    return send_from_directory(PROJECT_ROOT, "Tour.html")


if __name__ == "__main__":
    # Bind to all interfaces to be accessible from other machines (optional in dev)
    app.run(debug=True, host="0.0.0.0", port=5000)
