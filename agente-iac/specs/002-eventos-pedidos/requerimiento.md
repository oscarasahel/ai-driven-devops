Queremos recibir eventos de pedidos por un tema SNS y procesarlos de forma asíncrona.
Los eventos deben llegar a una cola SQS; si un mensaje falla 3 veces, debe ir a una cola de mensajes fallidos que conservemos 14 días.
El estado de cada pedido se guarda en una tabla DynamoDB con clave order_id, sin capacidad aprovisionada fija (pago por uso).
Los registros de estado expiran solos a los 90 días y la tabla debe poder recuperarse a un punto en el tiempo.
Las colas deben ir cifradas. Región us-east-1, etiquetas project, env y owner.
