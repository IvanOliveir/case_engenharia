with transacions AS (
	SELECT account_id , amount, 'Transferencia' AS transaction_type, dt FROM bankslip
	UNION ALL
	SELECT account_id , amount, 'Pix Send' AS transaction_type, dt FROM pix_send
	UNION ALL
	SELECT account_id , amount, 'Pix Received' AS transaction_type, dt FROM pix_received
	UNION ALL
	SELECT account_id_source AS account_id , amount, 'Peer-to-peer' AS transaction_type, dt FROM p2p_tef
)


SELECT
	c.customer_id,
	a.account_id,
	c.name,
	a.dt AS date,
	t.transaction_type,
	AVG(t.amount) AS mean_value

FROM account a
	JOIN customer c
	a.customer_id = c.customer_id
	JOIN transactions t
	a.account_id = t.account_id

GROUP BY
	a.customer_id, a.dt, t.transaction_type