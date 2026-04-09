import { useEffect, useState } from 'react';

interface ChainData {
    current?: number;
    timer?: string;
    [key: string]: any;
}

export function useLiveUpdates() {
    const [chainData, setChainData] = useState<ChainData | null>(null);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';
        const url = wsUrl.endsWith('/') ? `${wsUrl}live/` : `${wsUrl}/live/`;

        const socket = new WebSocket(url);

        socket.onopen = () => setIsConnected(true);
        socket.onclose = () => setIsConnected(false);

        socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            if (message.type === 'chain') {
                setChainData(message.payload);
            }
        };

        return () => {
            socket.close();
        };
    }, []);

    return { chainData, isConnected };
}
