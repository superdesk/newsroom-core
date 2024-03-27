def add_company_products(app, company_id, products):
    company = app.data.find_one("companies", req=None, _id=company_id)
    app.data.insert("products", products)
    company_products = company["products"] or []
    for product in products:
        company_products.append({"_id": product["_id"], "section": product["product_type"], "seats": 0})
    app.data.update("companies", company["_id"], {"products": company_products}, company)
