from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
)
import pika
import ssl
from .models import Enqueue
from .logger import Logger


async def serve(rabbitmq_host: str, port: int, username: str, password: str) -> None:
    """Run the RabbitMQ MCP server.
    """
    server = Server("mcp-rabbitmq")
    logger = Logger("server.log")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="enqueue",
                description="""Enqueue a message to a queue hosted on RabbitMQ""",
                inputSchema=Enqueue.model_json_schema(),
            )
        ]

    @server.call_tool()
    async def call_tool(
        name: str,
        arguments: dict
    ) -> list[TextContent]:
        if name == "enqueue":
            logger.log("[Debug] In enqueue")
            message = arguments["message"]
            queue = arguments["queue"]
            logger.log(f"[Debug] msg: {message} queue:{queue}")
            # Send to RabbitMQ host
            try:
                logger.log(f"[Debug] username: {username} password: {password}")
                logger.log(f"[Debug] host: {rabbitmq_host} port: {port}")
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                ssl_context.set_ciphers('ECDHE+AESGCM:!ECDSA')
                url = f"amqps://{username}:{password}@{rabbitmq_host}:{port}"
                parameters = pika.URLParameters(url)
                parameters.ssl_options = pika.SSLOptions(context=ssl_context)
                connection = pika.BlockingConnection(parameters)
                channel = connection.channel()
                channel.queue_declare(queue)
                channel.basic_publish(exchange="", routing_key=queue, body=message)
                return [TextContent(type="text", text=str("suceeded"))]
            except Exception as e:
                logger.log(f"[ERROR] {e}")
                return [TextContent(type="text", text=str("failed"))]
        raise ValueError(f"Tool not found: {name}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
