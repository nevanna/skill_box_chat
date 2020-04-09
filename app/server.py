import asyncio

class ServerProtocol(asyncio.Protocol):
	login : str = None
	server : 'Server'
	
	def __init__(self, server: 'Server'):
		self.server = server
	
	def data_received(self, data:bytes):
		print(data)
		decoded = data.decode()
		if self.login is not None:
			self.send_message(decoded)
			self.manage_history(self.login + ": "+ decoded + "\n")
		else:
			if decoded.startswith("login:"):
				nick_name  = decoded.replace("login:", "").replace("\r\n", "")
				list_name = []
				for person in self.server.clients:
					list_name.append(person.login)
				if nick_name in list_name:
					self.transport.write(f"{nick_name} has been already taken, try another one\n".encode())
					self.transport.close()
				else:
					self.login = nick_name
					self.transport.write(f"Hello, {self.login}!\n\n".encode())
					self.send_history()
			else:
				self.transport.write("wrong login\n\n".encode())


	def connection_made(self, transport):
		self.server.clients.append(self)
		self.transport = transport
		print("new client")

	def connection_lost(self, exception):
		self.server.clients.remove(self)
		print("client went out")

	def send_message(self, content: str):
		message = f"{self.login}: {content}"
		for user in self.server.clients:
			user.transport.write(message.encode())

	def send_history(self):
		history_msg = ""
		for row in self.server.history:
			history_msg+= row
		self.transport.write(f"You missed {len(self.server.history)} messages\n\n{history_msg}\n\n".encode())

	def manage_history(self, msg):
		if len(self.server.history) >= 10:
			self.server.history = self.server.history[1::]
		self.server.history.append(msg)


class Server:
	clients : list
	history = []

	HISTORY_DEEP = int(10)

	def __init__(self):
		self.clients = []
	
	def build_protocol(self):
		return ServerProtocol(self)

	async def start(self):
		loop = asyncio.get_running_loop()
		corutine = await loop.create_server(
			self.build_protocol,
			'127.0.0.1',
			8888
		)
		print("server is running")
		await corutine.serve_forever()
	
process = Server()
try:
	asyncio.run(process.start())
except KeyboardInterrupt:
	print("Server is stopped")
