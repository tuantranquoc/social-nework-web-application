import React, { useEffect, useState, useRef } from 'react';

export default function AppWs({ parentCallback }, {messageObject}) {
    const [isPaused, setPause] = useState(false);
    const [messageList, setMessageList] = useState([]);
    const ws = useRef(null);
    console.log("mess-obj-child-1", messageObject);
    useEffect(() => {
        ws.current = new WebSocket("ws://127.0.0.1:8000/ws/chat/aa/");
        ws.current.onopen = () => console.log("ws opened");
        ws.current.onclose = () => console.log("ws closed");
        console.log("mess-obj-child-2", messageObject);

        return () => {
            ws.current.close();
        };
    }, []);



    useEffect(() => {
        if (!ws.current) return;
        console.log("mess-obj-child-3", messageObject);
        ws.current.onmessage = e => {
            if (isPaused) return;
            const message = JSON.parse(e.data);
            if (message.length !== 0) {
                setMessageList(message);
                console.log("pass leg");
                parentCallback(message.messages);
            }
            console.log("e", message);
        };
    }, [isPaused]);

    return (<div>

    </div>)
}