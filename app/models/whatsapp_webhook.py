from pydantic import BaseModel, Field
from typing import List, Optional

class Text(BaseModel):
    """
    Modelo para el contenido de texto en el webhook de WhatsApp
    Atributos:
        body (str): El cuerpo del mensaje de texto.
    """
    body: str

class ButtonReply(BaseModel):
    """
    Modelo para respuestas de botones interactivos
    Atributos:
        id (str): ID del botón seleccionado.
        title (str): Título del botón seleccionado.
    """
    id: str
    title: str

class ListReply(BaseModel):
    """
    Modelo para respuestas de listas interactivas
    Atributos:
        id (str): ID de la opción seleccionada.
        title (str): Título de la opción seleccionada.
        description (Optional[str]): Descripción de la opción seleccionada.
    """
    id: str
    title: str
    description: Optional[str] = None

class Interactive(BaseModel):
    """
    Modelo para mensajes interactivos
    Atributos:
        type (str): Tipo de interacción ("button_reply" o "list_reply").
        button_reply (Optional[ButtonReply]): Respuesta de botón si aplica.
        list_reply (Optional[ListReply]): Respuesta de lista si aplica.
    """
    type: str
    button_reply: Optional[ButtonReply] = None
    list_reply: Optional[ListReply] = None

class Message(BaseModel):
    """
    Modelo para los mensajes en el webhook de WhatsApp
    Atributos:
        from_ (str): Número de teléfono del remitente.
        id (str): ID del mensaje.
        timestamp (str): Marca de tiempo del mensaje.
        type (str): Tipo de mensaje (por ejemplo, "text", "interactive").
        text (Optional[Text]): Contenido del mensaje, si es de tipo texto.
        interactive (Optional[Interactive]): Contenido interactivo, si es de tipo interactive.
    """
    from_: str = Field(..., alias="from")  # "from" es palabra reservada en Python
    id: str
    timestamp: str
    type: str
    text: Optional[Text] = None
    interactive: Optional[Interactive] = None

class Metadata(BaseModel):
    """
    Modelo para los metadatos en el webhook de WhatsApp
    Atributos:
        display_phone_number (str): Número de teléfono que muestra el mensaje.
        phone_number_id (str): ID del número de teléfono.
    """
    display_phone_number: str
    phone_number_id: str

class Profile(BaseModel):
    """
    Modelo para el perfil en el webhook de WhatsApp
    Atributos:
        name (str): Nombre del perfil.
    """
    name: str

class Contact(BaseModel):
    """
    Modelo para el contacto en el webhook de WhatsApp
    Atributos:
        profile (Profile): Perfil del contacto.
        wa_id (str): ID de WhatsApp del contacto.
    """
    profile: Profile
    wa_id: str

class Value(BaseModel):
    """
    Modelo para el valor en el webhook de WhatsApp
    Atributos:
        messaging_product (str): Producto de mensajería, generalmente "whatsapp".
        metadata (Metadata): Metadatos asociados al mensaje.
        contacts (Optional[List[Contact]]): Lista opcional de contactos involucrados en el mensaje.
        messages (Optional[List[Message]]): Lista opcional de mensajes recibidos.
    """
    messaging_product: str
    metadata: Metadata
    contacts: Optional[List[Contact]] = [] 
    messages: Optional[List[Message]] = []

class Change(BaseModel):
    """
    Modelo para los cambios en el webhook de WhatsApp
    Atributos:
        value (Value): El valor que contiene los detalles del cambio.
        field (str): El campo que ha cambiado.
    """
    value: Value
    field: str

class Entry(BaseModel):
    """
    Modelo para las entradas del webhook de WhatsApp
    Atributos:
        id (str): ID de la entrada.
        changes (List[Change]): Lista de cambios asociados a la entrada.
    """
    id: str
    changes: List[Change]

class WebhookPayload(BaseModel):
    """
    Modelo para el payload del webhook de WhatsApp
    
    Atributos:
        object (str): Tipo de objeto, generalmente "whatsapp_business_account".
        entry (List[Entry]): Lista de entradas que contienen los cambios y mensajes.
    """
    object: str
    entry: List[Entry]

    def get_mensaje(self) -> Message:
        """
        Método para obtener el primer mensaje del payload.
        
        Retorna:
            Message: El primer mensaje encontrado en el payload.
        """
        if len(self.entry) > 0 and len(self.entry[0].changes) > 0 and self.entry[0].changes[0].value.messages:
            return self.entry[0].changes[0].value.messages[0]
        return None
