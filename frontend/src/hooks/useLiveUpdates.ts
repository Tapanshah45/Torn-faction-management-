import { useEffect, useState } from 'react';

interface ChainData {
    current?: number | string;
    timer?: string;
    time_remaining?: number;
    [key: string]: unknown;
}

interface ChainBreakEvent {
    chain_id: string;
    reason: string;
    chain_broken: boolean;
    time_remaining?: number | null;
    last_hitter_name?: string | null;
}

interface ReliabilityRefreshMessage {
    updated: number;
}

export function useLiveUpdates() {
    const [chainData, setChainData] = useState<ChainData | null>(null);
    const [chainBreakEvent, setChainBreakEvent] = useState<ChainBreakEvent | null>(null);
    const [reliabilityRefresh, setReliabilityRefresh] = useState<ReliabilityRefreshMessage | null>(null);
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
            } else if (message.type === 'chain_break') {
                setChainBreakEvent(message.payload);
            } else if (message.type === 'reliability_refresh') {
                setReliabilityRefresh(message.payload);
            }
        };

        return () => {
            socket.close();
        };
    }, []);

    return { chainData, chainBreakEvent, reliabilityRefresh, isConnected };
}
