from database import get_db

DESCONTO_FAIXA_ALTA = 0.10
DESCONTO_FAIXA_MEDIA = 0.05
DESCONTO_FAIXA_BAIXA = 0.02
LIMITE_FAIXA_ALTA = 10000
LIMITE_FAIXA_MEDIA = 5000
LIMITE_FAIXA_BAIXA = 1000

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def find_by_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               ip.produto_id, ip.quantidade, ip.preco_unitario, pr.nome as produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
        WHERE p.usuario_id = ?
        ORDER BY p.id
    """, (usuario_id,))
    return _agrupa_pedidos(cursor.fetchall())


def find_all():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               ip.produto_id, ip.quantidade, ip.preco_unitario, pr.nome as produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
        ORDER BY p.id
    """)
    return _agrupa_pedidos(cursor.fetchall())


def _agrupa_pedidos(rows):
    pedidos = {}
    for row in rows:
        row = dict(row)
        pid = row['id']
        if pid not in pedidos:
            pedidos[pid] = {
                'id': row['id'],
                'usuario_id': row['usuario_id'],
                'status': row['status'],
                'total': row['total'],
                'criado_em': row['criado_em'],
                'itens': []
            }
        if row['produto_id']:
            pedidos[pid]['itens'].append({
                'produto_id': row['produto_id'],
                'produto_nome': row['produto_nome'] or 'Desconhecido',
                'quantidade': row['quantidade'],
                'preco_unitario': row['preco_unitario']
            })
    return list(pedidos.values())


def create(usuario_id, itens):
    db = get_db()
    cursor = db.cursor()

    total = 0
    for item in itens:
        cursor.execute("SELECT preco, estoque, nome FROM produtos WHERE id = ?", (item["produto_id"],))
        produto = cursor.fetchone()
        if produto is None:
            return {"erro": f"Produto {item['produto_id']} não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}
        total += produto["preco"] * item["quantidade"]

    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total)
    )
    pedido_id = cursor.lastrowid

    for item in itens:
        cursor.execute("SELECT preco FROM produtos WHERE id = ?", (item["produto_id"],))
        produto = cursor.fetchone()
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"])
        )
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"])
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def update_status(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
    return True


def relatorio_vendas():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
    aprovados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
    cancelados = cursor.fetchone()[0]

    if faturamento > LIMITE_FAIXA_ALTA:
        desconto = faturamento * DESCONTO_FAIXA_ALTA
    elif faturamento > LIMITE_FAIXA_MEDIA:
        desconto = faturamento * DESCONTO_FAIXA_MEDIA
    elif faturamento > LIMITE_FAIXA_BAIXA:
        desconto = faturamento * DESCONTO_FAIXA_BAIXA
    else:
        desconto = 0

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0
    }
