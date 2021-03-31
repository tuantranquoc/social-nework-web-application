import React from 'react';
import { useEffect, useState, useRef } from 'react';
import SidePanel from './side_panel/SidePanel';
import AppWs from '../websocket_1'

export default function Chat() {

    const [newMessage, setMessage] = useState(null);
    const [messageObject, setMessageObject] = useState(null);
    const [messageList, setMessageList] = useState([]);
    const ws = useRef(null);
    const newMessageHandler = event => {
        if (newMessage !== null) {
            setMessage(null);
        }
        event.preventDefault();
        setMessage(event.target.value);


    };
    var mess = {
        "author": "admin",
        "content": "hello world",
        "timestamp": "new_message"
    }

    useEffect(() => {
        ws.current = new WebSocket("ws://127.0.0.1:8000/ws/chat/aa/");
        ws.current.onopen = () => {
            console.log("ws opened")
        };
        ws.current.onclose = () => console.log("ws closed");
        return () => {
            ws.current.close();
        };
    }, []);



    useEffect(() => {
        if (!ws.current) return;
        if (messageObject !== null) {
            ws.current.send(JSON.stringify(messageObject));
            setMessageObject(null);
        }
        ws.current.onmessage = e => {
            const message = JSON.parse(e.data);
            if (message.messages !== undefined) {
                setMessageList(message.messages);
            }
            if (message.command !== undefined) {
                if (message.command === "new_message") {
                    var Object = {
                        "author": message.message.author,
                        "content": message.message.content,
                    }
                    setMessageList(messageList => [...messageList, Object]);
                }
            }
        };
    });

    const submitMessage = () => {
        const messageInput = document.getElementById("chat-message-input");
        messageInput.value = "";
        if (newMessage !== null) {
            var Object = {
                "from": "tuantran",
                "message": newMessage,
                'command': 'new_message'
            }
            setMessageObject(Object);
        }
    };

    var renderMessage = (message, author) => {
        const currentUser = "admin1";
        var className = author === "tuantran" ? "sent" : "replies";
        return (
            className ?
                <div>
                    <li className={className}>
                        <img src="http://emilcarlsson.se/assets/mikeross.png" alt="" />
                        <p>
                            {message}
                        </p>
                    </li>
                </div> : <div>
                    <li className="sent">
                        <img src="http://emilcarlsson.se/assets/mikeross.png" alt="" />
                        <p>
                            ajsdasd
                    </p>
                    </li>
                </div>
        )

    }
    return (
        <div id="frame">
            {/* <AppWs parentCallback={callback} messageObject={messageObject !== undefined ? messageObject : "hello world"} /> */}
            <SidePanel />
            <div className="content">
                <div className="contact-profile">
                    <img src="http://emilcarlsson.se/assets/harveyspecter.png" alt="" />

                    <div className="social-media">
                        <i className="fa fa-facebook" aria-hidden="true"></i>
                        <i className="fa fa-twitter" aria-hidden="true"></i>
                        <i className="fa fa-instagram" aria-hidden="true"></i>
                    </div>
                </div>
                <div className="messages">
                    <ul id="chat-log">
                        {messageList !== undefined ? messageList.map(message => renderMessage(message.content, message.author)) : null}
                    </ul>
                </div>
                <div className="message-input">
                    <div className="wrap">
                        <input onChange={newMessageHandler} id="chat-message-input" type="text" placeholder="Write your message..." />
                        <i className="fa fa-paperclip attachment" aria-hidden="true"></i>
                        <button onClick={submitMessage} id="chat-message-submit" className="submit"><i className="fa fa-paper-plane"
                            aria-hidden="true"></i></button>
                    </div>
                </div>
            </div>
        </div>
    )
}

