"""HTTP websocket server functional tests"""

import asyncio
import pytest
from aiohttp import web


@pytest.mark.run_loop
def test_websocket_json(create_app_and_client):
    @asyncio.coroutine
    def handler(request):
        ws = web.WebSocketResponse()
        yield from ws.prepare(request)
        msg = yield from ws.receive()

        msg_json = msg.json()
        answer = msg_json['test']
        ws.send_str(answer)

        yield from ws.close()
        return ws

    app, client = yield from create_app_and_client()
    app.router.add_route('GET', '/', handler)

    ws = yield from client.ws_connect('/')
    expected_value = 'value'
    payload = '{"test": "%s"}' % expected_value
    ws.send_str(payload)

    resp = yield from ws.receive()
    assert resp.data == expected_value


@pytest.mark.run_loop
def test_websocket_json_invalid_message(create_app_and_client):
    @asyncio.coroutine
    def handler(request):
        ws = web.WebSocketResponse()
        yield from ws.prepare(request)
        try:
            yield from ws.receive_json()
        except ValueError:
            ws.send_str('ValueError was raised')
        else:
            raise Exception('No Exception')
        finally:
            yield from ws.close()
        return ws

    app, client = yield from create_app_and_client()
    app.router.add_route('GET', '/', handler)

    ws = yield from client.ws_connect('/')
    payload = 'NOT A VALID JSON STRING'
    ws.send_str(payload)

    data = yield from ws.receive_str()
    assert 'ValueError was raised' in data


@pytest.mark.run_loop
def test_websocket_send_json(create_app_and_client):
    @asyncio.coroutine
    def handler(request):
        ws = web.WebSocketResponse()
        yield from ws.prepare(request)

        data = yield from ws.receive_json()
        ws.send_json(data)

        yield from ws.close()
        return ws

    app, client = yield from create_app_and_client()
    app.router.add_route('GET', '/', handler)

    ws = yield from client.ws_connect('/')
    expected_value = 'value'
    ws.send_json({'test': expected_value})

    data = yield from ws.receive_json()
    assert data['test'] == expected_value


@pytest.mark.run_loop
def test_websocket_receive_json(create_app_and_client):
    @asyncio.coroutine
    def handler(request):
        ws = web.WebSocketResponse()
        yield from ws.prepare(request)

        data = yield from ws.receive_json()
        answer = data['test']
        ws.send_str(answer)

        yield from ws.close()
        return ws

    app, client = yield from create_app_and_client()
    app.router.add_route('GET', '/', handler)

    ws = yield from client.ws_connect('/')
    expected_value = 'value'
    payload = '{"test": "%s"}' % expected_value
    ws.send_str(payload)

    resp = yield from ws.receive()
    assert resp.data == expected_value
