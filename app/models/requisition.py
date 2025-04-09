class Requisition:
    def __init__(self, requisition_id, description, quantity, unit_price):
        """
        Modèle pour une réquisition avec les informations principales.

        :param requisition_id: Identifiant unique de la réquisition.
        :param description: Description de la réquisition (par exemple, article demandé).
        :param quantity: Quantité de l'article demandé.
        :param unit_price: Prix unitaire de l'article demandé.
        """
        self.requisition_id = requisition_id
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
    
    def total_price(self):
        """
        Calculer le prix total pour cette réquisition.

        :return: Le prix total (quantity * unit_price).
        """
        return self.quantity * self.unit_price
    
    def to_dict(self):
        """
        Convertir l'objet en dictionnaire pour exportation.

        :return: Un dictionnaire avec les informations de la réquisition.
        """
        return {
            "requisition_id": self.requisition_id,
            "description": self.description,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_price": self.total_price()
        }
