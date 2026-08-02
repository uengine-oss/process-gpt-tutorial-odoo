# -*- coding: utf-8 -*-
"""
Odoo MCP x Claude Skill 워크북 — 실습 데이터 시딩 스크립트
============================================================

강의 전에 한 번 돌려 Odoo 샌드박스를 워크북이 기대하는 상태로 만든다.
여러 번 돌려도 안전하다(이름/코드로 먼저 찾고 없을 때만 생성).

사용법 (PowerShell):
    $env:ODOO_URL="https://<instance>.odoo.com"
    $env:ODOO_DB="<db>"
    $env:ODOO_USER="<login-email>"
    $env:ODOO_API_KEY="<api-key>"
    python materials/seed/seed_workshop_data.py

사용법 (bash):
    ODOO_URL=... ODOO_DB=... ODOO_USER=... ODOO_API_KEY=... \
      python materials/seed/seed_workshop_data.py

검증 환경: Odoo SaaS 19.4 (purchase / stock / account / mail 설치, 통화 KRW).
Odoo 19 에서 확인된 함정은 아래 주석에 그대로 남겨 두었다.
"""
import os
import sys
import xmlrpc.client

# --------------------------------------------------------------- connection
URL = os.environ.get("ODOO_URL")
DB = os.environ.get("ODOO_DB")
USER = os.environ.get("ODOO_USER")
KEY = os.environ.get("ODOO_API_KEY")
if not all([URL, DB, USER, KEY]):
    sys.exit("ODOO_URL / ODOO_DB / ODOO_USER / ODOO_API_KEY 환경변수를 먼저 설정하세요.")

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
UID = common.authenticate(DB, USER, KEY, {})
if not UID:
    sys.exit("인증 실패 — ODOO_USER / ODOO_API_KEY 를 확인하세요.")


def call(model, method, *args, **kw):
    return models.execute_kw(DB, UID, KEY, model, method, list(args), kw)


def search_read(model, domain=None, fields=None, **kw):
    if fields:
        kw["fields"] = fields
    return call(model, "search_read", domain or [], **kw)


def create(model, vals):
    return call(model, "create", vals)


def write(model, ids, vals):
    return call(model, "write", ids, vals)


def call_void(model, method, ids):
    """리턴이 None 인 메서드용. Odoo SaaS 19.4 XML-RPC 는 None 을 마샬링하지 못해
    호출은 성공해도 예외가 올라온다 — 그 경우만 무시한다."""
    try:
        return call(model, method, ids)
    except Exception as e:
        if "cannot marshal None" not in str(e):
            raise


# --------------------------------------------------------------- environment
WH = search_read("stock.warehouse", [], ["id", "lot_stock_id"])[0]
WH_ID, STOCK_LOC = WH["id"], WH["lot_stock_id"][0]
CATEG_GOODS = search_read("product.category", [], ["id"], limit=1)[0]["id"]
UOM_UNITS = search_read("uom.uom", [["name", "=", "Units"]], ["id"])[0]["id"]
KR = search_read("res.country", [["code", "=", "KR"]], ["id"])[0]["id"]
print(f"연결 OK — uid={UID}, warehouse={WH_ID}, stock_location={STOCK_LOC}")


# ------------------------------------------------------------------ partners
# (ref, 이름, 이메일, 전화, 도시, S=공급사 / C=고객)
COMPANIES = [
    ("SUP-01", "(주)한빛전자부품",  "sales@hanbit-parts.example.com",       "02-555-0101",  "성남시", "S"),
    ("SUP-02", "대한산업소재(주)",  "contact@daehan-materials.example.com", "041-555-0202", "아산시", "S"),
    ("SUP-03", "(주)정우정밀",     "order@jw-precision.example.com",       "031-555-0303", "화성시", "S"),
    ("SUP-04", "세강케이블(주)",    None,                                   "032-555-0404", "인천시", "S"),
    ("SUP-05", "(주)나노코팅테크",  "sales@nanocoat.example.com",           "053-555-0505", "대구시", "S"),
    ("SUP-06", "광성베어링(주)",    "ks@ks-bearing.example.com",            "051-555-0606", "부산시", "S"),
    ("SUP-07", "(주)에이스몰드",    None,                                   "055-555-0707", "김해시", "S"),
    ("SUP-08", "한결포장산업",      "hankyul@hankyul-pack.example.com",     None,           "청주시", "S"),
    ("CUS-01", "(주)미래모빌리티",  "po@mirae-mobility.example.com",        "031-555-0901", "화성시", "C"),
    ("CUS-02", "서한전자(주)",     "buy@seohan-elec.example.com",          "054-555-0902", "구미시", "C"),
]

# (이름, 소속 ref, 직책, 이메일, 전화)
CONTACTS = [
    ("김도현", "SUP-01", "영업팀장", "dh.kim@hanbit-parts.example.com",      "010-2222-0101"),
    ("박서연", "SUP-02", "구매담당", "sy.park@daehan-materials.example.com", "010-2222-0202"),
    ("이준호", "SUP-03", "생산관리", "jh.lee@jw-precision.example.com",      None),
    ("최민아", "SUP-04", "영업대표", None,                                   "010-2222-0404"),
    ("정태우", "SUP-05", "기술영업", "tw.jung@nanocoat.example.com",         "010-2222-0505"),
    ("한지원", "SUP-06", "품질담당", "jw.han@ks-bearing.example.com",        "010-2222-0606"),
]

partner = {}


def seed_partners():
    print("\n[1/3] 거래처")
    for ref, name, email, phone, city, kind in COMPANIES:
        vals = {"ref": ref, "email": email or False, "phone": phone or False,
                "city": city, "country_id": KR,
                "supplier_rank": 1 if kind == "S" else 0,
                "customer_rank": 1 if kind == "C" else 0}
        found = search_read("res.partner", [["name", "=", name]], ["id"])
        if found:
            pid = found[0]["id"]
            write("res.partner", [pid], vals)
        else:
            pid = create("res.partner", dict(vals, name=name))
        # is_company 는 Odoo 19 에서 create 시 무시되고 write 로만 반영된다.
        write("res.partner", [pid], {"is_company": True})
        partner[ref] = pid
        print(f"  {ref}  {name} (id={pid})")

    for name, pref, func, email, phone in CONTACTS:
        vals = {"function": func, "email": email or False, "phone": phone or False,
                "parent_id": partner[pref], "type": "contact"}
        found = search_read("res.partner",
                            [["name", "=", name], ["parent_id", "=", partner[pref]]], ["id"])
        if found:
            write("res.partner", [found[0]["id"]], vals)
            pid = found[0]["id"]
        else:
            pid = create("res.partner", dict(vals, name=name))
        print(f"  └ {name} / {func} @ {pref} (id={pid})")


# ------------------------------------------------------------------ products
# (코드, 이름, 원가, 공급사 ref, 리드타임(일), 최소재고, 최대재고, 현재고)
PRODUCTS = [
    ("PCB-100",  "메인 컨트롤 PCB",          85000, "SUP-01", 14,  30,  120,  12),
    ("SMPS-200", "SMPS 파워모듈",           100000, "SUP-01", 10,  20,   80,   5),
    ("SNS-310",  "근접센서 모듈",             42000, "SUP-01",  7,  50,  200, 180),
    ("ALU-400",  "알루미늄 프로파일 40x40",   18000, "SUP-02",  5, 100,  400, 260),
    ("STL-410",  "스테인리스 판재 1.2T",      55000, "SUP-02",  9,  40,  150,  22),
    ("BRG-500",  "정밀 볼베어링 6204",         9500, "SUP-06",  6, 200,  600, 200),
    ("GER-510",  "헬리컬 기어 M2",            76000, "SUP-03", 12,  30,  100,  64),
    ("CBL-600",  "하네스 케이블 2m",          12000, "SUP-04",  8, 150,  500,  90),
    ("CTG-700",  "세라믹 코팅제 5L",         145000, "SUP-05", 21,  10,   40,  31),
    ("PKG-800",  "완충 포장재 세트",            3200, "SUP-08",  4, 300, 1000, 240),
]
product = {}


def seed_products():
    print("\n[2/3] 품목 · 공급사정보 · 재주문규칙")
    for code, name, cost, sref, delay, mn, mx, _onhand in PRODUCTS:
        # Odoo 19: type='consu' + is_storable=True 가 '재고를 추적하는 물품'이다
        vals = {"type": "consu", "is_storable": True, "purchase_ok": True, "sale_ok": False,
                "standard_price": cost, "list_price": round(cost * 1.35),
                "categ_id": CATEG_GOODS, "uom_id": UOM_UNITS}
        found = search_read("product.product", [["default_code", "=", code]],
                            ["id", "product_tmpl_id"])
        if found:
            pid, tmpl = found[0]["id"], found[0]["product_tmpl_id"][0]
            write("product.product", [pid], vals)
        else:
            pid = create("product.product", dict(vals, name=name, default_code=code))
            tmpl = search_read("product.product", [["id", "=", pid]],
                               ["product_tmpl_id"])[0]["product_tmpl_id"][0]
        product[code] = pid

        si = search_read("product.supplierinfo",
                         [["product_tmpl_id", "=", tmpl], ["partner_id", "=", partner[sref]]], ["id"])
        sivals = {"price": cost, "delay": delay, "min_qty": 1}
        if si:
            write("product.supplierinfo", [si[0]["id"]], sivals)
        else:
            create("product.supplierinfo",
                   dict(sivals, product_tmpl_id=tmpl, partner_id=partner[sref]))

        # trigger='manual' — 'auto' 로 두면 Odoo 스케줄러가 실습 중에 멋대로 RFQ 를 만든다
        op = search_read("stock.warehouse.orderpoint", [["product_id", "=", pid]], ["id"])
        opvals = {"product_min_qty": mn, "product_max_qty": mx, "trigger": "manual"}
        if op:
            write("stock.warehouse.orderpoint", [op[0]["id"]], opvals)
        else:
            create("stock.warehouse.orderpoint",
                   dict(opvals, product_id=pid, warehouse_id=WH_ID, location_id=STOCK_LOC))
        print(f"  {code:9s} {name:22s} min {mn:>4} / max {mx:>4} / 공급사 {sref} / 리드타임 {delay}일")


# ----------------------------------------------------------------- purchases
# (공급사 ref, 발주일, [(품목코드, 수량)], 확정?, 입고완료?)
ORDERS = [
    ("SUP-01", "2026-05-11", [("PCB-100", 60), ("SNS-310", 100)], True,  True),
    ("SUP-02", "2026-05-15", [("ALU-400", 300)],                  True,  True),
    ("SUP-04", "2026-05-22", [("CBL-600", 400)],                  True,  True),
    ("SUP-01", "2026-06-02", [("SMPS-200", 50)],                  True,  True),
    ("SUP-06", "2026-06-05", [("BRG-500", 500)],                  True,  True),
    ("SUP-03", "2026-06-09", [("GER-510", 40)],                   True,  True),
    ("SUP-02", "2026-06-16", [("STL-410", 80)],                   True,  True),
    ("SUP-05", "2026-06-23", [("CTG-700", 20)],                   True,  True),
    ("SUP-01", "2026-07-01", [("SNS-310", 150)],                  True,  True),
    ("SUP-08", "2026-07-06", [("PKG-800", 800)],                  True,  True),
    ("SUP-03", "2026-07-13", [("GER-510", 25)],                   True,  False),  # 미착
    ("SUP-02", "2026-07-20", [("ALU-400", 150), ("STL-410", 30)], True,  False),  # 미착
    ("SUP-01", "2026-07-24", [("PCB-100", 40)],                   False, False),  # RFQ(draft)
    ("SUP-04", "2026-07-28", [("CBL-600", 200)],                  False, False),  # RFQ(draft)
]
COST = {c: p for c, _n, p, *_ in PRODUCTS}
PNAME = {c: n for c, n, *_ in PRODUCTS}


def receive(order_id, label):
    for po in search_read("purchase.order", [["id", "=", order_id]], ["picking_ids"]):
        for pick_id in po["picking_ids"]:
            pick = search_read("stock.picking", [["id", "=", pick_id]], ["state", "move_ids"])[0]
            if pick["state"] in ("done", "cancel"):
                continue
            for m in search_read("stock.move", [["id", "in", pick["move_ids"]]], ["product_uom_qty"]):
                write("stock.move", [m["id"]], {"quantity": m["product_uom_qty"], "picked": True})
            try:
                call("stock.picking", "button_validate", [pick_id])
            except Exception as e:
                print(f"      ! 입고 실패 {label}: {str(e)[-160:]}")


def seed_orders():
    print("\n[3/3] 발주")
    for sref, date, lines, confirm, received in ORDERS:
        origin = f"WORKSHOP/{sref}/{date}"
        if search_read("purchase.order", [["origin", "=", origin]], ["id"]):
            print(f"  (이미 있음) {origin}")
            continue
        oid = create("purchase.order", {"partner_id": partner[sref],
                                        "date_order": f"{date} 01:00:00", "origin": origin})
        for code, qty in lines:
            create("purchase.order.line", {
                "order_id": oid, "product_id": product[code],
                "name": f"[{code}] {PNAME[code]}", "product_qty": qty,
                "price_unit": COST[code], "date_planned": f"{date} 01:00:00",
                # 세금을 비워야 합계가 딱 떨어져 실습 중 숫자 확인이 쉽다
                "tax_ids": [(5,)],
            })
        if confirm:
            call("purchase.order", "button_confirm", [oid])
        rec = search_read("purchase.order", [["id", "=", oid]],
                          ["name", "state", "amount_total"])[0]
        if received:
            receive(oid, rec["name"])
        print(f"  {rec['name']}  {sref}  {date}  {rec['state']:8s} "
              f"{rec['amount_total']:>12,.0f}원" + ("  (입고완료)" if received else ""))


def set_stock_levels():
    print("\n[마무리] 재고실사로 현재고 확정")
    for code, _name, _c, _s, _d, mn, _mx, onhand in PRODUCTS:
        pid = product[code]
        q = search_read("stock.quant",
                        [["product_id", "=", pid], ["location_id", "=", STOCK_LOC]], ["id"])
        qid = q[0]["id"] if q else create("stock.quant",
                                          {"product_id": pid, "location_id": STOCK_LOC})
        write("stock.quant", [qid], {"inventory_quantity": onhand})
        call_void("stock.quant", "action_apply_inventory", [qid])
        got = search_read("product.product", [["id", "=", pid]], ["qty_available"])[0]
        flag = "부족" if got["qty_available"] < mn else ("경계" if got["qty_available"] == mn else "정상")
        ok = "OK" if abs(got["qty_available"] - onhand) < 0.01 else "!! 목표와 불일치"
        print(f"  {code:9s} 현재고 {got['qty_available']:>6.0f} / min {mn:>4}  {flag:4s} {ok}")


if __name__ == "__main__":
    seed_partners()
    seed_products()
    seed_orders()
    set_stock_levels()
    print("\n시딩 완료. 워크북 '0. 준비' 절의 확인 프롬프트로 검증하세요.")
