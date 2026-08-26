from flask import request


def paginate_query(query):
    """Paginate a SQLAlchemy query. Validates page/per_page against negative or
    zero values, and caps per_page at 100 to prevent abuse."""
    page = max(request.args.get("page", 1, type=int) or 1, 1)
    per_page = request.args.get("per_page", 20, type=int) or 20
    per_page = max(1, min(per_page, 100))

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return {
        "items": items,
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": (total + per_page - 1) // per_page if total else 0,
    }