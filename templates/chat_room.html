<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat — Vendly</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400..900&display=swap" rel="stylesheet">
    <style>
        :root {
            --navy: #0D1B2A;
            --orange: #FF6B35;
            --white: #ffffff;
            --gray-50: #f8f9fb;
            --text-muted: #6b7b8d;
            --border: #e8ecf0;
            --radius: 14px;
            --radius-sm: 10px;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--gray-50);
            color: var(--navy);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .navbar {
            background: var(--navy);
            padding: 0.8rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            z-index: 100;
        }
        .back-btn { color: white; text-decoration: none; font-size: 1.2rem; }
        .chat-header-info { flex: 1; }
        .chat-header-info .name { color: white; font-weight: 600; font-size: 0.9rem; }
        .chat-header-info .item { color: rgba(255,255,255,0.6); font-size: 0.75rem; }
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        .message {
            max-width: 75%;
            padding: 0.7rem 1rem;
            border-radius: 16px;
            font-size: 0.9rem;
            line-height: 1.4;
            word-wrap: break-word;
        }
        .message-sent {
            align-self: flex-end;
            background: var(--navy);
            color: white;
            border-bottom-right-radius: 4px;
        }
        .message-received {
            align-self: flex-start;
            background: white;
            border: 1px solid var(--border);
            border-bottom-left-radius: 4px;
        }
        .message-time { font-size: 0.65rem; opacity: 0.6; margin-top: 4px; text-align: right; }
        .system-message {
            align-self: center;
            font-size: 0.75rem;
            color: var(--text-muted);
            background: #f0f2f5;
            padding: 0.4rem 1rem;
            border-radius: 20px;
        }
        .offer-card {
            align-self: center;
            background: #fff8f0;
            border: 1px solid var(--orange);
            border-radius: var(--radius-sm);
            padding: 1rem;
            width: 90%;
            max-width: 350px;
        }
        .offer-card .offer-amount { font-size: 1.3rem; font-weight: 800; color: var(--orange); }
        .offer-card .offer-label { font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
        .offer-actions { display: flex; gap: 0.5rem; margin-top: 0.75rem; }
        .btn-accept {
            background: #22c55e; color: white; border: none;
            padding: 0.5rem 1rem; border-radius: 20px;
            font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.8rem; cursor: pointer;
        }
        .btn-reject {
            background: #ef4444; color: white; border: none;
            padding: 0.5rem 1rem; border-radius: 20px;
            font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.8rem; cursor: pointer;
        }
        .btn-counter {
            background: white; color: var(--navy); border: 1px solid var(--border);
            padding: 0.5rem 1rem; border-radius: 20px;
            font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.8rem; cursor: pointer;
        }
        .offer-status { text-align: center; font-size: 0.8rem; font-weight: 600; margin-top: 0.5rem; }
        .offer-accepted { color: #22c55e; }
        .offer-rejected { color: #ef4444; }
        .chat-input-area {
            display: flex; gap: 0.5rem; padding: 0.75rem 1rem;
            background: white; border-top: 1px solid var(--border);
        }
        .chat-input-area input {
            flex: 1; padding: 0.7rem 1rem; border: 1px solid var(--border);
            border-radius: 24px; font-family: 'Inter', sans-serif; font-size: 0.9rem; outline: none;
        }
        .chat-input-area input:focus { border-color: var(--orange); }
        .btn-send {
            background: var(--orange); color: white; border: none;
            padding: 0.7rem 1.2rem; border-radius: 24px;
            font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.85rem; cursor: pointer;
        }
        .btn-offer {
            background: white; color: var(--orange); border: 1px solid var(--orange);
            padding: 0.7rem 1rem; border-radius: 24px;
            font-family: 'Inter', sans-serif; font-weight: 600; font-size: 0.85rem; cursor: pointer;
        }
        .empty-chat { text-align: center; padding: 3rem; color: var(--text-muted); }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/chat" class="back-btn">←</a>
        <div class="chat-header-info">
            <div class="name" id="chat-name">Loading...</div>
            <div class="item" id="chat-item">...</div>
        </div>
    </nav>

    <div class="messages-container" id="messages">
        <div class="empty-chat" id="chat-loader">💬<br><span style="font-size:0.85rem;">Loading conversation...</span></div>
    </div>

    <div class="chat-input-area">
        <input type="text" id="message-input" placeholder="Type a message..." onkeypress="if(event.key==='Enter')sendMessage()">
        <button class="btn-offer" onclick="makeOffer()">💰</button>
        <button class="btn-send" onclick="sendMessage()">Send</button>
    </div>

    <script>
        const API_BASE = '';
        const roomId = window.location.pathname.split('/')[2];
        const urlParams = new URLSearchParams(window.location.search);
        const prefillOffer = urlParams.get('offer');

        function getToken() { return localStorage.getItem('vendly_token'); }
        if (!getToken()) { window.location.href = '/login'; }

        let currentUserId = null;
        let listingId = null;
        let lastMessageId = 0;
        let pollingInterval = null;
        let isLoading = false;

        async function init() {
            const token = getToken();
            try {
                // Run both requests in parallel for speed
                const [meRes, roomsRes] = await Promise.all([
                    fetch(`${API_BASE}/api/auth/me`, { headers: { 'Authorization': `Bearer ${token}` } }),
                    fetch(`${API_BASE}/api/chat/rooms`, { headers: { 'Authorization': `Bearer ${token}` } })
                ]);
                const meData = await meRes.json();
                currentUserId = meData.user.id;
                const rooms = await roomsRes.json();
                const room = rooms.find(r => r.room_id == roomId);
                if (room) {
                    document.getElementById('chat-name').textContent = room.other_user.full_name;
                    document.getElementById('chat-item').textContent = `${room.listing.title} · ₦${room.listing.price.toLocaleString()}`;
                    listingId = room.listing.id;
                }
            } catch (e) {}

            await loadMessages();
            pollingInterval = setInterval(loadMessages, 3000);

            if (prefillOffer && listingId) {
                setTimeout(() => sendOfferViaApi(prefillOffer), 800);
                window.history.replaceState({}, document.title, `/chat/${roomId}`);
            }
        }

        async function loadMessages() {
            if (isLoading) return;
            isLoading = true;
            try {
                const token = getToken();
                const res = await fetch(`${API_BASE}/api/chat/rooms/${roomId}/messages`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                const messages = await res.json();
                const container = document.getElementById('messages');
                const loader = document.getElementById('chat-loader');
                const newMessages = messages.filter(m => m.id > lastMessageId);

                if (messages.length > 0 && loader) {
                    loader.style.display = 'none';
                }

                if (newMessages.length > 0) {
                    newMessages.forEach(m => {
                        appendMessage(m);
                        lastMessageId = Math.max(lastMessageId, m.id);
                    });
                    scrollToBottom();
                }
            } catch (err) {
                console.error('Polling error:', err);
            }
            isLoading = false;
        }

        function appendMessage(msg) {
            const container = document.getElementById('messages');
            if (document.getElementById(`msg-${msg.id}`)) return;

            const isMine = msg.sender_id == currentUserId;
            const div = document.createElement('div');
            div.id = `msg-${msg.id}`;

            if (msg.type === 'offer' || msg.type === 'counter_offer') {
                div.className = 'offer-card';
                const offerData = msg.offer || {};
                const offerId = offerData.id;
                const status = offerData.status || 'pending';

                div.innerHTML = `
                    <div class="offer-label">${msg.type === 'counter_offer' ? '🔄 Counter Offer' : '💰 New Offer'}</div>
                    <div class="offer-amount">${msg.content}</div>
                    ${status === 'pending' && !isMine ? `
                        <div class="offer-actions" id="offer-actions-${offerId}">
                            <button class="btn-accept" onclick="respondOffer(${offerId},'accept')">✓ Accept</button>
                            <button class="btn-reject" onclick="respondOffer(${offerId},'reject')">✕ Reject</button>
                            <button class="btn-counter" onclick="counterOffer(${offerId})">↩ Counter</button>
                        </div>
                    ` : `
                        <div class="offer-status ${status === 'accepted' ? 'offer-accepted' : status === 'rejected' ? 'offer-rejected' : ''}">
                            ${status === 'accepted' ? '✅ Accepted' : status === 'rejected' ? '❌ Rejected' : status === 'countered' ? '🔄 Countered' : '⏳ Pending'}
                        </div>
                    `}
                    <div class="message-time">${new Date(msg.created_at).toLocaleTimeString()}</div>
                `;
            } else if (msg.type === 'accept' || msg.type === 'reject') {
                div.className = 'offer-card';
                div.innerHTML = `
                    <div class="offer-status ${msg.type === 'accept' ? 'offer-accepted' : 'offer-rejected'}">
                        ${msg.content}
                    </div>
                    <div class="message-time">${new Date(msg.created_at).toLocaleTimeString()}</div>
                `;
            } else {
                div.className = `message ${isMine ? 'message-sent' : 'message-received'}`;
                div.innerHTML = `
                    ${escapeHTML(msg.content)}
                    <div class="message-time">${new Date(msg.created_at).toLocaleTimeString()}</div>
                `;
            }

            container.appendChild(div);
        }

        function escapeHTML(str) {
            const d = document.createElement('div');
            d.textContent = str;
            return d.innerHTML;
        }

        function scrollToBottom() {
            const container = document.getElementById('messages');
            setTimeout(() => {
                container.scrollTop = container.scrollHeight;
            }, 100);
        }

        async function sendMessage() {
            const input = document.getElementById('message-input');
            const content = input.value.trim();
            if (!content) return;

            input.value = '';
            input.disabled = true;

            try {
                const token = getToken();
                const res = await fetch(`${API_BASE}/api/chat/rooms/${roomId}/send`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ content })
                });
                if (res.ok) {
                    const msg = await res.json();
                    // Instant display - add the message immediately
                    appendMessage(msg);
                    lastMessageId = Math.max(lastMessageId, msg.id);
                    scrollToBottom();
                }
            } catch (err) {
                console.error('Send failed:', err);
            }

            input.disabled = false;
            input.focus();
        }

        function makeOffer() {
            const amount = prompt('Enter your offer amount (₦):');
            if (!amount || isNaN(amount)) return;
            sendOfferViaApi(amount);
        }

        async function sendOfferViaApi(amount) {
            try {
                const token = getToken();
                const res = await fetch(`${API_BASE}/api/chat/rooms/${roomId}/offer`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ amount: parseFloat(amount) })
                });

                if (res.ok) {
                    const data = await res.json();
                    // Instant display
                    appendMessage(data.message);
                    lastMessageId = Math.max(lastMessageId, data.message.id);
                    scrollToBottom();
                } else {
                    const err = await res.json();
                    alert(err.msg || 'Offer failed');
                }
            } catch (err) {
                console.error('Offer failed:', err);
            }
        }

        async function respondOffer(offerId, action) {
            try {
                const token = getToken();
                const res = await fetch(`${API_BASE}/api/chat/rooms/${roomId}/offer/${offerId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ action })
                });

                const data = await res.json();
                if (res.ok) {
                    // Instant display
                    appendMessage(data.message);
                    lastMessageId = Math.max(lastMessageId, data.message.id);
                    scrollToBottom();
                    // Remove action buttons
                    const actions = document.getElementById(`offer-actions-${offerId}`);
                    if (actions) actions.style.display = 'none';
                } else {
                    alert(data.msg || 'Failed to respond');
                }
            } catch (err) {
                console.error('Response failed:', err);
            }
        }

        function counterOffer(offerId) {
            const amount = prompt('Enter your counter amount (₦):');
            if (!amount || isNaN(amount)) return;

            (async () => {
                try {
                    const token = getToken();
                    const res = await fetch(`${API_BASE}/api/chat/rooms/${roomId}/offer/${offerId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({ action: 'counter', amount: parseFloat(amount) })
                    });

                    const data = await res.json();
                    if (res.ok) {
                        appendMessage(data.message);
                        lastMessageId = Math.max(lastMessageId, data.message.id);
                        scrollToBottom();
                        const actions = document.getElementById(`offer-actions-${offerId}`);
                        if (actions) actions.style.display = 'none';
                    } else {
                        alert(data.msg || 'Counter failed');
                    }
                } catch (err) {
                    console.error('Counter failed:', err);
                }
            })();
        }

        window.addEventListener('beforeunload', () => {
            if (pollingInterval) clearInterval(pollingInterval);
        });

        init();
    </script>
</body>
</html>
