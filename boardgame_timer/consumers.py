import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_slug = self.scope['url_route']['kwargs']['session_slug']
        self.session_group_name = f'session_{self.session_slug}'

        # Join room group
        await self.channel_layer.group_add(
            self.session_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.session_group_name,
            self.channel_name
        )

    # Receive message from WebSocket (optional for now)
    # async def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json['message']
    #     await self.channel_layer.group_send(
    #         self.session_group_name,
    #         {
    #             'type': 'chat_message', # Or some other type for client-sent messages
    #             'message': message
    #         }
    #     )

    # Method to send game state to the WebSocket group
    async def send_game_state(self, event):
        state = event['state']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(state))
