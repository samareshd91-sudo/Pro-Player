import streamlit.components.v1 as components
import os
import base64

def trigger_pro_alerts(coin, direction, entry):
    flash_color = "rgba(0, 255, 170, 0.3)" if direction == "BUY" else "rgba(255, 68, 68, 0.3)"
    beep_freq = 800 if direction == "BUY" else 400
    
    # 🎵 MP3 Load
    audio_html = ""
    has_mp3 = "false"
    if os.path.exists("alert.mp3"):
        has_mp3 = "true"
        with open("alert.mp3", "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()
        audio_html = f"""
        <audio id="alarm" style="display:none">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        """
    
    # 🧠 Core JavaScript Logic (Escaped brackets to prevent Python F-string crashes)
    js_code = f"""
    <script>
        let mainDoc = document;
        let mainWindow = window;
        
        try {{
            if (window.parent !== window) {{
                mainDoc = window.parent.document;
                mainWindow = window.parent;
            }}
        }} catch (e) {{
            console.log("Cross-origin iframe detected.");
        }}

        const sigKey = "{coin}_{direction}_{entry}";
        let allowAlert = true;

        try {{
            if (mainWindow.localStorage.getItem("lastSMCAlert") === sigKey) {{
                allowAlert = false;
            }} else {{
                mainWindow.localStorage.setItem("lastSMCAlert", sigKey);
            }}
        }} catch (e) {{
            allowAlert = true;
        }}

        if (allowAlert) {{
            // 🟢 1. Screen Flash
            try {{
                if (mainWindow.flashTimeout) {{
                    clearTimeout(mainWindow.flashTimeout);
                }}
                if (!mainWindow.originalBgColor) {{
                    mainWindow.originalBgColor = mainWindow.getComputedStyle(mainDoc.body).backgroundColor;
                }}
                
                mainDoc.body.style.transition = "background-color 0.3s ease";
                mainDoc.body.style.backgroundColor = "{flash_color}";
                
                mainWindow.flashTimeout = setTimeout(() => {{
                    mainDoc.body.style.backgroundColor = mainWindow.originalBgColor;
                    mainWindow.originalBgColor = null;
                }}, 2000);
            }} catch (e) {{ console.log("Flash error:", e); }}

            // 🟢 2. Tab Blink
            try {{
                if (!mainWindow.originalDocTitle) {{
                    mainWindow.originalDocTitle = mainDoc.title; 
                }}
                let originalTitle = mainWindow.originalDocTitle;
                
                if (mainWindow.blinkInterval) {{
                    clearInterval(mainWindow.blinkInterval);
                }}
                if (mainWindow.blinkTimeout) {{
                    clearTimeout(mainWindow.blinkTimeout);
                }}
                
                mainWindow.blinkInterval = setInterval(() => {{
                    mainDoc.title = mainDoc.title === originalTitle ? "⚡ {direction} SIGNAL ⚡" : originalTitle;
                }}, 700);

                mainWindow.blinkTimeout = setTimeout(() => {{
                    if (mainWindow.blinkInterval) {{
                        clearInterval(mainWindow.blinkInterval);
                        mainWindow.blinkInterval = null;
                    }}
                    mainDoc.title = originalTitle;
                }}, 30000);

                if (!mainWindow.focusHandlerInstalled) {{
                    mainWindow.focusHandlerInstalled = true;
                    
                    const stopBlinking = () => {{
                        const isFocused = typeof mainDoc.hasFocus === "function" && mainDoc.hasFocus();
                        if (mainDoc.visibilityState === "visible" || isFocused) {{
                            if (mainWindow.blinkInterval) {{
                                clearInterval(mainWindow.blinkInterval);
                                mainWindow.blinkInterval = null;
                            }}
                            if (mainWindow.blinkTimeout) {{
                                clearTimeout(mainWindow.blinkTimeout);
                                mainWindow.blinkTimeout = null;
                            }}
                            mainDoc.title = mainWindow.originalDocTitle;
                        }}
                    }};

                    mainDoc.addEventListener("visibilitychange", stopBlinking);
                    mainWindow.addEventListener("focus", stopBlinking);
                }}
            }} catch (e) {{ console.log("Blink error:", e); }}

            // 🟢 3. Audio System
            let hasMp3 = {has_mp3};
            if (hasMp3) {{
                try {{
                    let audio = document.getElementById("alarm");
                    if (audio) {{
                        audio.pause();
                        audio.currentTime = 0;
                        audio.loop = true;
                        audio.play().catch(err => console.log("Autoplay Blocked:", err));
                        
                        if (mainWindow.audioTimeout) {{
                            clearTimeout(mainWindow.audioTimeout);
                        }}
                        mainWindow.audioTimeout = setTimeout(() => {{
                            audio.pause();
                            audio.currentTime = 0;
                        }}, 5000);
                    }}
                }} catch (e) {{ console.log("MP3 Error:", e); }}
            }} else {{
                try {{
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const osc = ctx.createOscillator();
                    const gainNode = ctx.createGain();
                    osc.connect(gainNode);
                    gainNode.connect(ctx.destination);
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime({beep_freq}, ctx.currentTime);
                    gainNode.gain.setValueAtTime(0.5, ctx.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 3.0);
                    osc.start(ctx.currentTime);
                    osc.stop(ctx.currentTime + 3.0);
                    osc.onended = () => ctx.close();
                }} catch (e) {{ console.log("Beep Error:", e); }}
            }}

            // 🟢 4. Notification System
            const notifTitle = "⚡ {coin} {direction} SIGNAL";
            const notifBody = "Entry Triggered at {entry}";
            const notifIcon = "https://cdn-icons-png.flaticon.com/512/2952/2952373.png";

            try {{
                if ("Notification" in window) {{
                    if (Notification.permission === "granted") {{
                        new Notification(notifTitle, {{ body: notifBody, icon: notifIcon, requireInteraction: true }});
                    }} else if (Notification.permission === "default") {{
                        Notification.requestPermission().then(permission => {{
                            if (permission === "granted") {{
                                new Notification(notifTitle, {{ body: notifBody, icon: notifIcon, requireInteraction: true }});
                            }}
                        }});
                    }}
                }}
            }} catch (e) {{ console.log("Notification Error:", e); }}
        }}
    </script>
    """
    
    components.html(audio_html + js_code, height=1, width=1)
