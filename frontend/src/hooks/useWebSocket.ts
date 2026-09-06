import { useState, useEffect } from 'react';
import { WSMessage } from '../types';

export function useWebSocket(experimentId: string | null) {
  const [messages, setMessages] = useState<WSMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);

  useEffect(() => {
    if (!experimentId) return;

    let ws: WebSocket;
    let reconnectTimer: NodeJS.Timeout;

    const connect = () => {
      ws = new WebSocket(`ws://localhost:8000/ws/experiments/${experimentId}`);

      ws.onopen = () => setIsConnected(true);
      
      ws.onmessage = (event) => {
        try {
          const msg: WSMessage = JSON.parse(event.data);
          setMessages(prev => [...prev, msg]);
          setLastMessage(msg);
        } catch (e) {
          console.error("Invalid WS message", e);
        }
      };

      ws.onclose = () => {
        setIsConnected(false);
        reconnectTimer = setTimeout(connect, 3000);
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, [experimentId]);

  return { messages, isConnected, lastMessage };
}
